# src/presentation/api/routes/prediction_routes.py
"""
Rutas de la API para predicciones
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from shared.utils.get_db import get_db
from application.use_cases.predictions.get_predictions_use_case import (
    GetPredictionsUseCase,
    GetPredictionsByRiskUseCase,
    GetPredictionsByStudentUseCase
)
from application.use_cases.predictions.predict_desertion_use_case import PredictDesertionUseCase
from application.dto.prediction_dto import PredictionDTO
from domain.exceptions.domain_exceptions import InvalidCSVException
from presentation.schemas.prediction_schema import PredictionResponse, PredictRequest

router = APIRouter(prefix="/predictions", tags=["Predicciones"])


@router.get("/", response_model=List[PredictionResponse])
async def get_all_predictions(db: Session = Depends(get_db)):
    """Obtiene todas las predicciones"""
    try:
        use_case = GetPredictionsUseCase(db)
        predictions = use_case.execute()
        return [pred.to_dict() for pred in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/{risk_level}", response_model=List[PredictionResponse])
async def get_predictions_by_risk(risk_level: str, db: Session = Depends(get_db)):
    """Obtiene predicciones por nivel de riesgo"""
    try:
        use_case = GetPredictionsByRiskUseCase(db)
        predictions = use_case.execute(risk_level)
        return [pred.to_dict() for pred in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}", response_model=List[PredictionResponse])
async def get_predictions_by_student(student_id: int, db: Session = Depends(get_db)):
    """Obtiene predicciones de un estudiante"""
    try:
        use_case = GetPredictionsByStudentUseCase(db)
        predictions = use_case.execute(student_id)
        return [pred.to_dict() for pred in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_from_file(
    filename: str,
    db: Session = Depends(get_db)
):
    """Realiza predicciones a partir de un archivo CSV"""
    try:
        import os
        # Construir ruta del archivo
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "uploads"))
        file_path = os.path.join(upload_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Ejecutar caso de uso
        use_case = PredictDesertionUseCase(db)
        predictions = use_case.execute(file_path)

        return {
            "predictions": [pred.to_dict() for pred in predictions],
            "total": len(predictions)
        }
    except InvalidCSVException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

