from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import pyotp                                      
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return _pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return _pwd.verify(p, h)

def create_token(data: dict) -> str:
    data = data.copy()
    if "sub" in data:
        data["sub"] = str(data["sub"])  # -> Force 'sub' to be a string.
    data["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ---------- TOTP ----------
def new_totp_secret() -> str:
    return pyotp.random_base32()

def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)   # ±30 sec
