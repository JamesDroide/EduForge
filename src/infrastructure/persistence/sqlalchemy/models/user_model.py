# src/infrastructure/persistence/sqlalchemy/models/user_model.py
"""
Modelo ORM para usuarios
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from infrastructure.config.database import Base
import datetime
import enum


class RolEnum(str, enum.Enum):
    """Enum para roles de usuario"""
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"


class UserModel(Base):
    """Modelo ORM para usuarios"""
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    rol = Column(SQLEnum(RolEnum, name='rols', create_constraint=True), nullable=False)
    nombre = Column(String, nullable=True)
    apellido = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
