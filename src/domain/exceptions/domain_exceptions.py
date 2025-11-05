# src/domain/exceptions/domain_exceptions.py
"""
Excepciones del dominio
"""


class DomainException(Exception):
    """Excepción base del dominio"""
    pass


class UserNotFoundException(DomainException):
    """Usuario no encontrado"""
    def __init__(self, user_id: int = None, username: str = None, email: str = None):
        if user_id:
            message = f"Usuario con ID {user_id} no encontrado"
        elif username:
            message = f"Usuario con username '{username}' no encontrado"
        elif email:
            message = f"Usuario con email '{email}' no encontrado"
        else:
            message = "Usuario no encontrado"
        super().__init__(message)


class UserAlreadyExistsException(DomainException):
    """Usuario ya existe"""
    def __init__(self, username: str = None, email: str = None):
        if username:
            message = f"Usuario con username '{username}' ya existe"
        elif email:
            message = f"Usuario con email '{email}' ya existe"
        else:
            message = "Usuario ya existe"
        super().__init__(message)


class InvalidCredentialsException(DomainException):
    """Credenciales inválidas"""
    def __init__(self):
        super().__init__("Credenciales incorrectas")


class InvalidCSVException(DomainException):
    """CSV inválido"""
    def __init__(self, message: str = "Archivo CSV inválido"):
        super().__init__(message)


class PredictionNotFoundException(DomainException):
    """Predicción no encontrada"""
    def __init__(self, prediction_id: int = None):
        if prediction_id:
            message = f"Predicción con ID {prediction_id} no encontrada"
        else:
            message = "Predicción no encontrada"
        super().__init__(message)


class UploadNotFoundException(DomainException):
    """Upload no encontrado"""
    def __init__(self, upload_id: int = None):
        if upload_id:
            message = f"Upload con ID {upload_id} no encontrado"
        else:
            message = "Upload no encontrado"
        super().__init__(message)


class UnauthorizedException(DomainException):
    """No autorizado"""
    def __init__(self, message: str = "No tiene permisos para realizar esta acción"):
        super().__init__(message)


class ValidationException(DomainException):
    """Error de validación"""
    def __init__(self, message: str):
        super().__init__(message)

