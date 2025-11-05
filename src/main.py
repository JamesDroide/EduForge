from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from upload import save_uploaded_file, clear_previous_data
from models.predictor import predict_desertion
from services.risk_service import update_latest_predictions, clear_latest_predictions
from services.attendance_service import update_attendance_data, clear_latest_csv_data
from services.upload_history_service import UploadHistoryService
import pandas as pd
import os
import time
from api.routes import dashboard_attendance, dashboard_risk, users, admin_panel, upload_history, db_admin
from config import Base, engine, SessionLocal

# IMPORTANTE: Importar TODOS los modelos ANTES de crear las tablas
from models.user import Usuario

from utils.dependencies import get_current_user_optional

# ==========================================
# CLEAN ARCHITECTURE - Nuevas rutas v2
# ==========================================
from presentation.api.routes.prediction_routes import router as prediction_router
from presentation.api.routes.auth_routes import router as auth_v2_router
from presentation.api.routes.user_routes import router as user_v2_router

# Ejecutar migraciones automáticas al iniciar
from migrations.auto_migrate import run_migrations
run_migrations()

# Crear todas las tablas en la base de datos
# Esto asegura que Usuario, UploadHistory, etc. existan
print("🔄 Creando tablas en la base de datos...")
Base.metadata.create_all(engine)
print("✅ Tablas creadas/verificadas correctamente")

# Verificar que la tabla usuarios existe
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
if 'usuarios' in tables:
    print("✅ Tabla 'usuarios' confirmada en la base de datos")
else:
    print("❌ ERROR: Tabla 'usuarios' NO existe en la base de datos")

# ✅ CORRECCIÓN: Limpiar variables globales al iniciar el servidor
# Esto asegura que no se muestren datos viejos de la BD hasta que se cargue un CSV
clear_latest_predictions()
clear_latest_csv_data()  # También limpiar datos de asistencia
print("🔄 Servidor iniciado - Variables globales limpiadas")

app = FastAPI(
    title="EduForge API - Unified",
    version="2.0.0",
    description="API para predicción de deserción estudiantil con Clean Architecture"
)

# ==========================================
# RUTAS CLEAN ARCHITECTURE (Nuevas v2)
# ==========================================
app.include_router(prediction_router)    # /predictions/*
app.include_router(auth_v2_router)       # /auth-v2/*
app.include_router(user_v2_router)       # /users-v2/*

# ==========================================
# RUTAS LEGACY (Compatibilidad)
# ==========================================
# Incluir routers para los dashboards
# app.include_router(auth.router, prefix="/auth", tags=["Autenticación Legacy"])  # ❌ ELIMINADO - Frontend migrado a /auth-v2
app.include_router(admin_panel.router, tags=["Panel de Administración"])
app.include_router(users.router, prefix="/api", tags=["Gestión de Usuarios Legacy"])
app.include_router(upload_history.router, prefix="/api", tags=["Historial de Cargas"])
app.include_router(db_admin.router, prefix="/api", tags=["Administración de Base de Datos"])
app.include_router(dashboard_attendance.router, prefix="/dashboard_attendance")
app.include_router(dashboard_risk.router, prefix="/dashboard_risk")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Desarrollo local
        "https://eduforge-git-main-jamesdroides-projects.vercel.app",  # Dominio exacto de Vercel
        "https://eduforge-wheat.vercel.app",  # Nuevo dominio de Vercel
        "https://eduforge-production.up.railway.app",  # Railway backend
        "https://*.vercel.app",  # Cualquier subdominio de Vercel
        "https://eduforge.vercel.app"  # Dominio principal si lo tienes
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Ruta raíz con información sobre la API"""
    return {
        "message": "EduForge API - Clean Architecture v2.0",
        "version": "2.0.0",
        "architecture": "Clean Architecture + DDD",
        "status": "✅ Migración completa a Clean Architecture",
        "endpoints": {
            "docs": "/docs",
            "clean_architecture": {
                "predictions": "/predictions/*",
                "auth": "/auth-v2/*",
                "users": "/users-v2/*"
            },
            "functional": {
                "upload": "/upload",
                "predict": "/predict",
                "dashboards": "/dashboard_*/*",
                "admin": "/api/*"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "Clean Architecture",
        "auth": "auth-v2 only"
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: Usuario = Depends(get_current_user_optional)):
    try:
        # Limpiar datos anteriores antes de cargar el nuevo archivo
        clear_previous_data()

        file_path = await save_uploaded_file(file)

        # Guardar en historial si hay usuario autenticado
        upload_id = None
        if current_user:
            db = SessionLocal()
            upload_record = UploadHistoryService.create_upload_record(
                db=db,
                filename=file.filename,
                original_filename=file.filename,
                file_path=file_path,
                user_id=current_user.id
            )
            upload_id = upload_record.id
            db.close()

        print(f"✅ Archivo guardado en: {file_path}")
        return {
            "success": True,
            "message": f"Archivo '{file.filename}' guardado correctamente",
            "filename": file.filename,
            "filepath": file_path,
            "upload_id": upload_id,
            "dashboard_reset": True
        }
    except Exception as e:
        print(f"❌ Error en upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

@app.post("/predict")
async def predict(filename: str, upload_id: int = None):
    start_time = time.time()

    try:
        # Usar la ruta absoluta consistentemente
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
        file_path = os.path.join(upload_dir, filename)

        print(f"Buscando archivo en: {file_path}")

        if not os.path.exists(file_path):
            try:
                available_files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []
            except:
                available_files = ["No se pudo listar el directorio"]

            raise HTTPException(
                status_code=404,
                detail=f"Archivo no encontrado en: {file_path}. Archivos disponibles: {available_files}"
            )

        # Verificar que el archivo sea legible
        try:
            df_test = pd.read_csv(file_path)
            print(f"✅ Archivo leído correctamente. Columnas: {df_test.columns.tolist()}")
            print(f"✅ Número de filas: {len(df_test)}")
            total_students = len(df_test)
        except Exception as e:
            print(f"❌ Error leyendo el archivo: {e}")

            # Actualizar historial con error si existe upload_id
            if upload_id:
                db = SessionLocal()
                UploadHistoryService.update_upload_stats(
                    db=db,
                    upload_id=upload_id,
                    total_students=0,
                    processed_students=0,
                    failed_students=0,
                    high_risk=0,
                    medium_risk=0,
                    low_risk=0,
                    processing_time=time.time() - start_time,
                    status='error',
                    error_message=f"Error leyendo CSV: {str(e)}"
                )
                db.close()

            raise HTTPException(status_code=400, detail=f"Error leyendo el archivo CSV: {str(e)}")

        # Llamar a la función de predicción
        predictions = predict_desertion(file_path)

        # Actualizar los datos para el frontend
        update_latest_predictions(predictions)
        update_attendance_data(predictions)

        # Guardar predicciones en el historial si existe upload_id
        if upload_id:
            db = SessionLocal()

            # Contar estadísticas
            high_risk_count = sum(1 for p in predictions if p.get('riesgo_desercion') == 'Alto')
            medium_risk_count = sum(1 for p in predictions if p.get('riesgo_desercion') == 'Medio')
            low_risk_count = sum(1 for p in predictions if p.get('riesgo_desercion') == 'Bajo')
            processed_count = len(predictions)
            failed_count = total_students - processed_count

            # Guardar cada predicción
            for pred in predictions:
                # Identificar factores de riesgo
                risk_factors = []
                if pred.get('nota_final', 0) < 11:
                    risk_factors.append('Nota baja')
                if pred.get('asistencia', 100) < 75:
                    risk_factors.append('Asistencia baja')
                if pred.get('conducta') in ['Mala', 'Regular']:
                    risk_factors.append('Conducta deficiente')

                UploadHistoryService.add_prediction_to_upload(
                    db=db,
                    upload_id=upload_id,
                    estudiante_id=pred.get('id_estudiante', 0),
                    nombre=pred.get('nombre', 'Sin nombre'),
                    nota_final=pred.get('nota_final', 0),
                    conducta=pred.get('conducta', ''),
                    asistencia=pred.get('asistencia', 0),
                    inasistencia=pred.get('inasistencia', 0),
                    resultado_prediccion=pred.get('resultado_prediccion', '0'),
                    riesgo_desercion=pred.get('riesgo_desercion', 'Bajo'),
                    probabilidad_desercion=pred.get('probabilidad_desercion', 0.0),
                    tiempo_prediccion=pred.get('tiempo_prediccion', 0.0),
                    risk_factors={'factors': risk_factors} if risk_factors else None
                )

            # Actualizar estadísticas del upload
            processing_time = time.time() - start_time
            UploadHistoryService.update_upload_stats(
                db=db,
                upload_id=upload_id,
                total_students=total_students,
                processed_students=processed_count,
                failed_students=failed_count,
                high_risk=high_risk_count,
                medium_risk=medium_risk_count,
                low_risk=low_risk_count,
                processing_time=processing_time,
                status='success' if failed_count == 0 else 'partial'
            )

            db.close()
            print(f"✅ Historial actualizado: {processed_count} predicciones guardadas")

        return {"predictions": predictions}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error general en /predict: {e}")

        # Actualizar historial con error si existe upload_id
        if upload_id:
            db = SessionLocal()
            UploadHistoryService.update_upload_stats(
                db=db,
                upload_id=upload_id,
                total_students=0,
                processed_students=0,
                failed_students=0,
                high_risk=0,
                medium_risk=0,
                low_risk=0,
                processing_time=time.time() - start_time,
                status='error',
                error_message=str(e)
            )
            db.close()

        raise HTTPException(status_code=400, detail=f"Error procesando el archivo: {str(e)}")
