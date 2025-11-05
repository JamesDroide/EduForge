# src/domain/entities/upload.py
"""
Entidad de dominio: Upload
Representa un upload de archivo CSV con predicciones
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Upload:
    """Entidad de dominio para upload de archivos"""
    
    id: Optional[int]
    user_id: int
    filename: str
    original_filename: str
    file_path: str
    upload_date: datetime
    total_students: int
    processed_students: int
    failed_students: int
    high_risk: int
    medium_risk: int
    low_risk: int
    processing_time: float
    status: str
    error_message: Optional[str] = None
    
    def is_successful(self) -> bool:
        """Verifica si el upload fue exitoso"""
        return self.status == 'success'
    
    def is_partial(self) -> bool:
        """Verifica si el upload fue parcial"""
        return self.status == 'partial'
    
    def has_errors(self) -> bool:
        """Verifica si hubo errores"""
        return self.status == 'error' or self.failed_students > 0
    
    def get_success_rate(self) -> float:
        """Calcula el porcentaje de éxito"""
        if self.total_students == 0:
            return 0.0
        return (self.processed_students / self.total_students) * 100
    
    def get_high_risk_percentage(self) -> float:
        """Calcula el porcentaje de estudiantes en alto riesgo"""
        if self.processed_students == 0:
            return 0.0
        return (self.high_risk / self.processed_students) * 100
# src/domain/entities/prediction.py
"""
Entidad de dominio: Prediction
Representa una predicción de deserción estudiantil
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Prediction:
    """Entidad de dominio para predicción de deserción"""
    
    id: Optional[int]
    id_estudiante: int
    nombre: str
    nota_final: float
    conducta: str
    asistencia: float
    inasistencia: float
    tiempo_prediccion: float
    resultado_prediccion: str
    riesgo_desercion: str
    probabilidad_desercion: float
    fecha: Optional[datetime]
    
    def is_high_risk(self) -> bool:
        """Determina si el estudiante está en alto riesgo"""
        return self.riesgo_desercion == "Alto"
    
    def is_medium_risk(self) -> bool:
        """Determina si el estudiante está en riesgo medio"""
        return self.riesgo_desercion == "Medio"
    
    def is_low_risk(self) -> bool:
        """Determina si el estudiante está en bajo riesgo"""
        return self.riesgo_desercion == "Bajo"
    
    def has_low_grade(self) -> bool:
        """Verifica si tiene nota baja (< 11)"""
        return self.nota_final < 11
    
    def has_low_attendance(self) -> bool:
        """Verifica si tiene asistencia baja (< 75%)"""
        return self.asistencia < 75
    
    def has_poor_behavior(self) -> bool:
        """Verifica si tiene conducta deficiente"""
        return self.conducta in ['Mala', 'Regular']
    
    def get_risk_factors(self) -> list[str]:
        """Obtiene lista de factores de riesgo"""
        factors = []
        if self.has_low_grade():
            factors.append('Nota baja')
        if self.has_low_attendance():
            factors.append('Asistencia baja')
        if self.has_poor_behavior():
            factors.append('Conducta deficiente')
        return factors

