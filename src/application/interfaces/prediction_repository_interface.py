# src/application/interfaces/prediction_repository_interface.py
"""
Interface para el repositorio de predicciones
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.prediction import Prediction


class IPredictionRepository(ABC):
    """Interface del repositorio de predicciones"""

    @abstractmethod
    def find_all(self) -> List[Prediction]:
        """Obtiene todas las predicciones"""
        pass

    @abstractmethod
    def find_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Busca una predicción por ID"""
        pass

    @abstractmethod
    def find_by_student_id(self, student_id: int) -> List[Prediction]:
        """Busca predicciones por ID de estudiante"""
        pass

    @abstractmethod
    def find_by_risk_level(self, risk_level: str) -> List[Prediction]:
        """Busca predicciones por nivel de riesgo"""
        pass

    @abstractmethod
    def save(self, prediction: Prediction) -> Prediction:
        """Guarda una predicción"""
        pass

    @abstractmethod
    def save_many(self, predictions: List[Prediction]) -> List[Prediction]:
        """Guarda múltiples predicciones"""
        pass

    @abstractmethod
    def delete_all(self) -> int:
        """Elimina todas las predicciones"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Cuenta el total de predicciones"""
        pass

