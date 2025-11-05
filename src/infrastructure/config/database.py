# src/config.py
import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Leer la URL de la base de datos desde la variable de entorno, o usar la local por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamesdroide@localhost:5432/eduforge")

# Loggear info crítica de conexión (sin password)
if DATABASE_URL:
    # Ocultar password para logging seguro
    safe_url = DATABASE_URL.split('@')[0].split(':')[0] + ':****@' + DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    logger.info(f"🔗 DATABASE_URL configurada: {safe_url}")
else:
    logger.warning("⚠️ DATABASE_URL no configurada, usando default local")

# Detectar si estamos en Railway
IS_RAILWAY = 'rlwy.net' in DATABASE_URL or 'railway' in DATABASE_URL.lower()
if IS_RAILWAY:
    logger.info("🚂 Railway detectado - Aplicando configuraciones especiales")

# Crear el engine de SQLAlchemy para conectar con PostgreSQL
# Con configuraciones robustas para producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=300 if IS_RAILWAY else 3600,   # Recicla más rápido en Railway
    pool_size=3 if IS_RAILWAY else 5,         # Pool más pequeño en Railway
    max_overflow=5 if IS_RAILWAY else 10,     # Conexiones extras permitidas
    echo=False,          # No imprimir queries SQL (cambiar a True para debug)
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    },
    # CRÍTICO para Railway: Forzar commit inmediato
    isolation_level="AUTOCOMMIT" if IS_RAILWAY else "READ COMMITTED"
)

# Crear la sesión de base de datos
# expire_on_commit=False evita que los objetos expiren después del commit
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True if IS_RAILWAY else False,  # Autoflush en Railway
    bind=engine,
    expire_on_commit=False  # ← CRÍTICO: Mantiene objetos accesibles después del commit
)

# Event listener para Railway: Forzar commit después de cada flush
if IS_RAILWAY:
    @event.listens_for(SessionLocal, "after_flush")
    def receive_after_flush(session, flush_context):
        logger.debug("🔵 After flush - forzando persist en Railway")

# Declarar la base para los modelos
Base = declarative_base()

# Verificar la conexión a la base de datos
def check_db_connection():
    try:
        # Establecer una conexión y ejecutar la consulta correctamente
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Conexión a la base de datos exitosa!")
            logger.info(f"   Database: {engine.url.database}")
            logger.info(f"   Host: {engine.url.host}")
            logger.info(f"   Port: {engine.url.port}")

            # Verificar versión de PostgreSQL
            version = connection.execute(text("SELECT version()"))
            pg_version = version.scalar()
            logger.info(f"   PostgreSQL: {pg_version[:50]}...")

    except OperationalError as e:
        logger.error(f"❌ Error al conectarse a la base de datos: {e}")

# Llamamos a esta función para verificar la conexión
check_db_connection()
