from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from models.upload_history import UploadHistory, UploadPrediction
from models.user import Usuario
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json


class UploadHistoryService:
    """Servicio para gestionar el historial de cargas CSV"""

    @staticmethod
    def create_upload_record(
        db: Session,
        filename: str,
        original_filename: str,
        file_path: str,
        user_id: int
    ) -> UploadHistory:
        """Crear un registro de carga nuevo"""
        upload = UploadHistory(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            user_id=user_id,
            status='processing'
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    @staticmethod
    def update_upload_stats(
        db: Session,
        upload_id: int,
        total_students: int,
        processed_students: int,
        failed_students: int,
        high_risk: int,
        medium_risk: int,
        low_risk: int,
        processing_time: float,
        status: str = 'success',
        error_message: Optional[str] = None
    ):
        """Actualizar las estadísticas de una carga"""
        upload = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
        if upload:
            upload.total_students = total_students
            upload.processed_students = processed_students
            upload.failed_students = failed_students
            upload.high_risk_count = high_risk
            upload.medium_risk_count = medium_risk
            upload.low_risk_count = low_risk

            # Calcular porcentajes
            if processed_students > 0:
                upload.high_risk_percentage = (high_risk / processed_students) * 100
                upload.medium_risk_percentage = (medium_risk / processed_students) * 100
                upload.low_risk_percentage = (low_risk / processed_students) * 100

            upload.processing_time = processing_time
            upload.status = status
            upload.error_message = error_message

            db.commit()
            db.refresh(upload)
        return upload

    @staticmethod
    def add_prediction_to_upload(
        db: Session,
        upload_id: int,
        estudiante_id: int,
        nombre: str,
        nota_final: float,
        conducta: str,
        asistencia: float,
        inasistencia: float,
        resultado_prediccion: str,
        riesgo_desercion: str,
        probabilidad_desercion: float,
        tiempo_prediccion: float,
        risk_factors: Optional[Dict] = None
    ):
        """Agregar una predicción individual al historial"""
        prediction = UploadPrediction(
            upload_history_id=upload_id,
            estudiante_id=estudiante_id,
            nombre=nombre,
            nota_final=nota_final,
            conducta=conducta,
            asistencia=asistencia,
            inasistencia=inasistencia,
            resultado_prediccion=resultado_prediccion,
            riesgo_desercion=riesgo_desercion,
            probabilidad_desercion=probabilidad_desercion,
            tiempo_prediccion=tiempo_prediccion,
            risk_factors=json.dumps(risk_factors) if risk_factors else None
        )
        db.add(prediction)
        db.commit()
        return prediction

    @staticmethod
    def get_all_uploads(
        db: Session,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UploadHistory]:
        """Obtener lista de todas las cargas con filtros"""
        query = db.query(UploadHistory)

        # Filtrar por usuario si no es admin
        if not is_admin and user_id:
            query = query.filter(UploadHistory.user_id == user_id)

        # Filtrar por rango de fechas
        if start_date:
            query = query.filter(UploadHistory.upload_date >= start_date)
        if end_date:
            query = query.filter(UploadHistory.upload_date <= end_date)

        # Búsqueda por nombre de archivo
        if search_query:
            query = query.filter(
                or_(
                    UploadHistory.filename.ilike(f"%{search_query}%"),
                    UploadHistory.original_filename.ilike(f"%{search_query}%")
                )
            )

        # Ordenar por fecha más reciente
        query = query.order_by(desc(UploadHistory.upload_date))

        # Paginación
        uploads = query.offset(skip).limit(limit).all()

        return uploads

    @staticmethod
    def get_upload_by_id(db: Session, upload_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> Optional[UploadHistory]:
        """Obtener una carga específica por ID"""
        query = db.query(UploadHistory).filter(UploadHistory.id == upload_id)

        # Si no es admin, verificar que sea dueño de la carga
        if not is_admin and user_id:
            query = query.filter(UploadHistory.user_id == user_id)

        return query.first()

    @staticmethod
    def get_predictions_by_upload(
        db: Session,
        upload_id: int,
        skip: int = 0,
        limit: int = 1000
    ) -> List[UploadPrediction]:
        """Obtener todas las predicciones de una carga específica"""
        predictions = db.query(UploadPrediction).filter(
            UploadPrediction.upload_history_id == upload_id
        ).offset(skip).limit(limit).all()

        return predictions

    @staticmethod
    def delete_upload(db: Session, upload_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> bool:
        """Eliminar una carga y todas sus predicciones"""
        query = db.query(UploadHistory).filter(UploadHistory.id == upload_id)

        # Si no es admin, verificar que sea dueño
        if not is_admin and user_id:
            query = query.filter(UploadHistory.user_id == user_id)

        upload = query.first()
        if upload:
            db.delete(upload)
            db.commit()
            return True
        return False

    @staticmethod
    def update_notes(db: Session, upload_id: int, notes: str, user_id: Optional[int] = None, is_admin: bool = False) -> Optional[UploadHistory]:
        """Actualizar las notas/observaciones de una carga"""
        query = db.query(UploadHistory).filter(UploadHistory.id == upload_id)

        if not is_admin and user_id:
            query = query.filter(UploadHistory.user_id == user_id)

        upload = query.first()
        if upload:
            upload.notes = notes
            db.commit()
            db.refresh(upload)
        return upload

    @staticmethod
    def get_statistics_summary(db: Session, user_id: Optional[int] = None, is_admin: bool = False) -> Dict:
        """Obtener resumen de estadísticas generales"""
        query = db.query(UploadHistory)

        if not is_admin and user_id:
            query = query.filter(UploadHistory.user_id == user_id)

        uploads = query.all()

        total_uploads = len(uploads)
        total_students = sum(u.total_students for u in uploads)
        total_processed = sum(u.processed_students for u in uploads)
        total_high_risk = sum(u.high_risk_count for u in uploads)
        total_medium_risk = sum(u.medium_risk_count for u in uploads)
        total_low_risk = sum(u.low_risk_count for u in uploads)

        # Últimas 30 días
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_uploads = [u for u in uploads if u.upload_date >= thirty_days_ago]

        return {
            'total_uploads': total_uploads,
            'total_students_processed': total_processed,
            'total_students_loaded': total_students,
            'total_high_risk': total_high_risk,
            'total_medium_risk': total_medium_risk,
            'total_low_risk': total_low_risk,
            'uploads_last_30_days': len(recent_uploads),
            'average_processing_time': sum(u.processing_time for u in uploads if u.processing_time) / total_uploads if total_uploads > 0 else 0
        }

    @staticmethod
    def compare_uploads(db: Session, upload_ids: List[int]) -> Dict:
        """Comparar estadísticas entre múltiples cargas"""
        uploads = db.query(UploadHistory).filter(UploadHistory.id.in_(upload_ids)).all()

        comparison = []
        for upload in uploads:
            comparison.append({
                'id': upload.id,
                'filename': upload.original_filename,
                'upload_date': upload.upload_date.isoformat(),
                'total_students': upload.total_students,
                'high_risk_percentage': round(upload.high_risk_percentage, 2),
                'medium_risk_percentage': round(upload.medium_risk_percentage, 2),
                'low_risk_percentage': round(upload.low_risk_percentage, 2),
                'high_risk_count': upload.high_risk_count,
                'medium_risk_count': upload.medium_risk_count,
                'low_risk_count': upload.low_risk_count
            })

        return {'uploads': comparison}

