"""
Script para crear/actualizar el usuario específico del panel de administración
Este usuario es INDEPENDIENTE del usuario 'admin' del sistema
IMPORTANTE: Las credenciales se leen desde variables de entorno (.env)
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio src al path para las importaciones
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from sqlalchemy.orm import Session
from models.user import Usuario, RolEnum
from utils.security import get_password_hash, verify_password
from config import SessionLocal, engine, Base

def create_or_update_admin_panel_user():
    """
    Crea o actualiza el usuario específico para el panel de administración
    Las credenciales se leen desde variables de entorno por seguridad
    """

    # Leer credenciales desde variables de entorno
    SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME")
    SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD")
    SUPERADMIN_EMAIL = os.getenv("SUPERADMIN_EMAIL")

    # Validar que las variables de entorno estén configuradas
    if not all([SUPERADMIN_USERNAME, SUPERADMIN_PASSWORD, SUPERADMIN_EMAIL]):
        print("❌ ERROR: Variables de entorno no configuradas")
        print("   Por favor configura en el archivo .env:")
        print("   - SUPERADMIN_USERNAME")
        print("   - SUPERADMIN_PASSWORD")
        print("   - SUPERADMIN_EMAIL")
        sys.exit(1)

    # Crear las tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Buscar si existe el usuario superadmin
        admin_panel_user = db.query(Usuario).filter(
            Usuario.username == SUPERADMIN_USERNAME
        ).first()

        if admin_panel_user:
            print(f"👤 Usuario '{SUPERADMIN_USERNAME}' encontrado - Actualizando credenciales...")

            # Verificar si la contraseña actual es correcta
            if verify_password(SUPERADMIN_PASSWORD, admin_panel_user.password_hash):
                print("✅ La contraseña ya es correcta")
            else:
                print("🔄 Actualizando contraseña")
                admin_panel_user.password_hash = get_password_hash(SUPERADMIN_PASSWORD)

            # Asegurar que tiene rol de administrador
            admin_panel_user.rol = RolEnum.ADMINISTRADOR
            admin_panel_user.is_active = True
            admin_panel_user.email = SUPERADMIN_EMAIL

            db.commit()
            db.refresh(admin_panel_user)

            print("✅ Usuario del panel de administración actualizado")
        else:
            print(f"➕ Creando usuario '{SUPERADMIN_USERNAME}' para el panel de gestión...")

            # Crear el usuario específico del panel de administración
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

            print("✅ Usuario del panel de administración creado exitosamente")

        print("\n" + "="*60)
        print("📋 CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN")
        print("="*60)
        print(f"   Username:       {SUPERADMIN_USERNAME}")
        print(f"   Email:          {SUPERADMIN_EMAIL}")
        print(f"   ID:             {admin_panel_user.id}")
        print(f"   Rol:            {admin_panel_user.rol}")
        print("="*60)
        print("\n⚠️  IMPORTANTE:")
        print("   - Las credenciales se gestionan mediante variables de entorno")
        print("   - Este usuario es INDEPENDIENTE del usuario 'admin' del sistema")
        print("   - NUNCA compartas las credenciales del superadmin")
        print("   - El código de acceso también está en las variables de entorno")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear/actualizar usuario del panel: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_or_update_admin_panel_user()
