# src/config.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Leer la URL de la base de datos desde la variable de entorno, o usar la local por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamesdroide@localhost:5432/eduforge")

# Crear el engine de SQLAlchemy para conectar con PostgreSQL
# Con configuraciones robustas para producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=3600,   # Recicla conexiones cada hora
    pool_size=5,         # Tamaño del pool de conexiones
    max_overflow=10,     # Conexiones extras permitidas
    echo=False,          # No imprimir queries SQL (cambiar a True para debug)
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Declarar la base para los modelos
Base = declarative_base()

# Verificar la conexión a la base de datos
def check_db_connection():
    try:
        # Establecer una conexión y ejecutar la consulta correctamente
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa!")
            print(f"   Database: {engine.url.database}")
            print(f"   Host: {engine.url.host}")
    except OperationalError as e:
        print(f"❌ Error al conectarse a la base de datos: {e}")

# Llamamos a esta función para verificar la conexión
check_db_connection()
