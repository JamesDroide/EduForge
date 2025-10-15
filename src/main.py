from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from upload import save_uploaded_file, clear_previous_data
from models.predictor import predict_desertion
from services.risk_service import update_latest_predictions, clear_latest_predictions
from services.attendance_service import update_attendance_data, clear_latest_csv_data
from services.upload_history_service import UploadHistoryService
from fastapi.responses import JSONResponse
import pandas as pd
import os
import time
from api.routes import dashboard_attendance, dashboard_risk, auth, users, admin_panel, upload_history, db_admin
from config import Base, engine, SessionLocal
from models import ResultadoPrediccion
from utils.dependencies import get_current_user_optional
from models.user import Usuario

# Ejecutar migraciones automáticas al iniciar
from migrations.auto_migrate import run_migrations
run_migrations()

# Crear todas las tablas en la base de datos
Base.metadata.create_all(engine)

# ✅ CORRECCIÓN: Limpiar variables globales al iniciar el servidor
# Esto asegura que no se muestren datos viejos de la BD hasta que se cargue un CSV
clear_latest_predictions()
clear_latest_csv_data()  # También limpiar datos de asistencia
print("🔄 Servidor iniciado - Variables globales limpiadas")

app = FastAPI(title="Eduforge API", version="1.0.0")

# Incluir routers para los dashboards
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(admin_panel.router, tags=["Panel de Administración"])
app.include_router(users.router, prefix="/api", tags=["Gestión de Usuarios"])
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
        "message": "API EduForge funcionando correctamente",
        "version": "1.0.0",
        "endpoints": ["/docs", "/dashboard_attendance", "/dashboard_risk", "/auth"]
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

@app.get("/api/reporte-general")
async def reporte_general():
    try:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "student_data.csv"))
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="Archivo student_data.csv no encontrado.")
        df = pd.read_csv(csv_path)
        resumen = df.describe(include='all').fillna('').to_dict()
        return JSONResponse(content=resumen)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el reporte general: {str(e)}")

@app.get("/api/resultados-prediccion")
async def get_resultados_prediccion():
    try:
        session = SessionLocal()
        resultados = session.query(ResultadoPrediccion).all()
        session.close()
        resultados_dict = [
            {
                "id": r.id,
                "id_estudiante": r.id_estudiante,
                "nombre": r.nombre,
                "nota": r.nota_final,  # Mantener 'nota' por compatibilidad con frontend
                "nota_final": r.nota_final,
                "conducta": r.conducta,
                "asistencia": r.asistencia,
                "inasistencia": r.inasistencia,
                "tiempo_prediccion": r.tiempo_prediccion,
                "resultado_prediccion": r.resultado_prediccion,
                "riesgo_desercion": r.riesgo_desercion,
                "probabilidad_desercion": r.probabilidad_desercion,
                "fecha": r.fecha.strftime('%Y-%m-%d %H:%M:%S') if r.fecha else None
            }
            for r in resultados
        ]
        return JSONResponse(content={"resultados": resultados_dict})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resultados: {str(e)}")

@app.get("/api/estadisticas-generales")
async def get_estadisticas_generales():
    """
    Endpoint para obtener estadísticas generales de las predicciones
    """
    try:
        session = SessionLocal()
        resultados = session.query(ResultadoPrediccion).all()

        if not resultados:
            return JSONResponse(content={
                "total_estudiantes": 0,
                "estudiantes_riesgo_alto": 0,
                "estudiantes_riesgo_bajo": 0,
                "porcentaje_riesgo": 0,
                "promedio_notas": 0,
                "promedio_asistencia": 0
            })

        total_estudiantes = len(resultados)
        riesgo_alto = sum(1 for r in resultados if int(r.resultado_prediccion) == 1)
        riesgo_bajo = total_estudiantes - riesgo_alto
        porcentaje_riesgo = (riesgo_alto / total_estudiantes) * 100
        promedio_notas = sum(r.nota for r in resultados) / total_estudiantes
        promedio_asistencia = sum(r.asistencia for r in resultados) / total_estudiantes

        session.close()

        return JSONResponse(content={
            "total_estudiantes": total_estudiantes,
            "estudiantes_riesgo_alto": riesgo_alto,
            "estudiantes_riesgo_bajo": riesgo_bajo,
            "porcentaje_riesgo": round(porcentaje_riesgo, 2),
            "promedio_notas": round(promedio_notas, 2),
            "promedio_asistencia": round(promedio_asistencia, 2)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@app.get("/api/estudiantes-riesgo")
async def get_estudiantes_riesgo():
    """
    Endpoint para obtener la lista de estudiantes en riesgo alto
    """
    try:
        session = SessionLocal()
        resultados = session.query(ResultadoPrediccion).filter(
            ResultadoPrediccion.resultado_prediccion == "1"
        ).all()

        estudiantes_riesgo = []
        for resultado in resultados:
            estudiantes_riesgo.append({
                "id_estudiante": resultado.id_estudiante,
                "nota": resultado.nota,
                "asistencia": resultado.asistencia,
                "conducta": resultado.conducta,
                "fecha": resultado.fecha.strftime('%Y-%m-%d') if resultado.fecha else None,
                "probabilidad_desercion": "Alto"
            })

        session.close()
        return JSONResponse(content={"estudiantes": estudiantes_riesgo})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estudiantes en riesgo: {str(e)}")

@app.delete("/api/limpiar-datos")
async def limpiar_datos():
    """
    Endpoint para limpiar todos los datos de predicciones cargados
    """
    try:
        session = SessionLocal()
        # Eliminar todos los registros de predicciones
        deleted_count = session.query(ResultadoPrediccion).delete()
        session.commit()
        session.close()

        print(f"✅ Se eliminaron {deleted_count} registros de predicciones")

        return JSONResponse(content={
            "success": True,
            "message": f"Se eliminaron {deleted_count} registros exitosamente",
            "registros_eliminados": deleted_count
        })
    except Exception as e:
        print(f"❌ Error al limpiar datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al limpiar datos: {str(e)}")

@app.delete("/clear-dashboard")
async def clear_dashboard():
    """
    Endpoint para limpiar manualmente todos los datos del dashboard
    """
    try:
        clear_previous_data()
        return {
            "success": True,
            "message": "Dashboard limpiado correctamente"
        }
    except Exception as e:
        print(f"❌ Error limpiando dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al limpiar dashboard: {str(e)}")

@app.get("/dashboard-status")
async def get_dashboard_status():
    """
    Endpoint para verificar si hay datos en el dashboard
    """
    try:
        db = SessionLocal()
        count = db.query(ResultadoPrediccion).count()
        db.close()

        return {
            "has_data": count > 0,
            "total_records": count
        }
    except Exception as e:
        print(f"❌ Error obteniendo estado del dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estado del dashboard: {str(e)}")

# Endpoint de diagnóstico eliminado por seguridad
# Las credenciales del superadmin se gestionan mediante variables de entorno
# Para crear/actualizar el usuario superadmin, ejecuta:
# python src/migrations/create_admin_panel_user.py
