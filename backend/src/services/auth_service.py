from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime
from models.user import Usuario
from schemas.auth_schemas import UserCreate, UserLogin
from utils.security import get_password_hash, verify_password, create_access_token
from typing import Optional

class AuthService:
    """Servicio para manejar la lógica de autenticación"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Usuario:
        """
        Crea un nuevo usuario en la base de datos

        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a crear

        Returns:
            Usuario: Usuario creado

        Raises:
            HTTPException: Si el usuario ya existe
        """
        try:
            existing_user = db.query(Usuario).filter(
                (Usuario.username == user_data.username) |
                (Usuario.email == user_data.email)
            ).first()

            if existing_user:
                if existing_user.username == user_data.username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El nombre de usuario ya está registrado"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El email ya está registrado"
                    )

            hashed_password = get_password_hash(user_data.password)
            db_user = Usuario(
                email=user_data.email,
                username=user_data.username,
                password_hash=hashed_password,
                nombre=getattr(user_data, 'nombre', None),
                apellido=getattr(user_data, 'apellido', None),
                rol=user_data.rol,
                is_active=getattr(user_data, 'is_active', True)
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return db_user

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear el usuario. El username o email ya existe"
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario verificando sus credenciales

        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña

        Returns:
            Usuario: Usuario autenticado o None si las credenciales son inválidas
        """
        user = db.query(Usuario).filter(Usuario.username == username).first()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> dict:
        """
        Inicia sesión de un usuario y genera un token de acceso

        Args:
            db: Sesión de base de datos
            login_data: Datos de login

        Returns:
            dict: Token de acceso y datos del usuario

        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        user = AuthService.authenticate_user(db, login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user.last_login = datetime.utcnow()
        db.commit()

        access_token = create_access_token(
            data={"sub": user.username, "rol": user.rol.value}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su nombre de usuario

        Args:
            db: Sesión de base de datos
            username: Nombre de usuario

        Returns:
            Usuario: Usuario encontrado o None
        """
        return db.query(Usuario).filter(Usuario.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario

        Returns:
            Usuario: Usuario encontrado o None
        """
        return db.query(Usuario).filter(Usuario.id == user_id).first()

    @staticmethod
    def change_password(db: Session, user: Usuario, old_password: str, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario

        Args:
            db: Sesión de base de datos
            user: Usuario
            old_password: Contraseña antigua
            new_password: Contraseña nueva

        Returns:
            bool: True si se cambió correctamente

        Raises:
            HTTPException: Si la contraseña antigua es incorrecta
        """
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña antigua es incorrecta"
            )

        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Desactiva un usuario

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario

        Returns:
            bool: True si se desactivó correctamente

        Raises:
            HTTPException: Si el usuario no existe
        """
        user = AuthService.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()

        return True
