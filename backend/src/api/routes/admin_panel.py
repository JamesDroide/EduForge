"""
Rutas especiales para el panel de administración
Requiere un código de acceso adicional además de las credenciales
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from utils.dependencies import get_db, require_admin
from models.user import Usuario
from schemas.auth_schemas import UserCreate, UserUpdate, UserResponse, PasswordChange
from utils.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel
from datetime import timedelta
import os

router = APIRouter(prefix="/admin", tags=["admin-panel"])

ADMIN_ACCESS_CODE = os.getenv("ADMIN_ACCESS_CODE", "EDUFORGE2025")

class AdminLoginRequest(BaseModel):
    username: str
    password: str
    access_code: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login especial para el panel de administración
    Requiere username, password Y código de acceso especial
    """
    if login_data.access_code != ADMIN_ACCESS_CODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de acceso inválido"
        )

    user = db.query(Usuario).filter(Usuario.username == login_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    if user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al panel de administración"
        )

    access_token = create_access_token(
        data={"sub": user.username, "rol": user.rol.value if hasattr(user.rol, 'value') else user.rol},
        expires_delta=timedelta(hours=12)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/users", response_model=List[UserResponse])
async def get_all_users_admin(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener lista de todos los usuarios desde el panel de administración
    EXCLUYE al usuario superadmin por seguridad
    """
    SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")

    users = db.query(Usuario).filter(
        Usuario.username != SUPERADMIN_USERNAME
    ).all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener un usuario por ID desde el panel de administración
    """
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Crear un nuevo usuario desde el panel de administración
    """
    import logging
    import time
    from sqlalchemy import inspect, text
    logger = logging.getLogger(__name__)

    try:
        inspector = inspect(db.bind)
        if 'usuarios' not in inspector.get_table_names():
            logger.error("CRITICO: La tabla 'usuarios' no existe en la base de datos")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de configuración: La tabla de usuarios no existe en la base de datos"
            )

        logger.info(f"Iniciando creacion de usuario: {user_data.username}")
        logger.info(f"Conexion BD: {db.bind.url.database} en {db.bind.url.host}:{db.bind.url.port}")

        existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
        if existing_user:
            logger.warning(f"Usuario ya existe: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_email:
            logger.warning(f"Email ya existe: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = Usuario(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            rol=user_data.rol,
            is_active=user_data.is_active
        )

        db.add(new_user)
        db.flush()
        db.commit()

        # En Railway con pooler, forzar sincronización de conexión antes de verificar en otra sesión
        db.execute(text("SELECT 1"))
        time.sleep(0.2)

        result = db.execute(text("SELECT COUNT(*) FROM usuarios WHERE id = :id"), {"id": new_user.id})
        count = result.scalar()

        if count == 0:
            logger.error("CRITICO: COUNT es 0 en la misma sesion despues del commit")
            db.commit()
            time.sleep(0.1)
            result = db.execute(text("SELECT COUNT(*) FROM usuarios WHERE id = :id"), {"id": new_user.id})
            count = result.scalar()

        from config import SessionLocal

        verify_db = SessionLocal()
        try:
            verification = verify_db.query(Usuario).filter(Usuario.id == new_user.id).first()
            if not verification:
                logger.error(f"ERROR CRITICO: Usuario con ID {new_user.id} no encontrado en nueva sesion")
                total = verify_db.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
                logger.error(f"  Total de usuarios en BD: {total}")
                last_ids = verify_db.execute(text("SELECT id, username FROM usuarios ORDER BY id DESC LIMIT 5")).fetchall()
                logger.error(f"  Ultimos IDs en BD: {last_ids}")
                raise Exception("El usuario no se guardó correctamente en la base de datos")

            logger.info(f"Usuario verificado en BD con ID: {verification.id}, Username: {verification.username}")
        finally:
            verify_db.close()

        db.refresh(new_user)
        logger.info(f"USUARIO CREADO EXITOSAMENTE: {new_user.username} (ID: {new_user.id})")

        return new_user

    except HTTPException:
        logger.error("HTTPException al crear usuario")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"ERROR CRITICO al crear usuario: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Actualizar un usuario existente desde el panel de administración
    NO permite modificar al usuario superadmin
    """
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")
        if user.username == SUPERADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede modificar este usuario"
            )

        if user_data.username and user_data.username != user.username:
            existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya está en uso"
                )
            user.username = user_data.username

        if user_data.email and user_data.email != user.email:
            existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está en uso"
                )
            user.email = user_data.email

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


@router.post("/users/{user_id}/change-password")
async def change_user_password_admin(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Cambiar la contraseña de un usuario desde el panel de administración
    """
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Eliminar un usuario desde el panel de administración
    El superadmin puede eliminar otros usuarios, pero no puede eliminarse a sí mismo
    """
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")
        if user.username == SUPERADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede eliminar el usuario superadmin del sistema. Este usuario es crítico para el funcionamiento del panel de administración."
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
