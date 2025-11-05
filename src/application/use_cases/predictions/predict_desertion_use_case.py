# src/application/use_cases/predictions/predict_desertion_use_case.py
"""
Caso de uso: Realizar predicción de deserción
"""
from typing import List
import pandas as pd
from sqlalchemy.orm import Session

from application.interfaces.prediction_repository_interface import IPredictionRepository
from application.dto.prediction_dto import PredictionDTO
from infrastructure.persistence.sqlalchemy.repositories.prediction_repository import PredictionRepository
from infrastructure.ml.predictor import MLPredictor
from domain.exceptions.domain_exceptions import InvalidCSVException


class PredictDesertionUseCase:
    """Caso de uso para predecir deserción a partir de un CSV"""

    def __init__(self, db: Session):
        self.repository: IPredictionRepository = PredictionRepository(db)
        self.predictor = MLPredictor()

    def execute(self, file_path: str) -> List[PredictionDTO]:
        """
        Ejecuta el caso de uso de predicción

        Args:
            file_path: Ruta al archivo CSV

        Returns:
            Lista de predicciones como DTOs
        """
        # 1. Validar y leer CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise InvalidCSVException(f"Error leyendo CSV: {str(e)}")

        # 2. Realizar predicciones usando el modelo ML
        predictions_dict = self.predictor.predict(file_path)

        # 3. Limpiar predicciones anteriores
        self.repository.delete_all()

        # 4. Convertir a entidades de dominio
        from domain.entities.prediction import Prediction
        predictions = []
        for pred_dict in predictions_dict:
            prediction = Prediction(
                id=None,
                id_estudiante=pred_dict.get('id_estudiante', 0),
                nombre=pred_dict.get('nombre', 'Sin nombre'),
                nota_final=pred_dict.get('nota_final', 0.0),
                conducta=pred_dict.get('conducta', ''),
                asistencia=pred_dict.get('asistencia', 0.0),
                inasistencia=pred_dict.get('inasistencia', 0.0),
                tiempo_prediccion=pred_dict.get('tiempo_prediccion', 0.0),
                resultado_prediccion=pred_dict.get('resultado_prediccion', '0'),
                riesgo_desercion=pred_dict.get('riesgo_desercion', 'Bajo'),
                probabilidad_desercion=pred_dict.get('probabilidad_desercion', 0.0),
                fecha=pred_dict.get('fecha')
            )
            predictions.append(prediction)

        # 5. Guardar en repositorio
        saved_predictions = self.repository.save_many(predictions)

        # 6. Retornar como DTOs
        return [PredictionDTO.from_entity(pred) for pred in saved_predictions]

