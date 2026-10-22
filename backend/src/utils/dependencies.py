from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config import SessionLocal
from models.user import Usuario
from utils.security import decode_access_token
from schemas.auth_schemas import TokenData
from typing import Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Define el esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_db():
    """
    Dependency para obtener la sesión de base de datos
    Con manejo robusto de transacciones

    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en la sesión de BD: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario actual desde el token JWT

    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos

    Returns:
        Usuario: Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar el token
        payload = decode_access_token(token)
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username, rol=payload.get("rol"))
    except Exception:
        raise credentials_exception

    # Buscar el usuario en la base de datos
    user = db.query(Usuario).filter(Usuario.username == token_data.username).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Obtiene el usuario actual si hay token, sino retorna None
    Útil para endpoints que funcionan con o sin autenticación
    """
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")

        if username is None:
            return None

        user = db.query(Usuario).filter(Usuario.username == username).first()

        if user and user.is_active:
            return user
    except Exception:
        pass

    return None

async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verifica que el usuario actual esté activo

    Args:
        current_user: Usuario actual

    Returns:
        Usuario: Usuario activo

    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user

async def require_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Verifica que el usuario actual sea administrador

    Args:
        current_user: Usuario actual

    Returns:
        Usuario: Usuario administrador

    Raises:
        HTTPException: Si el usuario no es administrador
    """
    from models.user import RolEnum

    if current_user.rol != RolEnum.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Se requiere rol de administrador"
        )
    return current_user

async def require_docente_or_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Verifica que el usuario sea docente o administrador

    Args:
        current_user: Usuario actual

    Returns:
        Usuario: Usuario autorizado

    Raises:
        HTTPException: Si el usuario no tiene permisos
    """
    if current_user.rol not in ["administrador", "docente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes"
        )
    return current_user
