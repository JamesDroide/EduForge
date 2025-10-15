"""
Script para crear usuario administrador por defecto
Este script se ejecuta una sola vez para crear el primer usuario admin
"""
import sys
import os

# Agregar el directorio src al path para las importaciones
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from sqlalchemy.orm import Session
from models.user import Usuario, RolEnum
from utils.security import get_password_hash
from config import SessionLocal, engine, Base

def create_admin_user():
    """Crea un usuario administrador por defecto si no existe"""

    # Crear las tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Verificar si ya existe un usuario admin
        admin_exists = db.query(Usuario).filter(
            Usuario.rol == RolEnum.ADMINISTRADOR
        ).first()

        if admin_exists:
            print("✅ Ya existe un usuario administrador")
            print(f"   Username: {admin_exists.username}")
            return

        # Crear usuario administrador por defecto
        admin_user = Usuario(
            email="admin@eduforge.com",
            username="admin",
            password_hash=get_password_hash("admin123"),  # Cambiar en producción
            rol=RolEnum.ADMINISTRADOR,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Usuario administrador creado exitosamente")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Password: admin123")
        print("   ⚠️  IMPORTANTE: Cambia la contraseña después del primer login")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuario administrador: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
