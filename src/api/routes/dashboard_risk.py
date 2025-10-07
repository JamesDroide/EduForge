# src/api/routes/dashboard_risk.py

from fastapi import APIRouter, Depends
from services.risk_service import RiskService
from pydantic import BaseModel
from typing import List

router = APIRouter()

class StudentRisk(BaseModel):
    student_id: int
    name: str
    grade: str  # Primary or Secondary
    risk_level: str  # Indicator of risk (e.g., High, Medium, Low)

class RiskSummaryResponse(BaseModel):
    labels: List[str]
    data: List[float]
    counts: List[int] = []  # Cantidades de estudiantes en riesgo
    totals: List[int] = []  # Totales de estudiantes por mes

@router.get("/students_at_risk", response_model=List[StudentRisk])
async def get_students_at_risk(risk_service: RiskService = Depends()):
    # Llamamos al servicio para obtener la lista de estudiantes en riesgo
    students_at_risk = risk_service.get_students_at_risk()
    return students_at_risk

@router.get("/risk_summary")
async def get_risk_summary(risk_service: RiskService = Depends()):
    """
    Endpoint actualizado que devuelve porcentajes, cantidades y totales de estudiantes en riesgo
    """
    summary = risk_service.get_monthly_dropout_risk_summary()

    return {
        "labels": summary.get("labels", []),
        "data": summary.get("data", []),
        "counts": summary.get("counts", []),
        "totals": summary.get("totals", [])
    }
