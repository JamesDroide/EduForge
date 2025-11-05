# src/application/interfaces/upload_repository_interface.py
"""
Interface para el repositorio de uploads
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.upload import Upload


class IUploadRepository(ABC):
    """Interface del repositorio de uploads"""

    @abstractmethod
    def find_all(self) -> List[Upload]:
        """Obtiene todos los uploads"""
        pass

    @abstractmethod
    def find_by_id(self, upload_id: int) -> Optional[Upload]:
        """Busca un upload por ID"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[Upload]:
        """Busca uploads por ID de usuario"""
        pass

    @abstractmethod
    def find_recent(self, limit: int = 10) -> List[Upload]:
        """Obtiene los uploads más recientes"""
        pass

    @abstractmethod
    def save(self, upload: Upload) -> Upload:
        """Guarda un upload"""
        pass

    @abstractmethod
    def update(self, upload: Upload) -> Upload:
        """Actualiza un upload"""
        pass

    @abstractmethod
    def delete(self, upload_id: int) -> bool:
        """Elimina un upload"""
        pass
# src/domain/exceptions/domain_exceptions.py
"""
Excepciones de dominio personalizadas
"""

class DomainException(Exception):
    """Excepción base de dominio"""
    pass


class UserNotFoundException(DomainException):
    """Usuario no encontrado"""
    def __init__(self, user_id: int = None, username: str = None):
        if user_id:
            message = f"Usuario con ID {user_id} no encontrado"
        elif username:
            message = f"Usuario '{username}' no encontrado"
        else:
            message = "Usuario no encontrado"
        super().__init__(message)


class PredictionNotFoundException(DomainException):
    """Predicción no encontrada"""
    def __init__(self, prediction_id: int):
        super().__init__(f"Predicción con ID {prediction_id} no encontrada")


class UploadNotFoundException(DomainException):
    """Upload no encontrado"""
    def __init__(self, upload_id: int):
        super().__init__(f"Upload con ID {upload_id} no encontrado")


class InvalidCSVException(DomainException):
    """CSV inválido"""
    def __init__(self, message: str = "El archivo CSV no es válido"):
        super().__init__(message)


class InvalidCredentialsException(DomainException):
    """Credenciales inválidas"""
    def __init__(self):
        super().__init__("Credenciales inválidas")


class UserAlreadyExistsException(DomainException):
    """Usuario ya existe"""
    def __init__(self, username: str = None, email: str = None):
        if username:
            message = f"El usuario '{username}' ya existe"
        elif email:
            message = f"El email '{email}' ya está registrado"
        else:
            message = "El usuario ya existe"
        super().__init__(message)


class UnauthorizedException(DomainException):
    """No autorizado"""
    def __init__(self, message: str = "No tienes permisos para realizar esta acción"):
        super().__init__(message)

