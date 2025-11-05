# src/application/use_cases/users/create_user_use_case.py
"""
Caso de uso: Crear usuario (admin)
"""
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from domain.entities.user import User
from domain.exceptions.domain_exceptions import UserAlreadyExistsException
from application.dto.user_dto import UserDTO
from shared.utils.security import hash_password


class CreateUserUseCase:
    """Caso de uso para crear usuario (por admin)"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, username: str, email: str, password: str, rol: str,
                nombre: str = None, apellido: str = None) -> UserDTO:
        """Ejecuta el caso de uso"""

        # Validar que no exista
        if self.repository.exists_by_username(username):
            raise UserAlreadyExistsException(username=username)

        if self.repository.exists_by_email(email):
            raise UserAlreadyExistsException(email=email)

        # Crear usuario
        user = User(
            id=None,
            username=username,
            email=email,
            rol=rol,
            hashed_password=hash_password(password),
            nombre=nombre,
            apellido=apellido
        )

        # Guardar
        saved_user = self.repository.save(user)

        return UserDTO.from_entity(saved_user)

