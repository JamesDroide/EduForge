from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.prediction_service import predict_dropout

router = APIRouter()

class StudentData(BaseModel):
    calificacion: float
    asistencia: float
    conducta: str

@router.post("/predict_dropout")
async def predict_dropout_api(student: StudentData):
    try:
        result = predict_dropout(student.calificacion, student.asistencia, student.conducta)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al realizar la predicción: {e}")
