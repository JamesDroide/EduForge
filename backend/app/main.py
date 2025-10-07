from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import numpy as np
import os

app = FastAPI(
    title="EduForge API",
    description="Sistema de predicción de deserción estudiantil",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "dropout_model.pkl")
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Advertencia: No se pudo cargar el modelo: {e}")

class StudentData(BaseModel):
    """Datos del estudiante para predicción"""
    attendance_rate: float = Field(..., ge=0, le=100, description="Porcentaje de asistencia")
    average_grade: float = Field(..., ge=0, le=10, description="Promedio de calificaciones")
    study_hours_per_week: float = Field(..., ge=0, le=168, description="Horas de estudio por semana")
    family_income: float = Field(..., ge=0, description="Ingreso familiar mensual")
    parent_education_level: int = Field(..., ge=1, le=5, description="Nivel educativo de padres (1-5)")
    extracurricular_activities: int = Field(..., ge=0, le=10, description="Número de actividades extracurriculares")
    failed_subjects: int = Field(..., ge=0, description="Número de materias reprobadas")
    age: int = Field(..., ge=15, le=30, description="Edad del estudiante")

class PredictionResponse(BaseModel):
    """Respuesta de predicción"""
    dropout_probability: float
    risk_level: str
    recommendations: List[str]

class StudentAnalysis(BaseModel):
    """Análisis detallado del estudiante"""
    student_id: str
    student_data: StudentData
    prediction: PredictionResponse
    factors_analysis: dict

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "EduForge API - Sistema de predicción de deserción estudiantil",
        "status": "active",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_dropout(student: StudentData):
    """Predecir riesgo de deserción para un estudiante"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Preparar datos para predicción
        features = np.array([[
            student.attendance_rate,
            student.average_grade,
            student.study_hours_per_week,
            student.family_income,
            student.parent_education_level,
            student.extracurricular_activities,
            student.failed_subjects,
            student.age
        ]])
        
        # Realizar predicción
        probability = model.predict_proba(features)[0][1]
        
        # Determinar nivel de riesgo
        if probability < 0.3:
            risk_level = "Bajo"
        elif probability < 0.6:
            risk_level = "Medio"
        else:
            risk_level = "Alto"
        
        # Generar recomendaciones
        recommendations = generate_recommendations(student, probability)
        
        return PredictionResponse(
            dropout_probability=round(probability * 100, 2),
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@app.post("/analyze", response_model=StudentAnalysis)
async def analyze_student(student_id: str, student: StudentData):
    """Análisis detallado de un estudiante específico"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Obtener predicción
        prediction_response = await predict_dropout(student)
        
        # Análisis de factores
        factors_analysis = analyze_factors(student)
        
        return StudentAnalysis(
            student_id=student_id,
            student_data=student,
            prediction=prediction_response,
            factors_analysis=factors_analysis
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/health")
async def health_check():
    """Verificar estado de la API"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

def generate_recommendations(student: StudentData, probability: float) -> List[str]:
    """Generar recomendaciones basadas en los datos del estudiante"""
    recommendations = []
    
    if student.attendance_rate < 75:
        recommendations.append("Mejorar asistencia a clases - Meta: >85%")
    
    if student.average_grade < 6:
        recommendations.append("Reforzar rendimiento académico con tutorías")
    
    if student.study_hours_per_week < 10:
        recommendations.append("Aumentar horas de estudio semanales - Recomendado: 15-20h")
    
    if student.failed_subjects > 2:
        recommendations.append("Programa de apoyo académico urgente")
    
    if student.extracurricular_activities == 0:
        recommendations.append("Participar en actividades extracurriculares para integración")
    
    if probability > 0.7:
        recommendations.append("Intervención inmediata: Entrevista con orientador")
    elif probability > 0.4:
        recommendations.append("Seguimiento mensual del progreso académico")
    
    if not recommendations:
        recommendations.append("Mantener el buen rendimiento actual")
    
    return recommendations

def analyze_factors(student: StudentData) -> dict:
    """Analizar factores individuales del estudiante"""
    return {
        "academic_performance": {
            "average_grade": student.average_grade,
            "status": "Excelente" if student.average_grade >= 8 else "Bueno" if student.average_grade >= 7 else "Regular" if student.average_grade >= 6 else "Necesita mejora",
            "failed_subjects": student.failed_subjects
        },
        "attendance": {
            "rate": student.attendance_rate,
            "status": "Excelente" if student.attendance_rate >= 90 else "Bueno" if student.attendance_rate >= 80 else "Regular" if student.attendance_rate >= 70 else "Crítico"
        },
        "study_habits": {
            "hours_per_week": student.study_hours_per_week,
            "status": "Excelente" if student.study_hours_per_week >= 20 else "Bueno" if student.study_hours_per_week >= 15 else "Regular" if student.study_hours_per_week >= 10 else "Insuficiente"
        },
        "socioeconomic_factors": {
            "family_income": student.family_income,
            "parent_education_level": student.parent_education_level,
            "status": "Favorable" if student.parent_education_level >= 4 else "Moderado" if student.parent_education_level >= 3 else "Requiere apoyo"
        },
        "engagement": {
            "extracurricular_activities": student.extracurricular_activities,
            "status": "Muy activo" if student.extracurricular_activities >= 3 else "Activo" if student.extracurricular_activities >= 1 else "Necesita mayor participación"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
