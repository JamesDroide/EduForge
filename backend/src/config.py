import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import logging

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamesdroide@localhost:5432/eduforge")

if DATABASE_URL:
    safe_url = DATABASE_URL.split('@')[0].split(':')[0] + ':****@' + DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    logger.info(f"DATABASE_URL configurada: {safe_url}")
else:
    logger.warning("DATABASE_URL no configurada, usando default local")

IS_RAILWAY = 'rlwy.net' in DATABASE_URL or 'railway' in DATABASE_URL.lower()
if IS_RAILWAY:
    logger.info("Railway detectado - Aplicando configuraciones especiales")

# Ajustes de pool e isolation_level específicos para evitar conexiones colgadas y transacciones sin confirmar en Railway
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300 if IS_RAILWAY else 3600,
    pool_size=3 if IS_RAILWAY else 5,
    max_overflow=5 if IS_RAILWAY else 10,
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    },
    isolation_level="AUTOCOMMIT" if IS_RAILWAY else "READ COMMITTED"
)

# expire_on_commit=False mantiene los atributos cargados en memoria tras cerrar o confirmar la sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True if IS_RAILWAY else False,
    bind=engine,
    expire_on_commit=False
)

if IS_RAILWAY:
    @event.listens_for(SessionLocal, "after_flush")
    def receive_after_flush(session, flush_context):
        logger.debug("After flush - forzando persist en Railway")

Base = declarative_base()

def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Conexion a la base de datos exitosa")
            logger.info(f"  Database: {engine.url.database}")
            logger.info(f"  Host: {engine.url.host}")
            logger.info(f"  Port: {engine.url.port}")

            version = connection.execute(text("SELECT version()"))
            pg_version = version.scalar()
            logger.info(f"  PostgreSQL: {pg_version[:50]}...")

    except OperationalError as e:
        logger.error(f"Error al conectarse a la base de datos: {e}")

check_db_connection()
