# src/application/dto/prediction_dto.py
"""
DTOs para predicciones
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from domain.entities.prediction import Prediction


@dataclass
class PredictionDTO:
    """DTO para predicción"""
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
    fecha: Optional[datetime]
    risk_factors: Optional[List[str]] = None

    @classmethod
    def from_entity(cls, entity: Prediction) -> 'PredictionDTO':
        """Crea un DTO desde una entidad"""
        return cls(
            id=entity.id,
            id_estudiante=entity.id_estudiante,
            nombre=entity.nombre,
            nota_final=entity.nota_final,
            conducta=entity.conducta,
            asistencia=entity.asistencia,
            inasistencia=entity.inasistencia,
            tiempo_prediccion=entity.tiempo_prediccion,
            resultado_prediccion=entity.resultado_prediccion,
            riesgo_desercion=entity.riesgo_desercion,
            probabilidad_desercion=entity.probabilidad_desercion,
            fecha=entity.fecha,
            risk_factors=entity.get_risk_factors()
        )

    def to_dict(self) -> dict:
        """Convierte el DTO a diccionario"""
        return {
            'id': self.id,
            'id_estudiante': self.id_estudiante,
            'nombre': self.nombre,
            'nota_final': self.nota_final,
            'conducta': self.conducta,
            'asistencia': self.asistencia,
            'inasistencia': self.inasistencia,
            'tiempo_prediccion': self.tiempo_prediccion,
            'resultado_prediccion': self.resultado_prediccion,
            'riesgo_desercion': self.riesgo_desercion,
            'probabilidad_desercion': self.probabilidad_desercion,
            'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha else None,
            'risk_factors': self.risk_factors
        }


@dataclass
class PredictionStatsDTO:
    """DTO para estadísticas de predicciones"""
    total_students: int
    high_risk: int
    medium_risk: int
    low_risk: int
    high_risk_percentage: float
    average_attendance: float
    average_grade: float
# src/infrastructure/persistence/sqlalchemy/repositories/prediction_repository.py
"""
Implementación del repositorio de predicciones usando SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from application.interfaces.prediction_repository_interface import IPredictionRepository
from domain.entities.prediction import Prediction
from infrastructure.persistence.sqlalchemy.models.prediction_model import PredictionModel


class PredictionRepository(IPredictionRepository):
    """Implementación del repositorio de predicciones"""

    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> List[Prediction]:
        """Obtiene todas las predicciones"""
        models = self.db.query(PredictionModel).all()
        return [self._to_entity(model) for model in models]

    def find_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Busca una predicción por ID"""
        model = self.db.query(PredictionModel).filter(PredictionModel.id == prediction_id).first()
        return self._to_entity(model) if model else None

    def find_by_student_id(self, student_id: int) -> List[Prediction]:
        """Busca predicciones por ID de estudiante"""
        models = self.db.query(PredictionModel).filter(
            PredictionModel.id_estudiante == student_id
        ).all()
        return [self._to_entity(model) for model in models]

    def find_by_risk_level(self, risk_level: str) -> List[Prediction]:
        """Busca predicciones por nivel de riesgo"""
        models = self.db.query(PredictionModel).filter(
            PredictionModel.riesgo_desercion == risk_level
        ).all()
        return [self._to_entity(model) for model in models]

    def save(self, prediction: Prediction) -> Prediction:
        """Guarda una predicción"""
        model = self._to_model(prediction)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def save_many(self, predictions: List[Prediction]) -> List[Prediction]:
        """Guarda múltiples predicciones"""
        models = [self._to_model(pred) for pred in predictions]
        self.db.add_all(models)
        self.db.commit()
        return [self._to_entity(model) for model in models]

    def delete_all(self) -> int:
        """Elimina todas las predicciones"""
        count = self.db.query(PredictionModel).delete()
        self.db.commit()
        return count

    def count(self) -> int:
        """Cuenta el total de predicciones"""
        return self.db.query(PredictionModel).count()

    def _to_entity(self, model: PredictionModel) -> Prediction:
        """Convierte un modelo ORM a entidad de dominio"""
        return Prediction(
            id=model.id,
            id_estudiante=model.id_estudiante,
            nombre=model.nombre,
            nota_final=model.nota_final,
            conducta=model.conducta,
            asistencia=model.asistencia,
            inasistencia=model.inasistencia,
            tiempo_prediccion=model.tiempo_prediccion,
            resultado_prediccion=model.resultado_prediccion,
            riesgo_desercion=model.riesgo_desercion,
            probabilidad_desercion=model.probabilidad_desercion,
            fecha=model.fecha
        )

    def _to_model(self, entity: Prediction) -> PredictionModel:
        """Convierte una entidad de dominio a modelo ORM"""
        return PredictionModel(
            id=entity.id,
            id_estudiante=entity.id_estudiante,
            nombre=entity.nombre,
            nota_final=entity.nota_final,
            conducta=entity.conducta,
            asistencia=entity.asistencia,
            inasistencia=entity.inasistencia,
            tiempo_prediccion=entity.tiempo_prediccion,
            resultado_prediccion=entity.resultado_prediccion,
            riesgo_desercion=entity.riesgo_desercion,
            probabilidad_desercion=entity.probabilidad_desercion,
            fecha=entity.fecha
        )

