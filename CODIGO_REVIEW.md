# 🔍 Revisión Integral del Código - EduForge

## Resumen Ejecutivo

Este documento presenta una revisión exhaustiva del código del sistema EduForge, un sistema de predicción de deserción estudiantil desarrollado con FastAPI (backend) y React (frontend).

**Fecha de Revisión:** 14 de Octubre, 2025  
**Revisado por:** GitHub Copilot Agent  
**Versión del Código:** Commit bd6070f

---

## 📊 Calificación General

| Categoría | Calificación | Estado |
|-----------|--------------|--------|
| Seguridad | ⚠️ 6/10 | Requiere Atención |
| Calidad de Código | ⚠️ 7/10 | Mejorable |
| Arquitectura | ✅ 7.5/10 | Buena |
| Rendimiento | ⚠️ 6.5/10 | Requiere Optimización |
| Mantenibilidad | ✅ 7/10 | Aceptable |
| Testing | ❌ 3/10 | Crítico |

---

## 🔴 PROBLEMAS CRÍTICOS

### 1. Credenciales Hardcodeadas en el Código

**Archivo:** `src/config.py` (línea 8)  
**Severidad:** 🔴 CRÍTICA

```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamesdroide@localhost:5432/eduforge")
```

**Problema:**
- La contraseña de la base de datos (`jamesdroide`) está expuesta en el código fuente
- Cualquier persona con acceso al repositorio puede ver las credenciales
- Riesgo de seguridad si el repositorio es público o si las credenciales son compartidas

**Recomendación:**
```python
# ✅ CORRECTO
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

# O usar un valor por defecto genérico sin credenciales reales
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/eduforge")
```

**Adicional:** `notebooks/data_1/data_preprocessing.py` (línea 5)
```python
ruta_csv = r'C:\Users\james\OneDrive\Documentos\PREGRADO UPAO\...'
```
- Ruta absoluta personal expuesta que revela información del sistema de desarrollo

---

### 2. Ausencia de Tests Automatizados

**Archivo:** `tests/test_api.py`  
**Severidad:** 🔴 CRÍTICA

**Problema:**
- El archivo de tests está completamente vacío
- No hay validación automatizada del código
- Alto riesgo de introducir bugs en producción
- Dificulta refactorización segura

**Recomendación:**
Implementar tests para los componentes críticos:

```python
# tests/test_predictor.py
import pytest
from src.models.predictor import predict_desertion, validate_input_data_real
import pandas as pd

def test_predict_desertion_with_valid_data():
    # Crear CSV de prueba
    test_data = pd.DataFrame({
        'estudiante_id': [1, 2],
        'nombre': ['Test 1', 'Test 2'],
        'nota_final': [15.0, 8.0],
        'asistencia': [90.0, 60.0],
        'inasistencia': [10.0, 40.0],
        'conducta': ['positivo', 'neutral']
    })
    test_file = '/tmp/test_data.csv'
    test_data.to_csv(test_file, index=False)
    
    results = predict_desertion(test_file)
    assert len(results) == 2
    assert 'riesgo_desercion' in results[0]

def test_validate_input_data_missing_columns():
    df = pd.DataFrame({'col1': [1, 2]})
    assert validate_input_data_real(df) == False
```

---

### 3. Falta de Validación en Endpoints de API

**Archivos:** `src/main.py` (múltiples endpoints)  
**Severidad:** 🔴 ALTA

**Problema en `/predict`:**
```python
@app.post("/predict")
async def predict(filename: str):
    # No hay validación del tipo de archivo
    # No hay sanitización del nombre de archivo
    # Riesgo de path traversal
```

**Vulnerabilidades:**
1. **Path Traversal:** Un atacante podría usar `filename="../../../etc/passwd"`
2. **Sin validación de extensión:** Podría intentar ejecutar archivos no CSV
3. **Sin límite de tamaño de archivo**

**Recomendación:**
```python
import re
from pathlib import Path

@app.post("/predict")
async def predict(filename: str):
    # Validar nombre de archivo
    if not re.match(r'^[\w\-. ]+\.csv$', filename):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    
    # Prevenir path traversal
    filename = Path(filename).name  # Solo nombre, sin path
    
    # Validar que el archivo existe y es un archivo regular
    file_path = Path(upload_dir) / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # Continuar con la lógica...
```

---

## ⚠️ PROBLEMAS DE SEVERIDAD ALTA

### 4. Gestión Inadecuada de Sesiones de Base de Datos

**Archivos:** `src/main.py`, `src/services/risk_service.py`  
**Severidad:** ⚠️ ALTA

**Problemas encontrados:**

**Ejemplo 1: Inconsistencia en cierre de sesiones**
```python
# src/main.py línea 177
promedio_notas = sum(r.nota for r in resultados) / total_estudiantes
```
- Usa `r.nota` pero el campo correcto es `r.nota_final`
- Esto causará errores en tiempo de ejecución

**Ejemplo 2: Falta de manejo de excepciones en transacciones**
```python
# src/models/predictor.py línea 151-157
try:
    session.query(ResultadoPrediccion).delete()
    session.commit()
except Exception as e:
    logger.warning(f"⚠️ Error limpiando registros anteriores: {e}")
    session.rollback()
```
- Bien manejado aquí ✅

Pero en otros lugares:
```python
# src/main.py línea 126-132
session = SessionLocal()
resultados = session.query(ResultadoPrediccion).all()
session.close()
```
- No hay manejo de excepciones
- Si falla la query, la sesión no se cierra

**Recomendación - Usar Context Managers:**
```python
from contextlib import contextmanager

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Uso:
with get_db_session() as session:
    resultados = session.query(ResultadoPrediccion).all()
```

---

### 5. Variables Globales Compartidas (Thread-Safety Issues)

**Archivo:** `src/services/risk_service.py` (líneas 7-8)  
**Severidad:** ⚠️ ALTA

```python
# Variable global para almacenar los últimos resultados
latest_predictions = []
```

**Problema:**
- En un entorno multi-threaded (uvicorn con múltiples workers), esta variable global puede causar:
  - Race conditions
  - Data corruption
  - Resultados inconsistentes entre requests

**Recomendación:**
```python
# Opción 1: Usar caché distribuido
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Opción 2: Siempre leer de la base de datos (más confiable)
def get_latest_predictions():
    session = SessionLocal()
    try:
        results = session.query(ResultadoPrediccion).all()
        return [format_prediction(r) for r in results]
    finally:
        session.close()

# Opción 3: Usar threading.local para datos por thread
import threading
thread_local = threading.local()
```

---

### 6. Inconsistencia en Nombres de Campos de Base de Datos

**Archivos:** Múltiples  
**Severidad:** ⚠️ ALTA

**Problema:**
```python
# src/main.py línea 177
promedio_notas = sum(r.nota for r in resultados) / total_estudiantes

# Pero en la base de datos el campo es 'nota_final'
# src/models/predictor.py línea 232
nota_final=nota_final_value,
```

**Evidencia adicional:**
```python
# src/main.py línea 138
"nota": r.nota_final,  # Mantener 'nota' por compatibilidad
"nota_final": r.nota_final,
```

**Recomendación:**
1. Unificar nomenclatura en la base de datos
2. Usar un solo nombre de campo
3. Crear property en el modelo SQLAlchemy si se necesita compatibilidad:

```python
class ResultadoPrediccion(Base):
    __tablename__ = 'resultados_prediccion'
    
    nota_final = Column(Float)
    
    @property
    def nota(self):
        """Alias para compatibilidad"""
        return self.nota_final
```

---

## ⚠️ PROBLEMAS DE SEVERIDAD MEDIA

### 7. Logging Excesivo en Producción

**Archivo:** `src/services/risk_service.py`  
**Severidad:** ⚠️ MEDIA

**Problema:**
```python
print(f"🔍 DEBUG: get_students_at_risk - {len(results)} registros encontrados en BD")
print(f"🔍 DEBUG: Procesando estudiante {result.nombre}: nota={nota_value}...")
```

- Uso de `print()` en lugar de logging
- Mensajes DEBUG en código de producción
- Emojis pueden causar problemas de encoding
- Impacto en rendimiento con grandes volúmenes de datos

**Recomendación:**
```python
import logging

logger = logging.getLogger(__name__)

# Configuración en main.py o config.py
logging.basicConfig(
    level=logging.INFO if os.getenv('ENV') == 'production' else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# En el código:
logger.debug(f"Procesando estudiante {result.nombre}: nota={nota_value}")
logger.info(f"Estudiantes procesados: {len(results)}")
```

---

### 8. CORS Demasiado Permisivo

**Archivo:** `src/main.py` (líneas 28-41)  
**Severidad:** ⚠️ MEDIA

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.vercel.app",  # ⚠️ Demasiado permisivo
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # ⚠️ Permite todos los headers
)
```

**Problemas:**
- Wildcard en subdominios permite potenciales ataques
- `allow_headers=["*"]` es innecesariamente permisivo
- En producción, deberías especificar orígenes exactos

**Recomendación:**
```python
# Cargar orígenes desde variable de entorno
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

### 9. Feature Engineering Duplicado

**Archivo:** `src/models/entrenar_modelo_mejorado.py` (líneas 86-118)  
**Severidad:** ⚠️ MEDIA

**Problema:**
- La función `feature_engineering_avanzado` tiene lógica compleja
- Esta lógica NO se aplica en `predictor.py` durante la inferencia
- **Inconsistencia entre entrenamiento y predicción**

**Comparación:**

**Entrenamiento (entrenar_modelo_mejorado.py):**
```python
def feature_engineering_avanzado(df):
    # Progreso entre períodos
    df['progreso_notas'] = df['nota_periodo_2'] - df['nota_periodo_1']
    df['tendencia_negativa'] = (df['progreso_notas'] < -0.1).astype(int)
    # ... más features
```

**Predicción (predictor.py):**
```python
def prepare_features_real(df: pd.DataFrame) -> pd.DataFrame:
    # Solo features básicas, NO incluye progreso_notas
    df_features['nota_normalizada'] = df_features['nota_final'] / 20.0
    df_features['conducta_encoded'] = ...
    # Falta feature_engineering_avanzado
```

**Impacto:**
- El modelo espera características que no se proporcionan
- Resultados de predicción pueden ser incorrectos o inconsistentes
- Error potencial si el modelo busca columnas que no existen

**Recomendación:**
1. Extraer feature engineering a un módulo compartido
2. Aplicar las mismas transformaciones en entrenamiento y predicción
3. Validar que las características coinciden

```python
# src/utils/feature_engineering.py
def create_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """Crea características avanzadas para entrenamiento Y predicción"""
    df_copy = df.copy()
    
    # 1. Progreso entre períodos (si existen las columnas)
    if 'nota_periodo_1' in df_copy.columns and 'nota_periodo_2' in df_copy.columns:
        df_copy['progreso_notas'] = df_copy['nota_periodo_2'] - df_copy['nota_periodo_1']
    else:
        df_copy['progreso_notas'] = 0  # Valor por defecto
    
    # ... más features
    return df_copy

# Usar en ambos archivos:
# - entrenar_modelo_mejorado.py
# - predictor.py
```

---

### 10. Generación de Nombres Falsos en Datos de Producción

**Archivo:** `src/models/predictor.py` (líneas 195-215)  
**Severidad:** ⚠️ MEDIA

```python
if 'nombre' in row.index and pd.notna(row['nombre']) and str(row['nombre']).strip():
    nombre = str(row['nombre']).strip()
else:
    # Lista de nombres realistas para generar automáticamente
    nombres_femeninos = ["Ana Sofia Martinez", "Maria Isabel Torres", ...]
    # Alternar entre nombres femeninos y masculinos
    if estudiante_id % 2 == 1:
        nombre = nombres_femeninos[(estudiante_id - 1) % len(nombres_femeninos)]
```

**Problemas:**
1. **Privacidad:** Genera nombres que parecen reales pero son falsos
2. **Confusión:** Los usuarios pueden pensar que son estudiantes reales
3. **Auditoría:** Dificulta rastrear qué datos son reales vs generados
4. **GDPR/Compliance:** Problemas potenciales con regulaciones de datos

**Recomendación:**
```python
if 'nombre' in row.index and pd.notna(row['nombre']) and str(row['nombre']).strip():
    nombre = str(row['nombre']).strip()
else:
    # Usar un formato que indique claramente que es un placeholder
    nombre = f"Estudiante_{estudiante_id:04d}"
    logger.warning(f"Nombre no proporcionado para ID {estudiante_id}, usando placeholder")
```

---

### 11. Manejo de Fechas Inconsistente

**Archivos:** `src/upload.py`, `src/models/predictor.py`  
**Severidad:** ⚠️ MEDIA

**Problema 1 - Fecha Hardcodeada:**
```python
# src/models/predictor.py línea 167
fecha_formateada = "2025-10-06"  # Fecha actual como defecto
```
- Fecha hardcodeada en lugar de usar `datetime.now()`

**Problema 2 - Lógica de Conversión Duplicada:**
```python
# src/upload.py línea 12-34
def excel_date_to_str(excel_date):
    # Conversión compleja de fechas Excel

# src/models/predictor.py línea 168-183
if 'fecha' in row.index and pd.notna(row['fecha']):
    try:
        fecha_original = str(row['fecha']).strip()
        if '/' in fecha_original:
            parts = fecha_original.split('/')
            # ... lógica de conversión duplicada
```

**Recomendación:**
```python
# src/utils/date_utils.py
from datetime import datetime
from typing import Union

def normalize_date(date_value: Union[str, int, float]) -> str:
    """Normaliza fechas en diferentes formatos a YYYY-MM-DD"""
    try:
        # Si es string
        if isinstance(date_value, str):
            date_value = date_value.strip()
            
            # Formato DD/MM/YYYY
            if '/' in date_value:
                dt = datetime.strptime(date_value, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d')
            
            # Formato YYYY-MM-DD (ya normalizado)
            datetime.strptime(date_value, '%Y-%m-%d')
            return date_value
        
        # Si es número (Excel serial date)
        if isinstance(date_value, (int, float)):
            base_date = datetime(1899, 12, 30)
            dt = base_date + timedelta(days=float(date_value))
            return dt.strftime('%Y-%m-%d')
    
    except Exception as e:
        logger.warning(f"Error parsing date {date_value}: {e}")
        return datetime.now().strftime('%Y-%m-%d')  # Usar fecha actual
    
    # Default
    return datetime.now().strftime('%Y-%m-%d')
```

---

## 💡 MEJORAS DE CÓDIGO RECOMENDADAS

### 12. Refactorizar Endpoint Monolítico `/predict`

**Archivo:** `src/main.py` (líneas 66-112)  
**Severidad:** 💡 MEJORA

**Problema:**
- Endpoint con más de 45 líneas
- Múltiples responsabilidades:
  - Validación de archivo
  - Lectura de datos
  - Predicción
  - Actualización de servicios
- Dificulta testing y mantenimiento

**Recomendación:**
```python
# src/services/prediction_service.py
class PredictionService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
    
    def validate_file_exists(self, filename: str) -> str:
        """Valida que el archivo existe y retorna la ruta"""
        file_path = os.path.join(self.upload_dir, filename)
        if not os.path.exists(file_path):
            available_files = os.listdir(self.upload_dir)
            raise HTTPException(
                status_code=404,
                detail=f"Archivo no encontrado. Disponibles: {available_files}"
            )
        return file_path
    
    def validate_csv_readable(self, file_path: str) -> pd.DataFrame:
        """Valida que el CSV es legible"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"CSV válido: {len(df)} filas, columnas: {df.columns.tolist()}")
            return df
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error leyendo CSV: {str(e)}"
            )
    
    async def process_predictions(self, file_path: str) -> List[Dict]:
        """Procesa predicciones y actualiza servicios"""
        # Validar CSV
        self.validate_csv_readable(file_path)
        
        # Predicciones
        predictions = predict_desertion(file_path)
        
        # Actualizar servicios
        update_latest_predictions(predictions)
        update_attendance_data(predictions)
        
        return predictions

# En main.py
prediction_service = PredictionService(UPLOAD_DIR)

@app.post("/predict")
async def predict(filename: str):
    try:
        return await prediction_service.process_predictions(
            prediction_service.validate_file_exists(filename)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 13. Eliminar Código Comentado y Debug

**Múltiples Archivos**  
**Severidad:** 💡 MEJORA

**Problemas encontrados:**
```python
# src/main.py línea 72
print(f"Buscando archivo en: {file_path}")  # Para depuración

# src/services/risk_service.py líneas 24, 39, 40
print(f"🔍 DEBUG: get_students_at_risk...")
print(f"🔍 DEBUG: Procesando estudiante...")
```

**Recomendación:**
- Usar logging apropiado en lugar de print()
- Configurar niveles de log (DEBUG, INFO, WARNING, ERROR)
- Remover mensajes DEBUG del código de producción

---

### 14. Optimizar Queries de Base de Datos

**Archivo:** `src/services/risk_service.py`  
**Severidad:** 💡 MEJORA

**Problema:**
```python
def get_students_at_risk(self):
    results = db.query(ResultadoPrediccion).all()  # Trae TODOS los registros
    
    all_students = []
    for result in results:
        # Procesa cada uno individualmente
        all_students.append({...})
```

**Problemas de rendimiento:**
- Trae todos los registros sin paginación
- Procesa datos en Python que podrían procesarse en SQL
- Sin índices en columnas frecuentemente consultadas

**Recomendación:**
```python
# Agregar índices en el modelo
class ResultadoPrediccion(Base):
    __tablename__ = 'resultados_prediccion'
    
    id = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, index=True)  # ✅ Índice
    riesgo_desercion = Column(String, index=True)  # ✅ Índice para filtros
    fecha = Column(DateTime, index=True)  # ✅ Índice para ordenamiento

# Usar paginación
def get_students_at_risk(self, page: int = 1, page_size: int = 50):
    offset = (page - 1) * page_size
    
    results = db.query(ResultadoPrediccion)\
        .filter(ResultadoPrediccion.riesgo_desercion == 'Alto')\
        .order_by(ResultadoPrediccion.probabilidad_desercion.desc())\
        .limit(page_size)\
        .offset(offset)\
        .all()
    
    total = db.query(ResultadoPrediccion)\
        .filter(ResultadoPrediccion.riesgo_desercion == 'Alto')\
        .count()
    
    return {
        'students': [format_student(r) for r in results],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': (total + page_size - 1) // page_size
    }
```

---

### 15. Validación de Datos de Entrada

**Archivo:** `src/models/predictor.py`  
**Severidad:** 💡 MEJORA

**Problema:**
```python
# No hay validación de rangos
nota_final_value = float(row.get('nota_final', 0))
asistencia_value = float(row.get('asistencia', 0))
```

**Riesgos:**
- Valores negativos
- Valores fuera de rango (ej: asistencia > 100%)
- Valores None o NaN sin manejo

**Recomendación:**
```python
def validate_and_sanitize_row(row: pd.Series) -> Dict:
    """Valida y sanitiza los datos de una fila"""
    
    # Nota final: debe estar entre 0 y 20
    nota_final = float(row.get('nota_final', 0))
    if nota_final < 0 or nota_final > 20:
        logger.warning(f"Nota fuera de rango: {nota_final}, ajustando")
        nota_final = max(0, min(20, nota_final))
    
    # Asistencia: debe estar entre 0 y 100
    asistencia = float(row.get('asistencia', 0))
    if asistencia < 0 or asistencia > 100:
        logger.warning(f"Asistencia fuera de rango: {asistencia}, ajustando")
        asistencia = max(0, min(100, asistencia))
    
    # Conducta: debe ser uno de los valores válidos
    conducta = str(row.get('conducta', 'neutral')).lower()
    valid_conductas = ['positivo', 'neutral', 'agresivo']
    if conducta not in valid_conductas:
        logger.warning(f"Conducta inválida: {conducta}, usando 'neutral'")
        conducta = 'neutral'
    
    return {
        'nota_final': nota_final,
        'asistencia': asistencia,
        'conducta': conducta,
        'inasistencia': float(row.get('inasistencia', 100 - asistencia))
    }
```

---

## 🏗️ ARQUITECTURA Y DISEÑO

### 16. Falta de Separación de Configuración por Entorno

**Archivos:** `src/config.py`, `frontend/src/config/api.js`  
**Severidad:** 💡 MEJORA

**Problema:**
- Configuración mezclada con lógica
- No hay archivos .env.example
- Dificulta deployment en diferentes entornos

**Recomendación:**
```python
# src/config/settings.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str
    database_pool_size: int = 5
    
    # Security
    allowed_origins: List[str] = ["http://localhost:3000"]
    secret_key: str
    
    # Application
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Model
    model_dir: str = "./scripts/models/trained"
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

```bash
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/eduforge
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

---

### 17. Mejorar Estructura de Respuestas API

**Múltiples Endpoints**  
**Severidad:** 💡 MEJORA

**Problema:**
- Respuestas inconsistentes entre endpoints
- Falta de estructura estándar
- Sin metadatos útiles (timestamp, versión, etc.)

**Ejemplo actual:**
```python
return {"predictions": predictions}  # Endpoint 1
return JSONResponse(content={"resultados": resultados_dict})  # Endpoint 2
return {"success": True, "message": "..."}  # Endpoint 3
```

**Recomendación:**
```python
# src/models/responses.py
from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    version: str = "1.0"

class PaginatedResponse(APIResponse):
    data: List[Any]
    page: int
    page_size: int
    total: int
    total_pages: int

# Uso en endpoints:
@app.get("/api/resultados-prediccion")
async def get_resultados_prediccion(page: int = 1, page_size: int = 50):
    try:
        # ... lógica ...
        return PaginatedResponse(
            success=True,
            data=resultados_dict,
            page=page,
            page_size=page_size,
            total=total_count,
            total_pages=(total_count + page_size - 1) // page_size
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message="Error al obtener resultados",
            errors=[str(e)]
        )
```

---

## 🚀 RENDIMIENTO

### 18. Caché de Predicciones del Modelo

**Archivo:** `frontend/src/utils/studentsCache.js`  
**Severidad:** 💡 MEJORA

**Observación:**
- El frontend implementa caché bien estructurado
- El backend NO implementa caché
- Cada request reprocesa desde la BD

**Recomendación Backend:**
```python
# src/utils/cache.py
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib

class PredictionCache:
    def __init__(self, ttl_seconds: int = 300):  # 5 minutos
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def _generate_key(self, data: str) -> str:
        """Genera key única basada en hash del contenido"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[List[Dict]]:
        """Obtiene del caché si no ha expirado"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: List[Dict]):
        """Guarda en caché con timestamp"""
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Limpia todo el caché"""
        self.cache.clear()

# Instancia global
prediction_cache = PredictionCache()

# Uso en predictor.py
def predict_desertion(file_path: str) -> List[Dict]:
    # Generar key basado en hash del archivo
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    # Intentar obtener del caché
    cached_result = prediction_cache.get(file_hash)
    if cached_result:
        logger.info("✅ Predicciones obtenidas del caché")
        return cached_result
    
    # Si no está en caché, procesar normalmente
    results = _process_predictions(file_path)
    
    # Guardar en caché
    prediction_cache.set(file_hash, results)
    
    return results
```

---

### 19. Optimizar Carga del Modelo ML

**Archivo:** `src/models/predictor.py` (líneas 22-31)  
**Severidad:** 💡 MEJORA

**Problema Actual:**
```python
# Carga del modelo al importar el módulo
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    config = joblib.load(CONFIG_PATH)
```

**Problemas:**
1. Se carga en cada worker de uvicorn (desperdicio de memoria)
2. Carga síncrona bloquea el startup
3. Sin lazy loading

**Recomendación:**
```python
# Singleton pattern para el modelo
class ModelManager:
    _instance = None
    _model = None
    _scaler = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self):
        """Carga lazy del modelo"""
        if self._model is None:
            logger.info("Cargando modelo ML...")
            self._model = joblib.load(MODEL_PATH)
            self._scaler = joblib.load(SCALER_PATH)
            self._config = joblib.load(CONFIG_PATH)
            logger.info("✅ Modelo cargado")
    
    @property
    def model(self):
        if self._model is None:
            self.load_model()
        return self._model
    
    @property
    def scaler(self):
        if self._scaler is None:
            self.load_model()
        return self._scaler
    
    @property
    def config(self):
        if self._config is None:
            self.load_model()
        return self._config

# Instancia global
model_manager = ModelManager()

# Uso
def predict_desertion(file_path: str):
    model = model_manager.model
    scaler = model_manager.scaler
    # ...
```

---

## 📱 FRONTEND

### 20. Manejo de Caché en Frontend

**Archivo:** `frontend/src/utils/studentsCache.js`  
**Severidad:** ✅ BUENA PRÁCTICA

**Observación Positiva:**
El código frontend tiene un buen sistema de caché:
- Invalidación apropiada en cambios
- Eventos personalizados para sincronización
- Timeout de 5 minutos configurable
- Manejo de estado de carga

**Sugerencias menores:**
```javascript
// Agregar compresión para localStorage
class StudentsCache {
  saveToLocalStorage(key, data) {
    try {
      // Comprimir datos antes de guardar
      const compressed = LZString.compress(JSON.stringify(data));
      localStorage.setItem(key, compressed);
    } catch (error) {
      console.error('Error guardando en localStorage:', error);
      // Si falla, intentar limpiar caché antiguo
      this.invalidate();
    }
  }
  
  loadFromLocalStorage(key) {
    try {
      const compressed = localStorage.getItem(key);
      if (compressed) {
        return JSON.parse(LZString.decompress(compressed));
      }
    } catch (error) {
      console.error('Error cargando de localStorage:', error);
      return null;
    }
  }
}
```

---

## 📋 DOCUMENTACIÓN

### 21. Falta de Documentación en Funciones Críticas

**Múltiples Archivos**  
**Severidad:** 💡 MEJORA

**Problema:**
Muchas funciones carecen de docstrings adecuadas:

```python
# src/models/predictor.py
def prepare_features_real(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara las características exactamente como el modelo entrenado las espera"""
    # ⚠️ Falta documentación de:
    # - Qué columnas espera el DataFrame
    # - Qué transformaciones aplica
    # - Qué columnas retorna
    # - Ejemplos de uso
```

**Recomendación:**
```python
def prepare_features_real(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara características del DataFrame para el modelo de predicción.
    
    Esta función transforma los datos crudos del CSV al formato que el modelo
    ML entrenado espera, aplicando las mismas transformaciones usadas durante
    el entrenamiento.
    
    Args:
        df: DataFrame con columnas requeridas:
            - nota_final (float): Nota del estudiante en escala 0-20
            - asistencia (float): Porcentaje de asistencia 0-100
            - inasistencia (float): Porcentaje de inasistencia 0-100
            - conducta (str): Categoría de conducta ('positivo', 'neutral', 'agresivo')
    
    Returns:
        DataFrame con características transformadas:
            - nota_normalizada (float): Nota escalada a 0-1
            - conducta_encoded (int): Conducta codificada (0=positivo, 1=neutral, 2=agresivo)
            - asistencia_normalizada (float): Asistencia escalada a 0-1
            - inasistencia_normalizada (float): Inasistencia escalada a 0-1
            - nota_baja (int): Indicador binario si nota < 11
            - alta_inasistencia (int): Indicador binario si inasistencia > 30
            - conducta_problematica (int): Indicador binario si conducta agresiva
    
    Raises:
        ValueError: Si faltan columnas requeridas
        TypeError: Si los tipos de datos son incorrectos
    
    Example:
        >>> df = pd.DataFrame({
        ...     'nota_final': [15.0, 8.5],
        ...     'asistencia': [90.0, 60.0],
        ...     'inasistencia': [10.0, 40.0],
        ...     'conducta': ['positivo', 'neutral']
        ... })
        >>> features = prepare_features_real(df)
        >>> print(features.columns)
        ['nota_normalizada', 'conducta_encoded', 'asistencia_normalizada', ...]
    """
    # Implementación...
```

---

## 🔒 SEGURIDAD ADICIONAL

### 22. Falta de Rate Limiting

**Archivo:** `src/main.py`  
**Severidad:** ⚠️ MEDIA

**Problema:**
- Sin límite de requests por IP/usuario
- Vulnerable a ataques DDoS
- Sin throttling en endpoints costosos

**Recomendación:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/predict")
@limiter.limit("10/minute")  # Máximo 10 predicciones por minuto
async def predict(request: Request, filename: str):
    # ...

@app.post("/upload")
@limiter.limit("5/minute")  # Máximo 5 uploads por minuto
async def upload_file(request: Request, file: UploadFile):
    # ...
```

---

### 23. Falta de Validación de Tamaño de Archivo

**Archivo:** `src/main.py`, `src/upload.py`  
**Severidad:** ⚠️ MEDIA

**Problema:**
```python
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # ⚠️ Sin validación de tamaño
    file_path = await save_uploaded_file(file)
```

**Riesgo:**
- Subida de archivos enormes puede agotar memoria/disco
- Ataque DoS subiendo archivos masivos

**Recomendación:**
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validar extensión
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos CSV"
        )
    
    # Validar tamaño
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()  # Obtener posición = tamaño
    file.file.seek(0)  # Volver al inicio
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo muy grande. Máximo: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
        )
    
    # Continuar con la lógica...
```

---

## 🧪 TESTING

### 24. Estrategia de Testing Inexistente

**Severidad:** 🔴 CRÍTICA

**Problema:**
- No hay tests unitarios
- No hay tests de integración
- No hay tests de API
- No hay cobertura de código

**Recomendación - Estructura de Tests:**

```
tests/
├── unit/
│   ├── test_predictor.py
│   ├── test_feature_engineering.py
│   ├── test_date_utils.py
│   └── test_models.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_upload_workflow.py
├── e2e/
│   └── test_prediction_flow.py
└── conftest.py
```

**Ejemplos de Tests Prioritarios:**

```python
# tests/unit/test_predictor.py
import pytest
import pandas as pd
from src.models.predictor import (
    validate_input_data_real,
    prepare_features_real,
    classify_risk_level
)

def test_classify_risk_level():
    """Test de clasificación de niveles de riesgo"""
    assert classify_risk_level(0.8) == "Alto"
    assert classify_risk_level(0.5) == "Medio"
    assert classify_risk_level(0.2) == "Bajo"

def test_validate_input_data_missing_columns():
    """Test de validación con columnas faltantes"""
    df = pd.DataFrame({'col1': [1, 2]})
    assert validate_input_data_real(df) == False

def test_validate_input_data_valid():
    """Test de validación con datos válidos"""
    df = pd.DataFrame({
        'nota_final': [15.0],
        'asistencia': [90.0],
        'inasistencia': [10.0],
        'conducta': ['positivo']
    })
    assert validate_input_data_real(df) == True

def test_prepare_features_normalization():
    """Test de normalización de características"""
    df = pd.DataFrame({
        'nota_final': [20.0, 0.0],
        'asistencia': [100.0, 0.0],
        'inasistencia': [0.0, 100.0],
        'conducta': ['positivo', 'agresivo']
    })
    
    result = prepare_features_real(df)
    
    # Verificar normalización de nota
    assert result['nota_normalizada'].iloc[0] == 1.0
    assert result['nota_normalizada'].iloc[1] == 0.0
    
    # Verificar codificación de conducta
    assert result['conducta_encoded'].iloc[0] == 0  # positivo
    assert result['conducta_encoded'].iloc[1] == 2  # agresivo
```

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
import tempfile
import pandas as pd

client = TestClient(app)

def test_upload_endpoint():
    """Test de endpoint /upload"""
    # Crear archivo CSV temporal
    df = pd.DataFrame({
        'estudiante_id': [1, 2],
        'nombre': ['Test 1', 'Test 2'],
        'nota_final': [15.0, 8.0],
        'asistencia': [90.0, 60.0],
        'inasistencia': [10.0, 40.0],
        'conducta': ['positivo', 'neutral']
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        
        with open(f.name, 'rb') as file:
            response = client.post(
                "/upload",
                files={"file": ("test.csv", file, "text/csv")}
            )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "filename" in data

def test_predict_endpoint():
    """Test de endpoint /predict"""
    # Primero subir un archivo
    # ... (usar test_upload_endpoint como helper)
    
    response = client.post("/predict", params={"filename": "test.csv"})
    
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0

def test_estadisticas_endpoint():
    """Test de endpoint /api/estadisticas-generales"""
    response = client.get("/api/estadisticas-generales")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_estudiantes" in data
    assert "porcentaje_riesgo" in data
```

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term
```

---

## 📊 RESUMEN DE ISSUES POR PRIORIDAD

### 🔴 CRÍTICOS (Requieren atención inmediata)

1. **Credenciales Hardcodeadas** - config.py
2. **Ausencia de Tests** - tests/
3. **Falta de Validación en APIs** - main.py

### ⚠️ ALTOS (Deben resolverse pronto)

4. **Gestión de Sesiones de BD** - Múltiples archivos
5. **Variables Globales Thread-Unsafe** - risk_service.py
6. **Inconsistencia de Campos** - main.py, predictor.py

### 💡 MEJORAS (Cuando haya tiempo)

7-11. Logging, CORS, Feature Engineering, Generación de Nombres, Fechas
12-15. Refactoring, Optimización, Validación
16-19. Arquitectura, Respuestas API, Caché, Carga de Modelo
20-23. Frontend, Documentación, Rate Limiting, Tamaño de Archivos

---

## ✅ ASPECTOS POSITIVOS DEL CÓDIGO

1. **Buena estructura de proyecto** - Separación clara de concerns (models, services, api)
2. **Uso de FastAPI** - Framework moderno y bien implementado
3. **Logging estructurado** - En la mayoría de lugares (aunque mejorable)
4. **Manejo de ML profesional** - Uso correcto de scikit-learn y joblib
5. **Frontend con caché** - Implementación sólida de caché en React
6. **Documentación README** - README.md bien estructurado
7. **CORS configurado** - Aunque permisivo, está presente
8. **Migraciones automáticas** - Sistema de migraciones implementado
9. **Separación de concerns** - Services, models, api routes bien organizados

---

## 🎯 PLAN DE ACCIÓN RECOMENDADO

### Fase 1: Seguridad (1-2 semanas)
- [ ] Remover credenciales hardcodeadas
- [ ] Implementar validación de entrada en todos los endpoints
- [ ] Agregar rate limiting
- [ ] Validar tamaños de archivo
- [ ] Auditoría de seguridad completa

### Fase 2: Calidad (2-3 semanas)
- [ ] Implementar suite de tests unitarios
- [ ] Implementar tests de integración
- [ ] Configurar CI/CD con tests automáticos
- [ ] Alcanzar 70%+ cobertura de código
- [ ] Agregar linting automático (flake8, black, mypy)

### Fase 3: Refactoring (2-3 semanas)
- [ ] Unificar nomenclatura de campos
- [ ] Refactorizar endpoints monolíticos
- [ ] Implementar context managers para BD
- [ ] Extraer feature engineering común
- [ ] Mejorar manejo de excepciones

### Fase 4: Optimización (1-2 semanas)
- [ ] Implementar caché en backend
- [ ] Optimizar queries de BD con índices
- [ ] Implementar paginación
- [ ] Lazy loading del modelo ML
- [ ] Profiling de performance

### Fase 5: Documentación (1 semana)
- [ ] Completar docstrings en todas las funciones
- [ ] Generar documentación API con Swagger
- [ ] Crear guías de deployment
- [ ] Documentar arquitectura
- [ ] Crear ejemplos de uso

---

## 📚 RECURSOS RECOMENDADOS

### Librerías Útiles
- **pytest** - Framework de testing
- **pytest-cov** - Cobertura de código
- **black** - Formateo automático de código
- **flake8** - Linting de Python
- **mypy** - Type checking
- **slowapi** - Rate limiting para FastAPI
- **python-dotenv** - Manejo de variables de entorno
- **pydantic** - Validación de datos
- **alembic** - Migraciones de BD más robustas
- **redis** - Caché distribuido

### Guías y Best Practices
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/14/orm/session_basics.html)
- [Python Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)

---

## 🏁 CONCLUSIÓN

El proyecto **EduForge** tiene una base sólida y está bien estructurado. Sin embargo, requiere atención en aspectos críticos de **seguridad** y **testing** antes de considerarlo production-ready.

### Puntos Fuertes
- Arquitectura limpia y organizada
- Uso apropiado de tecnologías modernas
- Funcionalidad core bien implementada

### Áreas de Mejora Prioritarias
- Seguridad (credenciales, validación)
- Testing (cobertura, automatización)
- Mantenibilidad (documentación, refactoring)

### Recomendación Final
**NO** desplegar a producción hasta resolver los issues críticos (🔴).  
Una vez resueltos, el sistema estará listo para un ambiente productivo con usuarios reales.

---

**Revisión Completa - EduForge System**  
*Documento generado automáticamente por GitHub Copilot Agent*
