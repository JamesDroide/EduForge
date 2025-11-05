# src/application/use_cases/auth/login_use_case.py
"""
Caso de uso: Login de usuario
"""
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from domain.exceptions.domain_exceptions import UserNotFoundException
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
            raise UserNotFoundException(username=username)

        # 2. Verificar contraseña
        if not verify_password(password, user.hashed_password):
            raise UserNotFoundException(username=username)

        # 3. Crear token
        access_token = create_access_token(data={"sub": user.username})

        # 4. Retornar resultado
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }

