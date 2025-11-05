# src/infrastructure/persistence/sqlalchemy/repositories/user_repository.py
"""
Implementación del repositorio de usuarios
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from domain.entities.user import User
from infrastructure.persistence.sqlalchemy.models.user_model import UserModel


class UserRepository(IUserRepository):
    """Implementación SQLAlchemy del repositorio de usuarios"""

    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> List[User]:
        """Obtiene todos los usuarios"""
        models = self.db.query(UserModel).all()
        return [self._to_entity(model) for model in models]

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por ID"""
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_username(self, username: str) -> Optional[User]:
        """Busca un usuario por username"""
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email"""
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un usuario con ese username"""
        return self.db.query(UserModel).filter(UserModel.username == username).count() > 0

    def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con ese email"""
        return self.db.query(UserModel).filter(UserModel.email == email).count() > 0

    def save(self, user: User) -> User:
        """Guarda un usuario"""
        model = self._to_model(user)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, user: User) -> User:
        """Actualiza un usuario"""
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if model:
            model.username = user.username
            model.email = user.email
            model.rol = user.rol
            model.password_hash = user.hashed_password
            model.nombre = user.nombre
            model.apellido = user.apellido
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        return user

    def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False

    def _to_entity(self, model: UserModel) -> User:
        """Convierte modelo ORM a entidad de dominio"""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            rol=model.rol.value if hasattr(model.rol, 'value') else str(model.rol),
            hashed_password=model.password_hash,  # ← Mapeado desde password_hash de BD
            nombre=model.nombre,
            apellido=model.apellido,
            created_at=model.created_at
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convierte entidad de dominio a modelo ORM"""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.hashed_password,  # ← Mapeado a password_hash de BD
            rol=entity.rol,
            nombre=entity.nombre,
            apellido=entity.apellido
        )
