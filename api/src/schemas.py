from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# -------- auth --------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str
    totp_code: Optional[str] = None           

# -------- user & settings --------
class UserOut(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    display_name: Optional[str]

    class Config:
        orm_mode = True

class UserSettingsOut(BaseModel):
    enable_2fa: bool
    face_login_app: bool
    enable_in_app_alerts: bool
    enable_push_notifications: bool
    notify_new_device_login: bool

    class Config:
        orm_mode = True

# -------- doorbells / perms --------
class DoorbellOut(BaseModel):
    doorbell_id: int
    doorbell_name: str
    class Config:
        orm_mode = True

class PermCheckResponse(BaseModel):           
    permission: str
    granted: bool

class OverrideSet(BaseModel):                
    permission_name: str
    is_granted: bool
