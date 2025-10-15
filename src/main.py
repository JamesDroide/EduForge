from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from upload import save_uploaded_file, clear_previous_data
from models.predictor import predict_desertion
from services.risk_service import update_latest_predictions, clear_latest_predictions
from services.attendance_service import update_attendance_data, clear_latest_csv_data  # Importar clear
from fastapi.responses import JSONResponse
import pandas as pd
import os
from api.routes import dashboard_attendance, dashboard_risk, auth, users, admin_panel
from config import Base, engine, SessionLocal
from models import ResultadoPrediccion

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
async def upload_file(file: UploadFile = File(...)):
    try:
        # Limpiar datos anteriores antes de cargar el nuevo archivo
        clear_previous_data()

        file_path = await save_uploaded_file(file)
        print(f"✅ Archivo guardado en: {file_path}")  # Debug para ver la ruta real
        return {
            "success": True,
            "message": f"Archivo '{file.filename}' guardado correctamente",
            "filename": file.filename,
            "filepath": file_path,
            "dashboard_reset": True  # Indicar que el dashboard se reseteo
        }
    except Exception as e:
        print(f"❌ Error en upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

@app.post("/predict")
async def predict(filename: str):
    try:
        # Usar la ruta absoluta consistentemente
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
        file_path = os.path.join(upload_dir, filename)

        print(f"Buscando archivo en: {file_path}")  # Para depuración

        if not os.path.exists(file_path):
            # Listar archivos disponibles para debug
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
            import pandas as pd
            df_test = pd.read_csv(file_path)
            print(f"✅ Archivo leído correctamente. Columnas: {df_test.columns.tolist()}")
            print(f"✅ Número de filas: {len(df_test)}")
        except Exception as e:
            print(f"❌ Error leyendo el archivo: {e}")
            raise HTTPException(status_code=400, detail=f"Error leyendo el archivo CSV: {str(e)}")

        # Llamar a la función de predicción
        predictions = predict_desertion(file_path)

        # ¡NUEVO! Actualizar los datos para el frontend
        update_latest_predictions(predictions)

        # ¡NUEVO! Actualizar los datos de asistencia para el gráfico
        update_attendance_data(predictions)

        return {"predictions": predictions}

    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        print(f"❌ Error general en /predict: {e}")
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

@app.get("/diagnostico-usuarios")
async def diagnostico_usuarios():
    """Endpoint temporal para diagnosticar y crear usuario administrador"""
    from models.user import Usuario
    from utils.security import get_password_hash, verify_password

    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()

        resultado = {
            "total_usuarios": len(usuarios),
            "usuarios": []
        }

        for u in usuarios:
            resultado["usuarios"].append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "rol": u.rol,
                "activo": u.is_active,
                "password_james232_valida": verify_password("james232", u.password_hash)
            })

        # Verificar si existe "administrador"
        admin = db.query(Usuario).filter(Usuario.username == "administrador").first()

        if not admin:
            resultado["accion"] = "Usuario 'administrador' NO existe - Creándolo ahora..."
            nuevo_admin = Usuario(
                username="administrador",
                email="admin@eduforge.com",
                password_hash=get_password_hash("james232"),
                rol="administrador",
                is_active=True
            )
            db.add(nuevo_admin)
            db.commit()
            db.refresh(nuevo_admin)
            resultado["administrador_creado"] = True
            resultado["nuevo_usuario"] = {
                "id": nuevo_admin.id,
                "username": nuevo_admin.username,
                "email": nuevo_admin.email,
                "rol": nuevo_admin.rol,
                "activo": nuevo_admin.is_active
            }
        else:
            resultado["accion"] = "Usuario 'administrador' YA existe"
            resultado["administrador_creado"] = False

            # Verificar y actualizar contraseña si es necesario
            if not verify_password("james232", admin.password_hash):
                resultado["password_actualizada"] = True
                resultado["mensaje_password"] = "Contraseña incorrecta - ACTUALIZADA a 'james232'"
                admin.password_hash = get_password_hash("james232")
                db.commit()
            else:
                resultado["password_actualizada"] = False
                resultado["mensaje_password"] = "Contraseña 'james232' es CORRECTA"

            # Verificar que sea administrador
            if admin.rol != "administrador":
                resultado["rol_actualizado"] = True
                resultado["mensaje_rol"] = f"Rol era '{admin.rol}' - ACTUALIZADO a 'administrador'"
                admin.rol = "administrador"
                db.commit()
            else:
                resultado["rol_actualizado"] = False
                resultado["mensaje_rol"] = "Rol es 'administrador' - CORRECTO"

            # Verificar que esté activo
            if not admin.is_active:
                resultado["activado"] = True
                resultado["mensaje_activo"] = "Usuario estaba inactivo - ACTIVADO"
                admin.is_active = True
                db.commit()
            else:
                resultado["activado"] = False
                resultado["mensaje_activo"] = "Usuario está activo - CORRECTO"

        resultado["credenciales"] = {
            "url": "http://localhost:3000/admin-panel/login",
            "username": "administrador",
            "password": "james232",
            "codigo_acceso": "EDUFORGE2025"
        }

        resultado["instrucciones"] = "Usa las credenciales de arriba para acceder al panel de administración"

        return resultado
    finally:
        db.close()
