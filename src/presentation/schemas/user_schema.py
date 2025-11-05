# src/presentation/schemas/user_schema.py
"""
Schemas de Pydantic para usuarios
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """Schema de respuesta para usuario"""
    id: int
    username: str
    email: str
    rol: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    created_at: Optional[str] = None


class UserCreateRequest(BaseModel):
    """Schema de petición para crear usuario"""
    username: str
    email: EmailStr
    password: str
    rol: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Schema de petición para actualizar usuario"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
# src/presentation/api/routes/auth_routes.py
"""
Rutas de la API para autenticación (Clean Architecture)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.utils.get_db import get_db
from application.use_cases.auth.login_use_case import LoginUseCase
from application.use_cases.auth.register_use_case import RegisterUseCase
from domain.exceptions.domain_exceptions import InvalidCredentialsException, UserAlreadyExistsException
from presentation.schemas.auth_schema import LoginRequest, RegisterRequest, AuthResponse

router = APIRouter(prefix="/auth-v2", tags=["Autenticación v2 (Clean)"])


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login de usuario usando Clean Architecture
    """
    try:
        use_case = LoginUseCase(db)
        result = use_case.execute(request.username, request.password)
        return result
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registro de usuario usando Clean Architecture
    """
    try:
        use_case = RegisterUseCase(db)
        result = use_case.execute(
            username=request.username,
            email=request.email,
            password=request.password,
            rol=request.rol,
            nombre=request.nombre,
            apellido=request.apellido
        )
        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "user": result
        }
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en registro: {str(e)}")

