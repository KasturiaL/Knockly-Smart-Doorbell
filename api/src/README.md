A minimal FastAPI back‑end that runs on a Raspberry Pi.  One `uvicorn` worker talks to a local MariaDB; nothing else is required.

---

## 1 . Start‑up

```bash
cd api            # project root on the Pi
python3 -m venv venv && source venv/bin/activate
cd src
pip install -r requirements.txt

# generate the JWT signing key once
export JWT_SECRET=$(openssl rand -hex 32)

uvicorn main:app --host 0.0.0.0 --port 8000
```

Swagger docs are at `http://<pi-ip>:8000/docs`.

---

## 2 . Core Endpoints

| Verb & Path | Result |
|-------------|--------|
| **POST** `/auth/register` | Create account → JWT |
| **POST** `/auth/login` | Login → JWT (`totp_code` optional) |
| **POST** `/auth/2fa/setup` | Enable TOTP, returns QR + `otpauth://` URI |
| **POST** `/auth/2fa/disable` | Disable TOTP |
| **GET** `/users/me` | Profile |
| **GET** `/users/me/settings` | User toggle settings |
| **GET** `/doorbells` | Doorbells linked to token user |
| **GET** `/doorbells/{id}/permissions` | List of permissions with `granted` flag |
| **PATCH** `/doorbells/{id}/permissions/override` | Add/Remove one permission override |

All endpoints except `/auth/*` require `Authorization: Bearer <token>`.

---

## 3 . Permission Logic

```
(role permissions)  ±  (user overrides)  →  effective set
```

Role comes from `user_doorbell`; overrides live in `user_permissions_override`.  Helper in `crud.py` returns the final set so routes can do:

```python
if "open_door" not in perms:
    raise HTTPException(403)
```

---

## 4 . Directory Outline

```
main.py        routes & auth dependency
models.py      SQLAlchemy ORM mappings
crud.py        DB helpers (auth, perms, overrides)
security.py    bcrypt, JWT, TOTP helpers
database.py    async connection pool
schemas.py     Pydantic request/response models
config.py      DB creds and JWT settings
requirements.txt
```

---

## 5 . Things we might do next:

* Add CRUD routes for `face_profiles`, `doorbell_logs`, etc.
* Put Caddy or Nginx in front if the service is exposed outside the LAN.
* Consider unit tests with `pytest` + FastAPI `TestClient`.



