from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from utils.dependencies import get_db, get_current_user, require_admin
from schemas.auth_schemas import (
    UserCreate, UserResponse, UserLogin, Token, ChangePassword
)
from services.auth_service import AuthService
from models.user import Usuario

router = APIRouter(tags=["Autenticación"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo admin puede crear usuarios
):
    """
    Registra un nuevo usuario (Solo administradores)

    Args:
        user_data: Datos del nuevo usuario
        db: Sesión de base de datos
        current_user: Usuario administrador actual

    Returns:
        UserResponse: Usuario creado
    """
    return AuthService.create_user(db, user_data)

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión y retorna un token de acceso

    Args:
        login_data: Credenciales de login
        db: Sesión de base de datos

    Returns:
        Token: Token de acceso y datos del usuario
    """
    result = AuthService.login_user(db, login_data)
    return result

@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint alternativo de login usando OAuth2PasswordRequestForm
    Útil para la documentación automática de FastAPI

    Args:
        form_data: Formulario con username y password
        db: Sesión de base de datos

    Returns:
        Token: Token de acceso y datos del usuario
    """
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    result = AuthService.login_user(db, login_data)
    return result

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actual

    Args:
        current_user: Usuario autenticado

    Returns:
        UserResponse: Datos del usuario actual
    """
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual

    Args:
        password_data: Contraseña antigua y nueva
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        dict: Mensaje de confirmación
    """
    AuthService.change_password(
        db,
        current_user,
        password_data.old_password,
        password_data.new_password
    )
    return {"message": "Contraseña actualizada correctamente"}

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Lista todos los usuarios (Solo administradores)

    Args:
        db: Sesión de base de datos
        current_user: Usuario administrador

    Returns:
        List[UserResponse]: Lista de usuarios
    """
    users = db.query(Usuario).all()
    return users

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Desactiva un usuario (Solo administradores)

    Args:
        user_id: ID del usuario a desactivar
        db: Sesión de base de datos
        current_user: Usuario administrador

    Returns:
        dict: Mensaje de confirmación
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivarte a ti mismo"
        )

    AuthService.deactivate_user(db, user_id)
    return {"message": "Usuario desactivado correctamente"}

@router.post("/logout")
async def logout(current_user: Usuario = Depends(get_current_user)):
    """
    Cierra sesión (en el frontend se debe eliminar el token)

    Args:
        current_user: Usuario autenticado

    Returns:
        dict: Mensaje de confirmación
    """
    return {"message": "Sesión cerrada correctamente"}

