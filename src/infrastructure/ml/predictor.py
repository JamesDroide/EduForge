# src/infrastructure/ml/predictor.py
"""
Wrapper para el modelo de Machine Learning
Contiene la lógica de predicción aislada
"""
import sys
import os

# Agregar path de models para importar predictor original
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from models.predictor import predict_desertion as original_predict


class MLPredictor:
    """
    Wrapper para el modelo de ML
    Abstrae la implementación del predictor original
    """

    def predict(self, file_path: str) -> list:
        """
        Realiza predicciones de deserción

        Args:
            file_path: Ruta al archivo CSV con datos de estudiantes

        Returns:
            Lista de diccionarios con las predicciones
        """
        return original_predict(file_path)

