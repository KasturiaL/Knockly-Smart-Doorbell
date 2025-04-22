from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Set
import models, security

# ---------- user helpers ----------
async def get_user_by_username(db: AsyncSession, username: str):
    res = await db.execute(select(models.User).where(models.User.username == username))
    return res.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    res = await db.execute(select(models.User).where(models.User.email == email))
    return res.scalars().first()

async def create_user(db: AsyncSession, *, username, email, password, display_name):
    user = models.User(username=username,
                       email=email,
                       password_hash=security.hash_password(password),
                       display_name=display_name)
    db.add(user)
    await db.commit(); await db.refresh(user)
    db.add(models.UserSettings(user_id=user.user_id))  # default toggles
    await db.commit()
    return user

async def authenticate(db: AsyncSession, identifier: str, password: str):
    user = await get_user_by_username(db, identifier) or await get_user_by_email(db, identifier)
    if user and security.verify_password(password, user.password_hash):
        return user
    return None

# ---------- doorbell helpers ----------
async def list_user_doorbells(db: AsyncSession, user_id: int) -> List[models.Doorbell]:
    q = (select(models.Doorbell)
         .join(models.User.doorbells)
         .where(models.User.user_id == user_id))
    res = await db.execute(q)
    return res.scalars().all()

# ---------- permission maths ----------
async def _role_permission_ids(db: AsyncSession, role_id: int) -> Set[int]:
    q = select(models.roles_permissions).where(models.roles_permissions.c.role_id == role_id)
    res = await db.execute(q)
    return {row.permission_id for row in res.fetchall()}

async def effective_permissions(db: AsyncSession, *, user_id: int, doorbell_id: int) -> Set[str]:
    # 1) fetch role attached in user_doorbell
    q = select(models.user_doorbell).where(
        (models.user_doorbell.c.user_id == user_id) &
        (models.user_doorbell.c.doorbell_id == doorbell_id)
    )
    row = (await db.execute(q)).first()
    if not row: return set()
    role_id = row.role_id

    # 2) role‑granted IDs
    ids = await _role_permission_ids(db, role_id)

    # 3) apply overrides
    ovr_q = select(models.UserPermOverride).where(
        (models.UserPermOverride.user_id == user_id)
    )
    for o in (await db.execute(ovr_q)).scalars():
        if o.is_granted:
            ids.add(o.permission_id)
        else:
            ids.discard(o.permission_id)

    # 4) map to readable names
    if not ids:
        return set()
    names_q = select(models.Permission.permission_name).where(models.Permission.permission_id.in_(ids))
    res = await db.execute(names_q)
    return {n for (n,) in res.all()}

async def set_override(db: AsyncSession, *, user_id: int, perm_name: str, is_granted: bool):
    perm_row = (await db.execute(select(models.Permission)
                                 .where(models.Permission.permission_name == perm_name))).scalar_one_or_none()
    if not perm_row:
        return False
    override = await db.get(models.UserPermOverride, (user_id, perm_row.permission_id))
    if override:
        override.is_granted = is_granted
    else:
        override = models.UserPermOverride(user_id=user_id,
                                           permission_id=perm_row.permission_id,
                                           is_granted=is_granted)
        db.add(override)
    await db.commit()
    return True
