from sqlalchemy import Column, Integer, String, Float, DateTime
from config import Base
import datetime

# Importar el modelo de Usuario
from models.user import Usuario

# Importar los modelos de historial de cargas
from models.upload_history import UploadHistory, UploadPrediction

class ResultadoPrediccion(Base):
    __tablename__ = 'resultados_prediccion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, nullable=False)
    nombre = Column(String, nullable=True)  # Nuevo campo
    nota = Column(Float, nullable=False)  # Campo original para compatibilidad
    nota_final = Column(Float, nullable=False)  # Campo adicional
    conducta = Column(String, nullable=True)  # Cambiado de Float a String
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=True)  # Nuevo campo
    tiempo_prediccion = Column(Float, nullable=False)
    resultado_prediccion = Column(String, nullable=False)
    riesgo_desercion = Column(String, nullable=True)  # Nuevo campo (Alto, Medio, Bajo)
    probabilidad_desercion = Column(Float, nullable=True)  # Nuevo campo
    fecha = Column(DateTime, default=datetime.datetime.utcnow)

class StudentData(Base):
    __tablename__ = 'student_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, nullable=False)  # Cambiado de estudiante_id a id_estudiante
    nombre = Column(String, nullable=False)
    nota_final = Column(Float, nullable=False)  # Agregado
    conducta = Column(String, nullable=True)
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Agregado
