# src/infrastructure/persistence/sqlalchemy/repositories/upload_repository.py
"""
Implementación del repositorio de uploads usando SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from application.interfaces.upload_repository_interface import IUploadRepository
from domain.entities.upload import Upload
from models.upload_history import UploadHistory as UploadModel


class UploadRepository(IUploadRepository):
    """Implementación del repositorio de uploads"""

    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> List[Upload]:
        """Obtiene todos los uploads"""
        models = self.db.query(UploadModel).order_by(desc(UploadModel.upload_date)).all()
        return [self._to_entity(model) for model in models]

    def find_by_id(self, upload_id: int) -> Optional[Upload]:
        """Busca un upload por ID"""
        model = self.db.query(UploadModel).filter(UploadModel.id == upload_id).first()
        return self._to_entity(model) if model else None

    def find_by_user_id(self, user_id: int) -> List[Upload]:
        """Busca uploads por ID de usuario"""
        models = self.db.query(UploadModel).filter(
            UploadModel.user_id == user_id
        ).order_by(desc(UploadModel.upload_date)).all()
        return [self._to_entity(model) for model in models]

    def find_recent(self, limit: int = 10) -> List[Upload]:
        """Obtiene los uploads más recientes"""
        models = self.db.query(UploadModel).order_by(
            desc(UploadModel.upload_date)
        ).limit(limit).all()
        return [self._to_entity(model) for model in models]

    def save(self, upload: Upload) -> Upload:
        """Guarda un nuevo upload"""
        model = self._to_model(upload)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, upload: Upload) -> Upload:
        """Actualiza un upload existente"""
        model = self.db.query(UploadModel).filter(UploadModel.id == upload.id).first()
        if not model:
            raise ValueError(f"Upload con ID {upload.id} no encontrado")

        # Actualizar campos
        model.total_students = upload.total_students
        model.processed_students = upload.processed_students
        model.failed_students = upload.failed_students
        model.high_risk = upload.high_risk
        model.medium_risk = upload.medium_risk
        model.low_risk = upload.low_risk
        model.processing_time = upload.processing_time
        model.status = upload.status
        model.error_message = upload.error_message

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, upload_id: int) -> bool:
        """Elimina un upload"""
        model = self.db.query(UploadModel).filter(UploadModel.id == upload_id).first()
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: UploadModel) -> Upload:
        """Convierte un modelo ORM a entidad de dominio"""
        return Upload(
            id=model.id,
            user_id=model.user_id,
            filename=model.filename,
            original_filename=model.original_filename,
            file_path=model.file_path,
            upload_date=model.upload_date,
            total_students=model.total_students,
            processed_students=model.processed_students,
            failed_students=model.failed_students,
            high_risk=model.high_risk,
            medium_risk=model.medium_risk,
            low_risk=model.low_risk,
            processing_time=model.processing_time,
            status=model.status,
            error_message=model.error_message
        )

    def _to_model(self, entity: Upload) -> UploadModel:
        """Convierte una entidad de dominio a modelo ORM"""
        return UploadModel(
            id=entity.id,
            user_id=entity.user_id,
            filename=entity.filename,
            original_filename=entity.original_filename,
            file_path=entity.file_path,
            upload_date=entity.upload_date,
            total_students=entity.total_students,
            processed_students=entity.processed_students,
            failed_students=entity.failed_students,
            high_risk=entity.high_risk,
            medium_risk=entity.medium_risk,
            low_risk=entity.low_risk,
            processing_time=entity.processing_time,
            status=entity.status,
            error_message=entity.error_message
        )
# src/infrastructure/persistence/sqlalchemy/repositories/user_repository.py
"""
Implementación del repositorio de usuarios usando SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from application.interfaces.user_repository_interface import IUserRepository
from domain.entities.user import User
from infrastructure.persistence.sqlalchemy.models.user_model import UserModel


class UserRepository(IUserRepository):
    """Implementación del repositorio de usuarios"""

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

    def save(self, user: User) -> User:
        """Guarda un nuevo usuario"""
        model = self._to_model(user)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, user: User) -> User:
        """Actualiza un usuario existente"""
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError(f"Usuario con ID {user.id} no encontrado")

        # Actualizar campos
        model.username = user.username
        model.email = user.email
        model.rol = user.rol
        model.hashed_password = user.hashed_password
        model.nombre = user.nombre
        model.apellido = user.apellido

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un usuario con ese username"""
        return self.db.query(UserModel).filter(UserModel.username == username).first() is not None

    def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con ese email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first() is not None

    def _to_entity(self, model: UserModel) -> User:
        """Convierte un modelo ORM a entidad de dominio"""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            rol=model.rol.value if hasattr(model.rol, 'value') else model.rol,
            hashed_password=model.hashed_password,
            nombre=model.nombre,
            apellido=model.apellido,
            created_at=model.created_at
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convierte una entidad de dominio a modelo ORM"""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            rol=entity.rol,
            hashed_password=entity.hashed_password,
            nombre=entity.nombre,
            apellido=entity.apellido
        )

