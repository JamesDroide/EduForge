# src/application/dto/user_dto.py
"""
DTOs para usuarios
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.entities.user import User


@dataclass
class UserDTO:
    """DTO para usuario"""
    id: int
    username: str
    email: str
    rol: str
    nombre: Optional[str]
    apellido: Optional[str]
    created_at: Optional[datetime]

    @classmethod
    def from_entity(cls, entity: User) -> 'UserDTO':
        """Crea un DTO desde una entidad"""
        return cls(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            rol=entity.rol,
            nombre=entity.nombre,
            apellido=entity.apellido,
            created_at=entity.created_at
        )

    def to_dict(self) -> dict:
        """Convierte el DTO a diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'rol': self.rol,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class UserCreateDTO:
    """DTO para crear usuario"""
    username: str
    email: str
    password: str
    rol: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None


@dataclass
class UserUpdateDTO:
    """DTO para actualizar usuario"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None

