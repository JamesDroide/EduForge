# src/application/use_cases/auth/register_use_case.py
"""
Caso de uso: Registro de usuario
"""
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository
from domain.entities.user import User
from domain.exceptions.domain_exceptions import UserAlreadyExistsException
from shared.utils.security import hash_password


class RegisterUseCase:
    """Caso de uso para registro de usuario"""

    def __init__(self, db: Session):
        self.repository: IUserRepository = UserRepository(db)

    def execute(self, username: str, email: str, password: str, rol: str = "estudiante",
                nombre: str = None, apellido: str = None) -> dict:
        """
        Ejecuta el registro

        Args:
            username: Nombre de usuario
            email: Email del usuario
            password: Contraseña en texto plano
            rol: Rol del usuario (estudiante, docente, administrador)
            nombre: Nombre del usuario (opcional)
            apellido: Apellido del usuario (opcional)

        Returns:
            Dict con datos del usuario creado
        """
        # 1. Validar que no exista el usuario
        if self.repository.exists_by_username(username):
            raise UserAlreadyExistsException(username=username)

        if self.repository.exists_by_email(email):
            raise UserAlreadyExistsException(email=email)

        # 2. Crear entidad de usuario
        user = User(
            id=None,
            username=username,
            email=email,
            rol=rol,
            hashed_password=hash_password(password),
            nombre=nombre,
            apellido=apellido
        )

        # 3. Guardar en repositorio
        saved_user = self.repository.save(user)

        # 4. Retornar respuesta
        return {
            "id": saved_user.id,
            "username": saved_user.username,
            "email": saved_user.email,
            "rol": saved_user.rol,
            "nombre": saved_user.nombre,
            "apellido": saved_user.apellido
        }

