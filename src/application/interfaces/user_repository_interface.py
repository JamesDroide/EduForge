# src/application/interfaces/user_repository_interface.py
"""
Interface para el repositorio de usuarios
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User


class IUserRepository(ABC):
    """Interface del repositorio de usuarios"""

    @abstractmethod
    def find_all(self) -> List[User]:
        """Obtiene todos los usuarios"""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por ID"""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Busca un usuario por username"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email"""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Guarda un usuario"""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Actualiza un usuario"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un usuario con ese username"""
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con ese email"""
        pass

