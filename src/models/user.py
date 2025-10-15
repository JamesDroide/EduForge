from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config import Base
import enum

class RolEnum(str, enum.Enum):
    """Enum para los roles de usuario"""
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"

class Usuario(Base):
    """Modelo de Usuario para autenticación"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    rol = Column(Enum(RolEnum), default=RolEnum.DOCENTE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    upload_history = relationship("UploadHistory", back_populates="user")

    def __repr__(self):
        return f"<Usuario(id={self.id}, username={self.username}, rol={self.rol})>"
