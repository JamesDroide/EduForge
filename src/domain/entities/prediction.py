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
    fecha: datetime
    nota_final: float
    asistencia: float
    inasistencia: float
    conducta: str
    resultado_prediccion: str
    riesgo_desercion: str
    probabilidad_desercion: float
    tiempo_prediccion: float
    upload_id: Optional[int] = None

    def is_high_risk(self) -> bool:
        """Verifica si es de alto riesgo"""
        return self.riesgo_desercion == "Alto"

    def is_medium_risk(self) -> bool:
        """Verifica si es de riesgo medio"""
        return self.riesgo_desercion == "Medio"

    def is_low_risk(self) -> bool:
        """Verifica si es de bajo riesgo"""
        return self.riesgo_desercion == "Bajo"

    def needs_intervention(self) -> bool:
        """Verifica si necesita intervención"""
        return self.is_high_risk() or self.is_medium_risk()

    def has_low_attendance(self) -> bool:
        """Verifica si tiene asistencia baja"""
        return self.asistencia < 75.0

    def has_low_grade(self) -> bool:
        """Verifica si tiene nota baja"""
        return self.nota_final < 11.0

    def has_behavior_issues(self) -> bool:
        """Verifica si tiene problemas de conducta"""
        return self.conducta in ["Mala", "Regular"]

    def get_risk_level_value(self) -> int:
        """Obtiene el valor numérico del nivel de riesgo"""
        if self.is_high_risk():
            return 3
        elif self.is_medium_risk():
            return 2
        else:
            return 1

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id": self.id,
            "id_estudiante": self.id_estudiante,
            "nombre": self.nombre,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "nota_final": self.nota_final,
            "asistencia": self.asistencia,
            "inasistencia": self.inasistencia,
            "conducta": self.conducta,
            "resultado_prediccion": self.resultado_prediccion,
            "riesgo_desercion": self.riesgo_desercion,
            "probabilidad_desercion": self.probabilidad_desercion,
            "tiempo_prediccion": self.tiempo_prediccion,
            "upload_id": self.upload_id
        }

    def get_risk_factors(self) -> list:
        """Obtiene los factores de riesgo identificados"""
        factors = []
        if self.has_low_grade():
            factors.append("Nota baja")
        if self.has_low_attendance():
            factors.append("Asistencia baja")
        if self.has_behavior_issues():
            factors.append("Conducta deficiente")
        return factors
