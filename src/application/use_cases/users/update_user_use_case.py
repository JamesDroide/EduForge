# src/application/use_cases/users/update_user_use_case.py
"""
Caso de uso: Actualizar usuario
"""
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from domain.exceptions.domain_exceptions import UserNotFoundException
from application.dto.user_dto import UserDTO
from shared.utils.security import hash_password


class UpdateUserUseCase:
    """Caso de uso para actualizar usuario"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, user_id: int, username: str = None, email: str = None,
                password: str = None, rol: str = None, nombre: str = None,
                apellido: str = None) -> UserDTO:
        """Ejecuta el caso de uso"""

        # Buscar usuario
        user = self.repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=user_id)

        # Actualizar campos
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.hashed_password = hash_password(password)
        if rol:
            user.rol = rol
        if nombre is not None:
            user.nombre = nombre
        if apellido is not None:
            user.apellido = apellido

        # Guardar cambios
        updated_user = self.repository.update(user)

        return UserDTO.from_entity(updated_user)


class DeleteUserUseCase:
    """Caso de uso para eliminar usuario"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, user_id: int) -> bool:
        """Ejecuta el caso de uso"""
        success = self.repository.delete(user_id)
        if not success:
            raise UserNotFoundException(user_id=user_id)

        return True

