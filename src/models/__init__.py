from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from config import Base
import datetime

# IMPORTANTE: Importar TODOS los modelos ANTES de usar Base.metadata
# Esto asegura que SQLAlchemy conozca todas las tablas
from models.user import Usuario, RolEnum
from models.upload_history import UploadHistory, UploadPrediction

class ResultadoPrediccion(Base):
    __tablename__ = 'resultados_prediccion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, nullable=False)
    nombre = Column(String, nullable=True)
    nota = Column(Float, nullable=False)
    nota_final = Column(Float, nullable=False)
    conducta = Column(String, nullable=True)
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=True)
    tiempo_prediccion = Column(Float, nullable=False)
    resultado_prediccion = Column(String, nullable=True)
    riesgo_desercion = Column(String, nullable=True)
    probabilidad_desercion = Column(Float, nullable=True)
    fecha = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class StudentData(Base):
    __tablename__ = 'student_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, nullable=False)
    nombre = Column(String, nullable=False)
    nota_final = Column(Float, nullable=False)
    conducta = Column(String, nullable=False)
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Exportar todos los modelos para que estén disponibles
__all__ = ['ResultadoPrediccion', 'StudentData', 'Usuario', 'RolEnum', 'UploadHistory', 'UploadPrediction']
