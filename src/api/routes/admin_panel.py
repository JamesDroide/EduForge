"""
Rutas especiales para el panel de administración
Requiere un código de acceso adicional además de las credenciales
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from utils.dependencies import get_db
from models.user import Usuario
from schemas.auth_schemas import UserCreate, UserUpdate, UserResponse, PasswordChange
from utils.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel
from datetime import timedelta
import os

router = APIRouter(prefix="/admin", tags=["admin-panel"])

# Código de acceso especial para el panel de administración
# En producción, esto debería estar en una variable de entorno
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
    # Verificar el código de acceso especial
    if login_data.access_code != ADMIN_ACCESS_CODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de acceso inválido"
        )

    # Verificar las credenciales del usuario
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

    # Verificar que el usuario sea administrador
    if user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder al panel de administración"
        )

    # Crear token de acceso
    access_token = create_access_token(
        data={"sub": user.username, "rol": user.rol},
        expires_delta=timedelta(hours=12)  # Token más largo para el panel de admin
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def get_current_admin(token: str = Depends(get_db)) -> Usuario:
    """
    Dependency para verificar que el usuario actual sea administrador con token válido
    """
    # Esta función sería similar a get_current_user pero con verificación adicional
    # Por ahora, la implementaremos en los endpoints individuales
    pass


@router.get("/users", response_model=List[UserResponse])
async def get_all_users_admin(
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los usuarios desde el panel de administración
    EXCLUYE al usuario superadmin por seguridad
    """
    # Obtener el username del superadmin desde variables de entorno
    SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")

    # Filtrar usuarios excluyendo al superadmin
    users = db.query(Usuario).filter(
        Usuario.username != SUPERADMIN_USERNAME
    ).all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: int,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario desde el panel de administración
    """
    import logging
    import time
    from sqlalchemy import inspect, text
    logger = logging.getLogger(__name__)

    try:
        # VERIFICACIÓN: Asegurar que la tabla usuarios existe
        inspector = inspect(db.bind)
        if 'usuarios' not in inspector.get_table_names():
            logger.error("❌ CRÍTICO: La tabla 'usuarios' no existe en la base de datos")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de configuración: La tabla de usuarios no existe en la base de datos"
            )

        logger.info(f"🔵 Iniciando creación de usuario: {user_data.username}")
        logger.info(f"🔵 Conexión BD: {db.bind.url.database} en {db.bind.url.host}:{db.bind.url.port}")

        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
        if existing_user:
            logger.warning(f"⚠️ Usuario ya existe: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        # Verificar si el email ya existe
        existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_email:
            logger.warning(f"⚠️ Email ya existe: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )

        # Crear el nuevo usuario
        logger.info(f"🔵 Creando objeto Usuario para: {user_data.username}")
        hashed_password = get_password_hash(user_data.password)
        new_user = Usuario(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            rol=user_data.rol,
            is_active=user_data.is_active
        )

        logger.info(f"🔵 Agregando usuario a la sesión...")
        db.add(new_user)

        logger.info(f"🔵 Ejecutando flush...")
        db.flush()
        logger.info(f"✅ Flush exitoso - Usuario tiene ID: {new_user.id}")

        logger.info(f"🔵 Ejecutando commit...")
        db.commit()
        logger.info(f"✅ Commit exitoso")

        # CRÍTICO PARA RAILWAY: Forzar que la conexión persista el cambio
        logger.info(f"🔵 Forzando persist con execute...")
        db.execute(text("SELECT 1"))  # Forzar que la conexión confirme

        logger.info(f"⏳ Esperando propagación en Railway (200ms)...")
        time.sleep(0.2)  # Aumentar a 200ms

        # VERIFICACIÓN CRÍTICA 1: Usar SQL directo en la MISMA sesión
        logger.info(f"🔵 Verificación SQL directa en sesión actual...")
        result = db.execute(text(f"SELECT COUNT(*) FROM usuarios WHERE id = {new_user.id}"))
        count = result.scalar()
        logger.info(f"✅ SQL en sesión actual: {count} registro(s)")

        if count == 0:
            logger.error(f"❌ CRÍTICO: COUNT es 0 en la misma sesión después del commit!")
            # Intentar commit adicional
            db.commit()
            logger.info(f"🔵 Commit adicional ejecutado")
            time.sleep(0.1)
            result = db.execute(text(f"SELECT COUNT(*) FROM usuarios WHERE id = {new_user.id}"))
            count = result.scalar()
            logger.info(f"🔵 Verificación después de 2do commit: {count} registro(s)")

        # VERIFICACIÓN CRÍTICA 2: Usar una nueva sesión INDEPENDIENTE
        logger.info(f"🔵 Verificando persistencia con nueva sesión...")
        from config import SessionLocal, engine

        # Crear nueva sesión con el MISMO engine
        verify_db = SessionLocal()
        try:
            # Verificación con ORM
            verification = verify_db.query(Usuario).filter(Usuario.id == new_user.id).first()
            if not verification:
                logger.error(f"❌ ERROR CRÍTICO: Usuario con ID {new_user.id} no encontrado en nueva sesión!")

                # Verificar cuántos usuarios hay en total
                total = verify_db.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
                logger.error(f"   Total de usuarios en BD: {total}")

                # Listar últimos IDs
                last_ids = verify_db.execute(text("SELECT id, username FROM usuarios ORDER BY id DESC LIMIT 5")).fetchall()
                logger.error(f"   Últimos IDs en BD: {last_ids}")

                raise Exception("El usuario no se guardó correctamente en la base de datos")

            logger.info(f"✅ Usuario verificado en BD con ID: {verification.id}, Username: {verification.username}")

            # Verificación adicional con SQL directo en nueva sesión
            result2 = verify_db.execute(text(f"SELECT COUNT(*) FROM usuarios WHERE id = {new_user.id}"))
            count2 = result2.scalar()
            logger.info(f"✅ Verificación SQL en nueva sesión: {count2} registros encontrados")

            # Verificar que la BD es la correcta
            db_name = verify_db.execute(text("SELECT current_database()")).scalar()
            logger.info(f"✅ Base de datos actual: {db_name}")

        finally:
            verify_db.close()

        logger.info(f"🔵 Refrescando objeto original...")
        db.refresh(new_user)
        logger.info(f"✅ Refresh exitoso")

        logger.info(f"✅✅✅ USUARIO CREADO EXITOSAMENTE: {new_user.username} (ID: {new_user.id})")

        return new_user

    except HTTPException:
        # Re-lanzar excepciones HTTP
        logger.error(f"❌ HTTPException al crear usuario")
        db.rollback()
        raise
    except Exception as e:
        # Hacer rollback en caso de cualquier otro error
        logger.error(f"❌ ERROR CRÍTICO al crear usuario: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
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

        # Verificar que no sea el superadmin
        SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")
        if user.username == SUPERADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede modificar este usuario"
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


@router.post("/users/{user_id}/change-password")
async def change_user_password_admin(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db)
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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db)
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

        # Verificar que no sea el superadmin intentando eliminarse a sí mismo
        SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")
        if user.username == SUPERADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede eliminar el usuario superadmin del sistema. Este usuario es crítico para el funcionamiento del panel de administración."
            )

        # El superadmin puede eliminar cualquier otro usuario (incluyendo 'admin')
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
