"""
Migración automática de base de datos
Se ejecuta automáticamente al iniciar la aplicación
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from sqlalchemy import inspect, text
from config import Base, engine
from models import ResultadoPrediccion, StudentData

def run_migrations():
    """
    Ejecuta las migraciones automáticas de la base de datos.
    Crea las tablas si no existen, o agrega columnas faltantes.
    """
    try:
        print("🔄 Verificando estructura de base de datos...")

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # =====================================================================
        # MIGRACIÓN 1: Tabla student_data
        # =====================================================================
        if 'student_data' not in existing_tables:
            print("📝 Creando tabla student_data...")
            Base.metadata.create_all(engine, tables=[StudentData.__table__])
            print("✅ Tabla student_data creada")
        else:
            print("✅ Tabla student_data existe")
            # Agregar columnas faltantes
            with engine.connect() as conn:
                student_data_columns = {
                    'id_estudiante': 'INTEGER NOT NULL DEFAULT 0',
                    'nota_final': 'FLOAT NOT NULL DEFAULT 0',
                    'fecha': 'DATE DEFAULT CURRENT_DATE',  # Agregar columna fecha
                    'created_at': 'TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP',
                }

                for column_name, column_type in student_data_columns.items():
                    try:
                        result = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='student_data' AND column_name='{column_name}'
                        """))

                        if result.fetchone() is None:
                            print(f"  🔄 Agregando columna {column_name} a student_data...")
                            conn.execute(text(f"""
                                ALTER TABLE student_data 
                                ADD COLUMN {column_name} {column_type}
                            """))
                            conn.commit()
                            print(f"  ✅ Columna {column_name} agregada")
                        else:
                            print(f"  ✅ Columna {column_name} ya existe")
                    except Exception as e:
                        print(f"  ⚠️  Error al agregar columna {column_name}: {e}")
                        conn.rollback()

        # =====================================================================
        # MIGRACIÓN 2: Tabla resultados_prediccion
        # =====================================================================
        if 'resultados_prediccion' not in existing_tables:
            print("📝 Creando tabla resultados_prediccion...")
            Base.metadata.create_all(engine, tables=[ResultadoPrediccion.__table__])
            print("✅ Tabla resultados_prediccion creada")
        else:
            print("✅ Tabla resultados_prediccion existe")
            # Agregar columnas faltantes
            with engine.connect() as conn:
                resultados_columns = {
                    'resultado_prediccion': 'VARCHAR(50)',
                    'fecha': 'DATE',
                    'created_at': 'TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP',
                }

                for column_name, column_type in resultados_columns.items():
                    try:
                        result = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='resultados_prediccion' AND column_name='{column_name}'
                        """))

                        if result.fetchone() is None:
                            print(f"  🔄 Agregando columna {column_name} a resultados_prediccion...")
                            conn.execute(text(f"""
                                ALTER TABLE resultados_prediccion 
                                ADD COLUMN {column_name} {column_type}
                            """))
                            conn.commit()
                            print(f"  ✅ Columna {column_name} agregada")
                        else:
                            print(f"  ✅ Columna {column_name} ya existe")
                    except Exception as e:
                        print(f"  ⚠️  Error al agregar columna {column_name}: {e}")
                        conn.rollback()

        print("✅ Migración completada exitosamente\n")
        return True

    except Exception as e:
        print(f"❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
"""
Paquete de migraciones automáticas para Eduforge
"""
