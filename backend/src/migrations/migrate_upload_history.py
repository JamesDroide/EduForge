"""
Script de migración para crear las tablas del historial de cargas
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from config import SessionLocal, Base, engine
from models.upload_history import UploadHistory, UploadPrediction
from models.user import Usuario

def migrate_upload_history_tables():
    """Crear las tablas de historial de cargas"""
    print("Iniciando migracion de tablas de historial...")

    try:
        Base.metadata.create_all(bind=engine, tables=[
            UploadHistory.__table__,
            UploadPrediction.__table__
        ])

        print("Tablas de historial creadas exitosamente:")
        print("  - upload_history")
        print("  - upload_predictions")

        db = SessionLocal()
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('upload_history', 'upload_predictions')
        """))

        tables = [row[0] for row in result]
        print(f"\nTablas verificadas: {tables}")

        db.close()

        return True

    except Exception as e:
        print(f"Error en la migracion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def add_user_name_fields():
    """Agregar campos nombre y apellido a la tabla usuarios si no existen"""
    print("\nAgregando campos nombre y apellido a usuarios...")

    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND column_name IN ('nombre', 'apellido')
        """))

        existing_columns = [row[0] for row in result]

        if 'nombre' not in existing_columns:
            db.execute(text("ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(100)"))
            print("Campo 'nombre' agregado")
        else:
            print("Campo 'nombre' ya existe")

        if 'apellido' not in existing_columns:
            db.execute(text("ALTER TABLE usuarios ADD COLUMN apellido VARCHAR(100)"))
            print("Campo 'apellido' agregado")
        else:
            print("Campo 'apellido' ya existe")

        db.commit()
        return True

    except Exception as e:
        print(f"Error agregando campos: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("MIGRACION: Sistema de Historial de Cargas CSV")

    success1 = add_user_name_fields()
    success2 = migrate_upload_history_tables()

    if success1 and success2:
        print("\nMIGRACION COMPLETADA EXITOSAMENTE")
        print("Ahora puedes:")
        print("1. Reiniciar el servidor backend")
        print("2. Subir un CSV y las cargas se guardaran en el historial")
        print("3. Acceder a /historial en el frontend para ver el historial")
    else:
        print("\nMIGRACION COMPLETADA CON ERRORES")
        print("Revisa los mensajes de error anteriores")
