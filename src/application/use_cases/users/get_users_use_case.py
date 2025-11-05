# src/application/use_cases/users/get_users_use_case.py
"""
Caso de uso: Obtener todos los usuarios
"""
from typing import List
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from application.dto.user_dto import UserDTO


class GetUsersUseCase:
    """Caso de uso para obtener todos los usuarios"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self) -> List[UserDTO]:
        """Ejecuta el caso de uso"""
        users = self.repository.find_all()
        return [UserDTO.from_entity(user) for user in users]


class GetUserByIdUseCase:
    """Caso de uso para obtener un usuario por ID"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, user_id: int) -> UserDTO:
        """Ejecuta el caso de uso"""
        from domain.exceptions.domain_exceptions import UserNotFoundException

        user = self.repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=user_id)

        return UserDTO.from_entity(user)

