"""
Script para crear usuario administrador por defecto
Este script se ejecuta una sola vez para crear el primer usuario admin
IMPORTANTE: Las credenciales se leen desde variables de entorno (.env)
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from models.user import Usuario, RolEnum
from utils.security import get_password_hash
from config import SessionLocal, engine, Base

def create_admin_user():
    """Crea un usuario administrador por defecto si no existe"""

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
    DEFAULT_ADMIN_EMAIL = "admin@eduforge.com"

    ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
    ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_exists = db.query(Usuario).filter(
            Usuario.username == ADMIN_USERNAME
        ).first()

        if admin_exists:
            print("Ya existe un usuario administrador")
            print(f"  Username: {admin_exists.username}")
            return

        admin_user = Usuario(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            rol=RolEnum.ADMINISTRADOR,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Usuario administrador creado exitosamente")
        print(f"  Email: {admin_user.email}")
        print(f"  Username: {admin_user.username}")
        print("  IMPORTANTE: Cambia la contrasena despues del primer login")
        print("  NOTA: Este usuario es diferente del superadmin del panel de gestion")

    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario administrador: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
