# EduForge API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Root Endpoint
**GET** `/`

Obtiene información general de la API.

**Response:**
```json
{
  "message": "EduForge API - Sistema de predicción de deserción estudiantil",
  "status": "active",
  "model_loaded": true
}
```

---

### 2. Health Check
**GET** `/health`

Verifica el estado de salud de la API.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

### 3. Predict Dropout
**POST** `/predict`

Predice el riesgo de deserción para un estudiante.

**Request Body:**
```json
{
  "attendance_rate": 85.0,
  "average_grade": 7.5,
  "study_hours_per_week": 15.0,
  "family_income": 2500.0,
  "parent_education_level": 3,
  "extracurricular_activities": 2,
  "failed_subjects": 0,
  "age": 18
}
```

**Field Descriptions:**
- `attendance_rate` (float): Porcentaje de asistencia (0-100)
- `average_grade` (float): Promedio de calificaciones (0-10)
- `study_hours_per_week` (float): Horas de estudio semanales (0-168)
- `family_income` (float): Ingreso familiar mensual en moneda local (>= 0)
- `parent_education_level` (int): Nivel educativo de padres (1-5)
  - 1: Primaria
  - 2: Secundaria
  - 3: Preparatoria
  - 4: Universidad
  - 5: Posgrado
- `extracurricular_activities` (int): Número de actividades extracurriculares (0-10)
- `failed_subjects` (int): Número de materias reprobadas (>= 0)
- `age` (int): Edad del estudiante (15-30)

**Response:**
```json
{
  "dropout_probability": 4.71,
  "risk_level": "Bajo",
  "recommendations": [
    "Mantener el buen rendimiento actual"
  ]
}
```

**Risk Levels:**
- `Bajo`: dropout_probability < 30%
- `Medio`: 30% <= dropout_probability < 60%
- `Alto`: dropout_probability >= 60%

---

### 4. Analyze Student
**POST** `/analyze?student_id={id}`

Realiza un análisis detallado de un estudiante específico.

**Query Parameters:**
- `student_id` (string): Identificador único del estudiante

**Request Body:**
Same as `/predict` endpoint

**Response:**
```json
{
  "student_id": "EST-001",
  "student_data": {
    "attendance_rate": 85.0,
    "average_grade": 7.5,
    "study_hours_per_week": 15.0,
    "family_income": 2500.0,
    "parent_education_level": 3,
    "extracurricular_activities": 2,
    "failed_subjects": 0,
    "age": 18
  },
  "prediction": {
    "dropout_probability": 4.71,
    "risk_level": "Bajo",
    "recommendations": [
      "Mantener el buen rendimiento actual"
    ]
  },
  "factors_analysis": {
    "academic_performance": {
      "average_grade": 7.5,
      "status": "Bueno",
      "failed_subjects": 0
    },
    "attendance": {
      "rate": 85.0,
      "status": "Bueno"
    },
    "study_habits": {
      "hours_per_week": 15.0,
      "status": "Bueno"
    },
    "socioeconomic_factors": {
      "family_income": 2500.0,
      "parent_education_level": 3,
      "status": "Moderado"
    },
    "engagement": {
      "extracurricular_activities": 2,
      "status": "Activo"
    }
  }
}
```

---

## Error Responses

### 400 Bad Request
Datos de entrada inválidos o faltantes.

```json
{
  "detail": [
    {
      "loc": ["body", "attendance_rate"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 500 Internal Server Error
Error del servidor durante el procesamiento.

```json
{
  "detail": "Error en predicción: <error message>"
}
```

### 503 Service Unavailable
Modelo de ML no disponible.

```json
{
  "detail": "Modelo no disponible"
}
```

---

## Examples

### Example 1: Low Risk Student
**Request:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_rate": 95,
    "average_grade": 8.5,
    "study_hours_per_week": 20,
    "family_income": 3500,
    "parent_education_level": 4,
    "extracurricular_activities": 3,
    "failed_subjects": 0,
    "age": 18
  }'
```

**Response:**
```json
{
  "dropout_probability": 1.2,
  "risk_level": "Bajo",
  "recommendations": [
    "Mantener el buen rendimiento actual"
  ]
}
```

### Example 2: High Risk Student
**Request:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_rate": 60,
    "average_grade": 5.0,
    "study_hours_per_week": 5,
    "family_income": 1000,
    "parent_education_level": 1,
    "extracurricular_activities": 0,
    "failed_subjects": 4,
    "age": 19
  }'
```

**Response:**
```json
{
  "dropout_probability": 84.5,
  "risk_level": "Alto",
  "recommendations": [
    "Mejorar asistencia a clases - Meta: >85%",
    "Reforzar rendimiento académico con tutorías",
    "Aumentar horas de estudio semanales - Recomendado: 15-20h",
    "Programa de apoyo académico urgente",
    "Participar en actividades extracurriculares para integración",
    "Intervención inmediata: Entrevista con orientador"
  ]
}
```

### Example 3: Detailed Analysis
**Request:**
```bash
curl -X POST "http://localhost:8000/analyze?student_id=EST-001" \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_rate": 85,
    "average_grade": 7.5,
    "study_hours_per_week": 15,
    "family_income": 2500,
    "parent_education_level": 3,
    "extracurricular_activities": 2,
    "failed_subjects": 0,
    "age": 18
  }'
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test the API endpoints directly from your browser.
