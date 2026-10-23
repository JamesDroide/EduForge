"""
Migración para hacer que user_id en upload_history sea nullable
y agregar ondelete='SET NULL' a la clave foránea
"""
import sys
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from sqlalchemy import text
from config import engine

def migrate():
    """Ejecutar la migración"""
    print("Iniciando migracion: Modificando columna user_id en upload_history...")

    try:
        with engine.connect() as connection:
            trans = connection.begin()

            try:
                print("Paso 1: Eliminando restriccion de clave foranea antigua...")
                connection.execute(text("""
                    ALTER TABLE upload_history 
                    DROP CONSTRAINT IF EXISTS upload_history_user_id_fkey;
                """))

                print("Paso 2: Modificando columna user_id para permitir NULL...")
                connection.execute(text("""
                    ALTER TABLE upload_history 
                    ALTER COLUMN user_id DROP NOT NULL;
                """))

                print("Paso 3: Agregando nueva restriccion de clave foranea con ON DELETE SET NULL...")
                connection.execute(text("""
                    ALTER TABLE upload_history 
                    ADD CONSTRAINT upload_history_user_id_fkey 
                    FOREIGN KEY (user_id) 
                    REFERENCES usuarios(id) 
                    ON DELETE SET NULL;
                """))

                trans.commit()
                print("Migracion completada exitosamente")
                print("  - user_id ahora permite valores NULL")
                print("  - Al eliminar un usuario, sus registros de historial se mantendran con user_id=NULL")

            except Exception as e:
                trans.rollback()
                print(f"Error durante la migracion: {e}")
                raise

    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()
