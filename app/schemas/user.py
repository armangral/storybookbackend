from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr







class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: EmailStr
    # role: UserRole


class UserCreate(UserBase):
    password: str

class UserCreateWithAdmin(UserCreate):
    pass

class UserOut(UserBase):
    id: uuid.UUID
    is_super_admin: Optional[bool]

    class Config:
        orm_mode = True
