# src/application/use_cases/predictions/get_predictions_use_case.py
"""
Casos de uso: Obtener predicciones
"""
from typing import List
from sqlalchemy.orm import Session

from application.interfaces.prediction_repository_interface import IPredictionRepository
from infrastructure.persistence.sqlalchemy.repositories.prediction_repository import PredictionRepository
from application.dto.prediction_dto import PredictionDTO


class GetPredictionsUseCase:
    """Caso de uso para obtener todas las predicciones"""

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
        predictions = self.repository.find_by_risk(risk_level)
        return [PredictionDTO.from_entity(pred) for pred in predictions]


class GetPredictionsByStudentUseCase:
    """Caso de uso para obtener predicciones de un estudiante"""

    def __init__(self, db: Session):
        self.repository: IPredictionRepository = PredictionRepository(db)

    def execute(self, student_id: int) -> List[PredictionDTO]:
        """Ejecuta el caso de uso"""
        predictions = self.repository.find_by_student(student_id)
        return [PredictionDTO.from_entity(pred) for pred in predictions]

