from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time


class ReunioneOcupada(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time


class AgendaOcupada(BaseModel):
    reuniones: List[ReunioneOcupada]


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
    hora_actual: time
    empleado: EmpleadoConfig
    abogado: AbogadoConfig
    dias_feriados: List[date]
    agenda_empleado: Optional[AgendaOcupada] = None
    agenda_abogado: Optional[AgendaOcupada] = None


class AgendamientoResponse(BaseModel):
    fecha_actual: date
    fecha_notificacion: date
    fecha_inicio_conteo: date
    fecha_cita: date
    hora_cita: time
    es_agendable: bool
    motivo: Optional[str] = None