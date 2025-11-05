# src/shared/utils/security.py
"""
Utilidades de seguridad para autenticación
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
# src/application/use_cases/auth/login_use_case.py
"""
Caso de uso: Login de usuario
"""
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from domain.exceptions.domain_exceptions import InvalidCredentialsException
from shared.utils.security import verify_password, create_access_token


class LoginUseCase:
    """Caso de uso para login de usuario"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, username: str, password: str) -> dict:
        """
        Ejecuta el login

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Dict con token y datos del usuario
        """
        # 1. Buscar usuario
        user = self.repository.find_by_username(username)

        if not user:
            raise InvalidCredentialsException()

        # 2. Verificar contraseña
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        # 3. Generar token
        token = create_access_token({"sub": user.username})

        # 4. Retornar respuesta
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "nombre": user.nombre,
                "apellido": user.apellido
            }
        }

