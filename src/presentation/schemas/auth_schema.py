# src/presentation/schemas/auth_schema.py
"""
Schemas de Pydantic para autenticación
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema de petición para login"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Schema de petición para registro"""
    username: str
    email: EmailStr
    password: str
    rol: str = "estudiante"
    nombre: Optional[str] = None
    apellido: Optional[str] = None


class AuthResponse(BaseModel):
    """Schema de respuesta para autenticación"""
    access_token: str
    token_type: str
    user: dict


class UserInfo(BaseModel):
    """Schema de información de usuario"""
    id: int
    username: str
    email: str
    rol: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None

