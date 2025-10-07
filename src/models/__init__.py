from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from config import Base
import datetime

class ResultadoPrediccion(Base):
    __tablename__ = 'resultados_prediccion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, nullable=False)
    nota = Column(Float, nullable=False)
    conducta = Column(Float, nullable=False)
    asistencia = Column(Float, nullable=False)
    tiempo_prediccion = Column(Float, nullable=False)
    resultado_prediccion = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)

class StudentData(Base):
    __tablename__ = 'student_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    estudiante_id = Column(Integer, nullable=False)
    nombre = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=False)
    conducta = Column(String, nullable=True)
