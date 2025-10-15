"""
Script de migración para crear las tablas del historial de cargas
"""
import sys
import os

# Agregar el directorio src al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from config import DATABASE_URL, SessionLocal
from models.upload_history import UploadHistory, UploadPrediction
from models.user import Usuario
from config import Base, engine

def migrate_upload_history_tables():
    """Crear las tablas de historial de cargas"""
    print("🔄 Iniciando migración de tablas de historial...")

    try:
        # Crear las tablas
        Base.metadata.create_all(bind=engine, tables=[
            UploadHistory.__table__,
            UploadPrediction.__table__
        ])

        print("✅ Tablas de historial creadas exitosamente:")
        print("   - upload_history")
        print("   - upload_predictions")

        # Verificar que las tablas existen
        db = SessionLocal()
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('upload_history', 'upload_predictions')
        """))

        tables = [row[0] for row in result]
        print(f"\n✅ Tablas verificadas: {tables}")

        db.close()

        return True

    except Exception as e:
        print(f"❌ Error en la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def add_user_name_fields():
    """Agregar campos nombre y apellido a la tabla usuarios si no existen"""
    print("\n🔄 Agregando campos nombre y apellido a usuarios...")

    db = SessionLocal()
    try:
        # Verificar si las columnas ya existen
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND column_name IN ('nombre', 'apellido')
        """))

        existing_columns = [row[0] for row in result]

        if 'nombre' not in existing_columns:
            db.execute(text("ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(100)"))
            print("✅ Campo 'nombre' agregado")
        else:
            print("ℹ️  Campo 'nombre' ya existe")

        if 'apellido' not in existing_columns:
            db.execute(text("ALTER TABLE usuarios ADD COLUMN apellido VARCHAR(100)"))
            print("✅ Campo 'apellido' agregado")
        else:
            print("ℹ️  Campo 'apellido' ya existe")

        db.commit()
        return True

    except Exception as e:
        print(f"❌ Error agregando campos: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Sistema de Historial de Cargas CSV")
    print("=" * 60)

    # Ejecutar migraciones
    success1 = add_user_name_fields()
    success2 = migrate_upload_history_tables()

    if success1 and success2:
        print("\n" + "=" * 60)
        print("✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("\nAhora puedes:")
        print("1. Reiniciar el servidor backend")
        print("2. Subir un CSV y las cargas se guardarán en el historial")
        print("3. Acceder a /historial en el frontend para ver el historial")
    else:
        print("\n" + "=" * 60)
        print("⚠️  MIGRACIÓN COMPLETADA CON ERRORES")
        print("=" * 60)
        print("Revisa los mensajes de error anteriores")
