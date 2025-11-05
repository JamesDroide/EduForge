# src/presentation/schemas/prediction_schema.py
"""
Schemas de Pydantic para validación de predicciones
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PredictionResponse(BaseModel):
    """Schema de respuesta para predicción"""
    id: Optional[int]
    id_estudiante: int
    nombre: str
    nota_final: float
    conducta: str
    asistencia: float
    inasistencia: float
    tiempo_prediccion: float
    resultado_prediccion: str
    riesgo_desercion: str
    probabilidad_desercion: float
    fecha: Optional[str]
    risk_factors: Optional[List[str]] = None


class PredictRequest(BaseModel):
    """Schema de petición para realizar predicción"""
    filename: str
    upload_id: Optional[int] = None


class PredictionStatsResponse(BaseModel):
    """Schema de respuesta para estadísticas"""
    total_students: int
    high_risk: int
    medium_risk: int
    low_risk: int
    high_risk_percentage: float
    average_attendance: float
    average_grade: float
# src/application/use_cases/predictions/get_predictions_use_case.py
"""
Caso de uso: Obtener todas las predicciones
"""
from typing import List
from sqlalchemy.orm import Session

from application.interfaces.prediction_repository_interface import IPredictionRepository
from application.dto.prediction_dto import PredictionDTO
from infrastructure.persistence.sqlalchemy.repositories.prediction_repository import PredictionRepository


class GetPredictionsUseCase:
    """Caso de uso para obtener predicciones"""

    def __init__(self, db: Session):
        self.repository: IPredictionRepository = PredictionRepository(db)

    def execute(self) -> List[PredictionDTO]:
        """Ejecuta el caso de uso"""
        predictions = self.repository.find_all()
        return [PredictionDTO.from_entity(pred) for pred in predictions]


class GetPredictionsByRiskUseCase:
    """Caso de uso para obtener predicciones por nivel de riesgo"""

    def __init__(self, db: Session):
        self.repository: IPredictionRepository = PredictionRepository(db)

    def execute(self, risk_level: str) -> List[PredictionDTO]:
        """Ejecuta el caso de uso"""
        predictions = self.repository.find_by_risk_level(risk_level)
        return [PredictionDTO.from_entity(pred) for pred in predictions]


class GetPredictionsByStudentUseCase:
    """Caso de uso para obtener predicciones de un estudiante"""

    def __init__(self, db: Session):
        self.repository: IPredictionRepository = PredictionRepository(db)

    def execute(self, student_id: int) -> List[PredictionDTO]:
        """Ejecuta el caso de uso"""
        predictions = self.repository.find_by_student_id(student_id)
        return [PredictionDTO.from_entity(pred) for pred in predictions]

