from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from config import Base
import datetime

class UploadHistory(Base):
    """Historial de archivos CSV cargados"""
    __tablename__ = 'upload_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)  # Ahora permite NULL

    # Estadísticas del archivo
    total_students = Column(Integer, default=0)
    processed_students = Column(Integer, default=0)
    failed_students = Column(Integer, default=0)

    # Estadísticas de riesgo
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    low_risk_count = Column(Integer, default=0)
    high_risk_percentage = Column(Float, default=0.0)
    medium_risk_percentage = Column(Float, default=0.0)
    low_risk_percentage = Column(Float, default=0.0)

    # Estado del procesamiento
    status = Column(String(50), default='processing')  # processing, success, error, partial
    error_message = Column(Text, nullable=True)

    # Notas y observaciones
    notes = Column(Text, nullable=True)

    # Tiempo de procesamiento
    processing_time = Column(Float, nullable=True)  # en segundos

    # Relaciones
    user = relationship("Usuario", back_populates="upload_history")
    predictions = relationship("UploadPrediction", back_populates="upload_history", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'user_full_name': f"{self.user.nombre} {self.user.apellido}" if self.user else None,
            'total_students': self.total_students,
            'processed_students': self.processed_students,
            'failed_students': self.failed_students,
            'high_risk_count': self.high_risk_count,
            'medium_risk_count': self.medium_risk_count,
            'low_risk_count': self.low_risk_count,
            'high_risk_percentage': round(self.high_risk_percentage, 2),
            'medium_risk_percentage': round(self.medium_risk_percentage, 2),
            'low_risk_percentage': round(self.low_risk_percentage, 2),
            'status': self.status,
            'error_message': self.error_message,
            'notes': self.notes,
            'processing_time': round(self.processing_time, 2) if self.processing_time else None
        }


class UploadPrediction(Base):
    """Predicciones asociadas a cada carga de CSV"""
    __tablename__ = 'upload_predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_history_id = Column(Integer, ForeignKey('upload_history.id'), nullable=False)

    # Datos del estudiante
    estudiante_id = Column(Integer, nullable=False)
    nombre = Column(String(255), nullable=True)

    # Datos de entrada
    nota_final = Column(Float, nullable=False)
    conducta = Column(String(50), nullable=True)
    asistencia = Column(Float, nullable=False)
    inasistencia = Column(Float, nullable=True)

    # Resultados de predicción
    resultado_prediccion = Column(String(50), nullable=False)
    riesgo_desercion = Column(String(20), nullable=True)
    probabilidad_desercion = Column(Float, nullable=True)

    # Factores de riesgo identificados
    risk_factors = Column(Text, nullable=True)  # JSON string con factores

    # Tiempo de predicción
    tiempo_prediccion = Column(Float, nullable=False)
    fecha_prediccion = Column(DateTime, default=datetime.datetime.utcnow)

    # Relación
    upload_history = relationship("UploadHistory", back_populates="predictions")

    def to_dict(self):
        return {
            'id': self.id,
            'upload_history_id': self.upload_history_id,
            'estudiante_id': self.estudiante_id,
            'nombre': self.nombre,
            'nota_final': self.nota_final,
            'conducta': self.conducta,
            'asistencia': self.asistencia,
            'inasistencia': self.inasistencia,
            'resultado_prediccion': self.resultado_prediccion,
            'riesgo_desercion': self.riesgo_desercion,
            'probabilidad_desercion': round(self.probabilidad_desercion, 4) if self.probabilidad_desercion else None,
            'risk_factors': self.risk_factors,
            'tiempo_prediccion': round(self.tiempo_prediccion, 4),
            'fecha_prediccion': self.fecha_prediccion.isoformat() if self.fecha_prediccion else None
        }
