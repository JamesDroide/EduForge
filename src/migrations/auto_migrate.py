"""
Migración automática de base de datos
Se ejecuta automáticamente al iniciar la aplicación
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from sqlalchemy import inspect
from config import Base, engine
from models import ResultadoPrediccion, StudentData

def run_migrations():
    """
    Ejecuta las migraciones automáticas de la base de datos.
    Crea las tablas si no existen, o las actualiza si faltan columnas.
    """
    try:
        print("🔄 Verificando estructura de base de datos...")

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Verificar tabla resultados_prediccion
        if 'resultados_prediccion' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('resultados_prediccion')]
            required_columns = ['nota', 'nota_final', 'nombre', 'inasistencia', 'riesgo_desercion', 'probabilidad_desercion']
            missing = [col for col in required_columns if col not in columns]

            if missing:
                print(f"⚠️  Columnas faltantes detectadas: {missing}")
                print("🔧 Recreando tabla resultados_prediccion...")
                Base.metadata.drop_all(engine, tables=[ResultadoPrediccion.__table__])
                Base.metadata.create_all(engine, tables=[ResultadoPrediccion.__table__])
                print("✅ Tabla resultados_prediccion actualizada")
            else:
                print("✅ Tabla resultados_prediccion está actualizada")
        else:
            print("📝 Creando tabla resultados_prediccion...")
            Base.metadata.create_all(engine, tables=[ResultadoPrediccion.__table__])
            print("✅ Tabla resultados_prediccion creada")

        # Verificar tabla student_data
        if 'student_data' not in existing_tables:
            print("📝 Creando tabla student_data...")
            Base.metadata.create_all(engine, tables=[StudentData.__table__])
            print("✅ Tabla student_data creada")
        else:
            print("✅ Tabla student_data está actualizada")

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

