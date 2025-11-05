# src/infrastructure/persistence/sqlalchemy/models/prediction_model.py
"""
Modelo ORM para predicciones (ResultadoPrediccion)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from infrastructure.config.database import Base
import datetime


class PredictionModel(Base):
    """Modelo ORM para predicciones de deserción"""
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

