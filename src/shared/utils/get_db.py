# src/shared/utils/get_db.py
"""
Utilidad para obtener sesión de base de datos (Dependency Injection)
"""
from sqlalchemy.orm import Session
from infrastructure.config.database import SessionLocal


def get_db():
    """
    Generador de sesión de base de datos para FastAPI
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

