"""
Rutas para la gestión de usuarios (CRUD completo)
Solo accesible por administradores
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from utils.dependencies import get_db, get_current_user
from models.user import Usuario
from schemas.auth_schemas import UserCreate, UserUpdate, UserResponse, PasswordChange
from utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los usuarios
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta función"
        )

    users = db.query(Usuario).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un usuario por ID
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta función"
        )

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear usuarios"
        )

    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        # Verificar si el email ya existe
        existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )

        # Crear el nuevo usuario
        hashed_password = get_password_hash(user_data.password)
        new_user = Usuario(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            rol=user_data.rol,
            is_active=user_data.is_active
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario existente
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar usuarios"
        )

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verificar si el nuevo username ya está en uso (si se cambió)
        if user_data.username and user_data.username != user.username:
            existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
            user.username = user_data.username

        # Verificar si el nuevo email ya está en uso (si se cambió)
        if user_data.email and user_data.email != user.email:
            existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está en uso"
                )
            user.email = user_data.email

        # Actualizar otros campos
        if user_data.rol is not None:
            user.rol = user_data.rol
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        db.commit()
        db.refresh(user)

        return user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.post("/{user_id}/change-password")
async def change_user_password(
    user_id: int,
    password_data: PasswordChange,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar la contraseña de un usuario
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar contraseñas"
        )

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Actualizar la contraseña
        user.password_hash = get_password_hash(password_data.new_password)
        db.commit()

        return {"message": "Contraseña actualizada exitosamente"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un usuario
    Solo para administradores
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar usuarios"
        )

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # No permitir que el administrador se elimine a sí mismo
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminarte a ti mismo"
            )

        db.delete(user)
        db.commit()

        return None

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}"
        )
