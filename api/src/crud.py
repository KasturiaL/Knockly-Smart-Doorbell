from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload                       # NEW
from typing import Optional, List, Set
import models, security

# ---------- user helpers ----------
async def _user_query():
    """Reusable SELECT that eagerly loads the settings relationship."""
    return select(models.User).options(selectinload(models.User.settings))

async def get_user_by_username(db: AsyncSession, username: str):
    stmt = (await _user_query()).where(models.User.username == username)
    res = await db.execute(stmt)
    return res.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = (await _user_query()).where(models.User.email == email)
    res = await db.execute(stmt)
    return res.scalars().first()

async def create_user(db: AsyncSession, *, username, email, password, display_name):
    user = models.User(
        username=username,
        email=email,
        password_hash=security.hash_password(password),
        display_name=display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # insert default settings row
    db.add(models.UserSettings(user_id=user.user_id))
    await db.commit()
    return user

async def authenticate(db: AsyncSession, identifier: str, password: str):
    # single query for either username OR email, with settings pre‑loaded
    stmt = (await _user_query()).where(
        (models.User.username == identifier) | (models.User.email == identifier)
    )
    user = (await db.execute(stmt)).scalars().first()
    if user and security.verify_password(password, user.password_hash):
        return user
    return None

# ---------- doorbell helpers ----------
async def list_user_doorbells(db: AsyncSession, user_id: int) -> List[models.Doorbell]:
    q = (
        select(models.Doorbell)
        .join(models.User.doorbells)
        .where(models.User.user_id == user_id)
    )
    res = await db.execute(q)
    return res.scalars().all()

# ---------- permission maths ----------
async def _role_permission_ids(db: AsyncSession, role_id: int) -> Set[int]:
    q = select(models.roles_permissions).where(
        models.roles_permissions.c.role_id == role_id
    )
    res = await db.execute(q)
    return {row.permission_id for row in res.fetchall()}

async def effective_permissions(
    db: AsyncSession, *, user_id: int, doorbell_id: int
) -> Set[str]:
    # 1) role attached in user_doorbell
    q = select(models.user_doorbell).where(
        (models.user_doorbell.c.user_id == user_id)
        & (models.user_doorbell.c.doorbell_id == doorbell_id)
    )
    row = (await db.execute(q)).first()
    if not row:
        return set()
    role_id = row.role_id

    # 2) permissions from role
    ids = await _role_permission_ids(db, role_id)

    # 3) apply overrides
    ovr_q = select(models.UserPermOverride).where(
        models.UserPermOverride.user_id == user_id
    )
    for o in (await db.execute(ovr_q)).scalars():
        if o.is_granted:
            ids.add(o.permission_id)
        else:
            ids.discard(o.permission_id)

    # 4) translate IDs ➜ names
    if not ids:
        return set()
    names_q = select(models.Permission.permission_name).where(
        models.Permission.permission_id.in_(ids)
    )
    res = await db.execute(names_q)
    return {n for (n,) in res.all()}

async def set_override(
    db: AsyncSession, *, user_id: int, perm_name: str, is_granted: bool
):
    perm_row = (
        await db.execute(
            select(models.Permission).where(
                models.Permission.permission_name == perm_name
            )
        )
    ).scalar_one_or_none()
    if not perm_row:
        return False

    override = await db.get(
        models.UserPermOverride, (user_id, perm_row.permission_id)
    )
    if override:
        override.is_granted = is_granted
    else:
        override = models.UserPermOverride(
            user_id=user_id,
            permission_id=perm_row.permission_id,
            is_granted=is_granted,
        )
        db.add(override)
    await db.commit()
    return True

# ---------- face profile helpers (NEW) ----------
async def list_faces(db: AsyncSession, *, doorbell_id: int) -> List[models.FaceProfile]:
    stmt = select(models.FaceProfile).where(models.FaceProfile.doorbell_id == doorbell_id)
    res = await db.execute(stmt)
    return res.scalars().all()

async def add_face(db: AsyncSession, *, doorbell_id: int,
                   face_data: bytes, name: str | None):
    fp = models.FaceProfile(
        doorbell_id=doorbell_id,
        face_data=face_data,
        face_profile_name=name,
    )
    db.add(fp)
    await db.commit()
    await db.refresh(fp)
    return fp

async def set_face_blocked(db: AsyncSession, *, face_id: int, blocked: bool):
    fp = await db.get(models.FaceProfile, face_id)
    if not fp:
        return None
    fp.is_blocked = blocked
    await db.commit()
    return fp

