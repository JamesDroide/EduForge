from sklearn.preprocessing import StandardScaler
from src.models.prediction_model import DropoutPredictionModel

model_path = r"C:\Users\james\OneDrive\Documentos\PREGRADO UPAO\CICLO 9\Tesis I\EduForge\src\models\trained\dropout_model.pkl"
scaler_path = r"C:\Users\james\OneDrive\Documentos\PREGRADO UPAO\CICLO 9\Tesis I\EduForge\src\models\trained\scaler.pkl"

model = DropoutPredictionModel(model_path, scaler_path)


def predict_dropout(calificacion: float, asistencia: float, conducta: str):
    """
    Realiza la predicción sobre si un estudiante va a desertar o no.

    :param calificacion: La calificación del estudiante
    :param asistencia: El porcentaje de asistencia del estudiante
    :param conducta: La conducta del estudiante ("Buena", "Mala")
    :return: Un mensaje indicando si el estudiante tiene riesgo de deserción o no
    """
    try:
        conducta_val = 1 if conducta.lower() == 'buena' else 0
        features = [calificacion, asistencia, conducta_val]
        features_scaled = StandardScaler().fit_transform([features])
        prediction = model.predict(features_scaled)

        if prediction == 1:
            return {"prediccion": "Sí", "mensaje": "El estudiante tiene riesgo de deserción."}
        else:
            return {"prediccion": "No", "mensaje": "El estudiante no tiene riesgo de deserción."}
    except Exception as e:
        raise Exception(f"Error al realizar la predicción: {e}")
