#!/bin/bash

echo "Iniciando aplicacion EduForge..."
echo "Working directory: $(pwd)"

cd src || exit 1

echo "Verificando conexion a la base de datos..."
python -c "from config import check_db_connection; check_db_connection()" || {
    echo "Error: No se pudo conectar a la base de datos"
    exit 1
}

echo "Ejecutando migraciones y creando tablas..."
python -c "
import sys
sys.path.insert(0, '.')
from config import Base, engine
from models.user import Usuario
from models.upload_history import UploadHistory, UploadPrediction
from models import ResultadoPrediccion, StudentData

print('Creando todas las tablas...')
Base.metadata.create_all(engine)

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Tablas en BD: {tables}')

if 'usuarios' in tables:
    print('Tabla usuarios confirmada')
else:
    print('ERROR: Tabla usuarios NO existe')
    sys.exit(1)
" || {
    echo "Error al crear tablas"
    exit 1
}

echo "Base de datos lista"
echo "Iniciando servidor FastAPI..."

exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
