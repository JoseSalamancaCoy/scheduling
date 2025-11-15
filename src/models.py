from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time


class EmpleadoConfig(BaseModel):
    dias_trabajo_empleado: List[str]
    horario_inicio: time
    horario_fin: time
    trabaja_festivos: bool


class AbogadoConfig(BaseModel):
    dias_trabajo_abogado: List[str]
    dias_no_trabajo_abogado: List[str]
    horario_inicio: time
    horario_fin: time


class AgendamientoRequest(BaseModel):
    fecha_actual: date
    empleado: EmpleadoConfig
    abogado: AbogadoConfig
    dias_feriados: List[date]


class AgendamientoResponse(BaseModel):
    fecha_actual: date
    fecha_notificacion: date
    fecha_inicio_conteo: date
    fecha_cita: date
    hora_cita: time
    es_agendable: bool
    motivo: Optional[str] = None