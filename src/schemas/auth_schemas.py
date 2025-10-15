from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RolEnum(str, Enum):
    """Enum para los roles de usuario"""
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"

class UserBase(BaseModel):
    """Schema base para usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    rol: RolEnum = RolEnum.DOCENTE

class UserCreate(UserBase):
    """Schema para crear un nuevo usuario"""
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str

class UserResponse(UserBase):
    """Schema para respuesta de usuario (sin password)"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema para el token de acceso"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Schema para datos del token"""
    username: Optional[str] = None
    rol: Optional[str] = None

class ChangePassword(BaseModel):
    """Schema para cambiar contraseña"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

