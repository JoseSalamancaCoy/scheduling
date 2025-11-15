from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class EventoResponse(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime


class AgendaResponse(BaseModel):
    eventos: List[EventoResponse]


class HorarioDia(BaseModel):
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None


class ConfiguracionResponse(BaseModel):
    dias_laborales: Dict[str, bool]
    horarios_por_dia: Dict[str, Optional[HorarioDia]]