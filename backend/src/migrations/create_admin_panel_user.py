"""
Script para crear/actualizar el usuario especifico del panel de administracion
Este usuario es INDEPENDIENTE del usuario 'admin' del sistema
IMPORTANTE: Las credenciales se leen desde variables de entorno (.env)
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from models.user import Usuario, RolEnum
from utils.security import get_password_hash, verify_password
from config import SessionLocal, engine, Base

def create_or_update_admin_panel_user():
    """
    Crea o actualiza el usuario especifico para el panel de administracion
    Las credenciales se leen desde variables de entorno por seguridad
    """
    SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")
    SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "james232")
    SUPERADMIN_EMAIL = os.getenv("SUPERADMIN_EMAIL", "administrador@eduforge.com")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Evitar colision de email con otro usuario existente (ej. admin@eduforge.com del usuario admin)
        email_collision = db.query(Usuario).filter(
            Usuario.email == SUPERADMIN_EMAIL,
            Usuario.username != SUPERADMIN_USERNAME
        ).first()
        if email_collision:
            fallback_email = f"{SUPERADMIN_USERNAME}@eduforge.com"
            print(f"Email '{SUPERADMIN_EMAIL}' ya pertenece a '{email_collision.username}'. Usando '{fallback_email}' para '{SUPERADMIN_USERNAME}'.")
            SUPERADMIN_EMAIL = fallback_email

        admin_panel_user = db.query(Usuario).filter(
            Usuario.username == SUPERADMIN_USERNAME
        ).first()

        if admin_panel_user:
            print(f"Usuario '{SUPERADMIN_USERNAME}' encontrado - Actualizando credenciales...")

            if verify_password(SUPERADMIN_PASSWORD, admin_panel_user.password_hash):
                print("La contrasena ya es correcta")
            else:
                print("Actualizando contrasena")
                admin_panel_user.password_hash = get_password_hash(SUPERADMIN_PASSWORD)

            admin_panel_user.rol = RolEnum.ADMINISTRADOR
            admin_panel_user.is_active = True
            admin_panel_user.email = SUPERADMIN_EMAIL

            db.commit()
            db.refresh(admin_panel_user)

            print("Usuario del panel de administracion actualizado")
        else:
            print(f"Creando usuario '{SUPERADMIN_USERNAME}' para el panel de gestion...")

            admin_panel_user = Usuario(
                email=SUPERADMIN_EMAIL,
                username=SUPERADMIN_USERNAME,
                password_hash=get_password_hash(SUPERADMIN_PASSWORD),
                rol=RolEnum.ADMINISTRADOR,
                is_active=True
            )

            db.add(admin_panel_user)
            db.commit()
            db.refresh(admin_panel_user)

            print("Usuario del panel de administracion creado exitosamente")

        print("\nCONFIGURACION DEL PANEL DE ADMINISTRACION")
        print(f"  Username: {SUPERADMIN_USERNAME}")
        print(f"  Email:    {SUPERADMIN_EMAIL}")
        print(f"  ID:       {admin_panel_user.id}")
        print(f"  Rol:      {admin_panel_user.rol}")

    except Exception as e:
        db.rollback()
        print(f"Error al crear/actualizar usuario del panel: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_or_update_admin_panel_user()
