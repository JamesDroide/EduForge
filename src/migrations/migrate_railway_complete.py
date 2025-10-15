"""
Migración completa para Railway - Agrega todas las columnas necesarias
Este script debe ejecutarse DESPUÉS del despliegue inicial en Railway
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config import engine
from sqlalchemy import text

def migrate_all():
    """
    Agrega todas las columnas necesarias a las tablas student_data y resultados_prediccion
    """
    with engine.connect() as conn:
        print("🔄 Iniciando migración completa...")

        # =====================================================================
        # MIGRACIÓN 1: Tabla student_data
        # =====================================================================
        print("\n📋 Verificando tabla student_data...")

        student_data_columns = {
            'id_estudiante': 'INTEGER NOT NULL DEFAULT 0',
            'nota_final': 'FLOAT NOT NULL DEFAULT 0',
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
                print(f"  ⚠️  Error con columna {column_name}: {e}")
                conn.rollback()

        # =====================================================================
        # MIGRACIÓN 2: Tabla resultados_prediccion
        # =====================================================================
        print("\n📋 Verificando tabla resultados_prediccion...")

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
                print(f"  ⚠️  Error con columna {column_name}: {e}")
                conn.rollback()

        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETA FINALIZADA")
        print("="*60)
        print("\n📊 Estructura final de las tablas:")

        # Mostrar estructura de student_data
        print("\n📋 Tabla: student_data")
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='student_data'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]}")

        # Mostrar estructura de resultados_prediccion
        print("\n📋 Tabla: resultados_prediccion")
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='resultados_prediccion'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]}")

if __name__ == "__main__":
    print("="*60)
    print("🚀 MIGRACIÓN COMPLETA PARA RAILWAY")
    print("="*60)
    migrate_all()
    print("\n⚠️  IMPORTANTE: Reinicia la aplicación en Railway para que tome los cambios")
