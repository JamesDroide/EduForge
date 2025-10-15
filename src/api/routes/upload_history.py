from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from utils.dependencies import get_db, get_current_user
from services.upload_history_service import UploadHistoryService
from models.user import Usuario, RolEnum

router = APIRouter()


# Schemas
class UploadHistoryResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    upload_date: str
    user_id: int
    username: Optional[str]
    user_full_name: Optional[str]
    total_students: int
    processed_students: int
    failed_students: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    high_risk_percentage: float
    medium_risk_percentage: float
    low_risk_percentage: float
    status: str
    error_message: Optional[str]
    notes: Optional[str]
    processing_time: Optional[float]


class PredictionResponse(BaseModel):
    id: int
    upload_history_id: int
    estudiante_id: int
    nombre: Optional[str]
    nota_final: float
    conducta: Optional[str]
    asistencia: float
    inasistencia: Optional[float]
    resultado_prediccion: str
    riesgo_desercion: Optional[str]
    probabilidad_desercion: Optional[float]
    risk_factors: Optional[str]
    tiempo_prediccion: float
    fecha_prediccion: Optional[str]


class UpdateNotesRequest(BaseModel):
    notes: str


@router.get("/history", response_model=List[UploadHistoryResponse])
async def get_upload_history(
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Buscar por nombre de archivo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener historial de cargas CSV
    - Admins ven todas las cargas
    - Docentes solo ven sus propias cargas
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    # Convertir fechas si se proporcionan
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    uploads = UploadHistoryService.get_all_uploads(
        db=db,
        user_id=current_user.id,
        is_admin=is_admin,
        start_date=start_dt,
        end_date=end_dt,
        search_query=search,
        skip=skip,
        limit=limit
    )

    return [upload.to_dict() for upload in uploads]


@router.get("/history/{upload_id}", response_model=UploadHistoryResponse)
async def get_upload_detail(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalle de una carga específica
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    upload = UploadHistoryService.get_upload_by_id(
        db=db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not upload:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    return upload.to_dict()


@router.get("/history/{upload_id}/predictions", response_model=List[PredictionResponse])
async def get_upload_predictions(
    upload_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener todas las predicciones de una carga específica
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    # Verificar que el usuario tenga acceso a esta carga
    upload = UploadHistoryService.get_upload_by_id(
        db=db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not upload:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    predictions = UploadHistoryService.get_predictions_by_upload(
        db=db,
        upload_id=upload_id,
        skip=skip,
        limit=limit
    )

    return [pred.to_dict() for pred in predictions]


@router.delete("/history/{upload_id}")
async def delete_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar una carga del historial
    - Admins pueden eliminar cualquier carga
    - Docentes solo sus propias cargas
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    deleted = UploadHistoryService.delete_upload(
        db=db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Carga no encontrada o sin permisos")

    return {"message": "Carga eliminada exitosamente", "upload_id": upload_id}


@router.put("/history/{upload_id}/notes")
async def update_upload_notes(
    upload_id: int,
    request: UpdateNotesRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar las notas/observaciones de una carga
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    upload = UploadHistoryService.update_notes(
        db=db,
        upload_id=upload_id,
        notes=request.notes,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not upload:
        raise HTTPException(status_code=404, detail="Carga no encontrada o sin permisos")

    return {"message": "Notas actualizadas exitosamente", "upload": upload.to_dict()}


@router.get("/history/statistics/summary")
async def get_statistics_summary(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener resumen de estadísticas del historial
    """
    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    stats = UploadHistoryService.get_statistics_summary(
        db=db,
        user_id=current_user.id,
        is_admin=is_admin
    )

    return stats


@router.post("/history/compare")
async def compare_uploads(
    upload_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Comparar estadísticas entre múltiples cargas
    """
    if len(upload_ids) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 cargas para comparar")

    if len(upload_ids) > 10:
        raise HTTPException(status_code=400, detail="Máximo 10 cargas para comparar")

    comparison = UploadHistoryService.compare_uploads(db=db, upload_ids=upload_ids)

    return comparison


@router.get("/history/{upload_id}/download")
async def download_original_csv(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Descargar el archivo CSV original
    """
    from fastapi.responses import FileResponse
    import os

    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    upload = UploadHistoryService.get_upload_by_id(
        db=db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not upload:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    if not os.path.exists(upload.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(
        path=upload.file_path,
        filename=upload.original_filename,
        media_type='text/csv'
    )


@router.get("/history/{upload_id}/export")
async def export_predictions(
    upload_id: int,
    format: str = Query("csv", regex="^(csv|excel)$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Exportar las predicciones en formato CSV o Excel
    """
    from fastapi.responses import StreamingResponse
    import pandas as pd
    import io

    is_admin = current_user.rol == RolEnum.ADMINISTRADOR

    # Verificar acceso
    upload = UploadHistoryService.get_upload_by_id(
        db=db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not upload:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    # Obtener predicciones
    predictions = UploadHistoryService.get_predictions_by_upload(
        db=db,
        upload_id=upload_id,
        limit=10000
    )

    # Convertir a DataFrame
    data = [pred.to_dict() for pred in predictions]
    df = pd.DataFrame(data)

    # Eliminar campos innecesarios
    if 'risk_factors' in df.columns:
        df = df.drop('risk_factors', axis=1)

    # Exportar según formato
    if format == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Predicciones')
        output.seek(0)

        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename=predicciones_{upload_id}.xlsx'}
        )
    else:  # CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename=predicciones_{upload_id}.csv'}
        )

