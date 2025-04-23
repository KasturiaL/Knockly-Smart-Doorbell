# SmartDoor API

A compact FastAPI service that runs directly on a Raspberry Pi.  
One `uvicorn` worker talks to the local MariaDB instance—no extra services
required.

---

## 1 · Start-up

```bash
cd api               # project root on the Pi
python3 -m venv venv && source venv/bin/activate
cd src
pip install -r requirements.txt

# one-time: create a signing key for JWTs
export JWT_SECRET=$(openssl rand -hex 32)

uvicorn main:app --host 0.0.0.0 --port 8000
```

Interactive docs will be at `http://<pi-ip>:8000/docs`.

---

## 2 · Core endpoints

| Verb + Path | Purpose |
|-------------|---------|
| **POST** `/auth/register` | Create account → JWT |
| **POST** `/auth/login` | Login → JWT (`totp_code` optional) |
| **POST** `/auth/2fa/setup` | Enable TOTP, returns QR + `otpauth://` URI |
| **POST** `/auth/2fa/disable` | Disable TOTP |
| **GET** `/users/me` | Profile |
| **GET** `/users/me/settings` | User toggle settings |
| **GET** `/doorbells` | Doorbells linked to the current user |
| **GET** `/doorbells/{id}/permissions` | List permissions with `granted` flag |
| **PATCH** `/doorbells/{id}/permissions/override` | Add/Remove one permission override |
| **GET** `/doorbells/{id}/faces` | *NEW* – list face profiles for the bell |
| **PATCH** `/faces/{face_id}/block?block=true\|false` | *NEW* – set `is_blocked` |

All routes except `/auth/*` expect `Authorization: Bearer <token>`.

---

## 3 · Permission logic

```
(role permissions)  ±  (user overrides)  →  effective set
```

* Role comes from `user_doorbell`.  
* Overrides live in `user_permissions_override`.  
* Helper in `crud.py` returns the resolved set, so a route can simply do:

```python
if "open_door" not in perms:
    raise HTTPException(403)
```

---

## 4 · Directory outline

```
main.py        HTTP routes & auth dependency
models.py      SQLAlchemy ORM mappings (face_profiles now links to doorbells)
crud.py        DB helpers (auth, perms, faces, overrides)
security.py    bcrypt, JWT, TOTP helpers
database.py    async connection pool
schemas.py     Pydantic request / response models
config.py      DB creds and JWT settings
requirements.txt
```

---

## 5 · Next things to consider

* Extend CRUD for `doorbell_logs`, sensor data, etc.  
* Put Caddy or Nginx in front if the API must be reachable from outside
  the LAN.  
* Add unit tests with `pytest` + FastAPI `TestClient`.  
* Consider database migrations with Alembic once the schema stabilises.

