# src/domain/entities/user.py
"""
Entidad de dominio: User
Representa un usuario del sistema
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Entidad de dominio para usuario"""
    
    id: Optional[int]
    username: str
    email: str
    rol: str
    hashed_password: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == "administrador"
    
    def is_teacher(self) -> bool:
        """Verifica si el usuario es docente"""
        return self.rol == "docente"
    
    def is_student(self) -> bool:
        """Verifica si el usuario es estudiante"""
        return self.rol == "estudiante"
    
    def can_manage_users(self) -> bool:
        """Verifica si puede gestionar usuarios"""
        return self.is_admin()
    
    def can_upload_data(self) -> bool:
        """Verifica si puede subir datos"""
        return self.is_admin() or self.is_teacher()
    
    def get_full_name(self) -> str:
        """Obtiene el nombre completo del usuario"""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.username

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "rol": self.rol,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
