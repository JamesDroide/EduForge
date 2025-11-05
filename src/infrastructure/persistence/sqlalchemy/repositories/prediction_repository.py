# src/infrastructure/persistence/sqlalchemy/repositories/prediction_repository.py
"""
Implementación del repositorio de predicciones
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from application.interfaces.prediction_repository_interface import IPredictionRepository
from domain.entities.prediction import Prediction
from infrastructure.persistence.sqlalchemy.models.prediction_model import PredictionModel


class PredictionRepository(IPredictionRepository):
    """Implementación SQLAlchemy del repositorio de predicciones"""

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

    def find_by_student(self, student_id: int) -> List[Prediction]:
        """Busca predicciones por ID de estudiante"""
        models = self.db.query(PredictionModel).filter(
            PredictionModel.id_estudiante == student_id
        ).all()
        return [self._to_entity(model) for model in models]

    def find_by_risk(self, risk_level: str) -> List[Prediction]:
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
        count = self.db.query(PredictionModel).count()
        self.db.query(PredictionModel).delete()
        self.db.commit()
        return count

    def count(self) -> int:
        """Cuenta el total de predicciones"""
        return self.db.query(PredictionModel).count()

    def _to_entity(self, model: PredictionModel) -> Prediction:
        """Convierte modelo ORM a entidad de dominio"""
        return Prediction(
            id=model.id,
            id_estudiante=model.id_estudiante,
            nombre=model.nombre or "Sin nombre",
            fecha=model.fecha if model.fecha else datetime.now(),
            nota_final=model.nota_final,
            asistencia=model.asistencia,
            inasistencia=model.inasistencia or 0.0,
            conducta=model.conducta or "Regular",
            resultado_prediccion=model.resultado_prediccion or "0",
            riesgo_desercion=model.riesgo_desercion or "Bajo",
            probabilidad_desercion=model.probabilidad_desercion or 0.0,
            tiempo_prediccion=model.tiempo_prediccion
        )

    def _to_model(self, entity: Prediction) -> PredictionModel:
        """Convierte entidad de dominio a modelo ORM"""
        return PredictionModel(
            id=entity.id,
            id_estudiante=entity.id_estudiante,
            nombre=entity.nombre,
            nota=entity.nota_final,
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

