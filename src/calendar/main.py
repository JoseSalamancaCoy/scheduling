from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from typing import Annotated

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import AgendaResponse, ConfiguracionResponse
from services.agenda_service import agenda_service
from services.configuracion_service import configuracion_service


app = FastAPI(
    title="API de Consulta de Agendas",
    description="API REST para consultar agendas de abogados y empleados",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "API de Consulta de Agendas - v1.0.0"}


@app.get("/abogado/agenda", response_model=AgendaResponse)
async def get_agenda_abogado(
    fecha_inicio: Annotated[datetime, Query(description="Fecha y hora de inicio del rango (formato ISO 8601)")],
    fecha_fin: Annotated[datetime, Query(description="Fecha y hora de fin del rango (formato ISO 8601)")]
):
    """
    Obtiene la agenda del abogado en el rango de fechas especificado.

    Retorna una lista de eventos/reuniones del abogado en el rango solicitado.
    Solo incluye eventos en días laborales según la configuración.
    """
    try:
        if fecha_inicio >= fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="fecha_inicio debe ser anterior a fecha_fin"
            )

        agenda = agenda_service.get_agenda_abogado(fecha_inicio, fecha_fin)
        return agenda

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.get("/empleado/agenda", response_model=AgendaResponse)
async def get_agenda_empleado(
    fecha_inicio: Annotated[datetime, Query(description="Fecha y hora de inicio del rango (formato ISO 8601)")],
    fecha_fin: Annotated[datetime, Query(description="Fecha y hora de fin del rango (formato ISO 8601)")]
):
    """
    Obtiene la agenda del empleado en el rango de fechas especificado.

    Retorna una lista de eventos/reuniones del empleado en el rango solicitado.
    Solo incluye eventos en días laborales según la configuración.
    """
    try:
        if fecha_inicio >= fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="fecha_inicio debe ser anterior a fecha_fin"
            )

        agenda = agenda_service.get_agenda_empleado(fecha_inicio, fecha_fin)
        return agenda

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.get("/configuracion/horario-laboral", response_model=ConfiguracionResponse)
async def get_configuracion_horario_laboral():
    """
    Obtiene la configuración completa de días y horarios laborales.

    Retorna la configuración de qué días son laborales y los horarios
    de trabajo para cada día de la semana.
    """
    try:
        configuracion = configuracion_service.load_configuracion()
        return configuracion

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/configuracion/reload")
async def reload_configuracion():
    """
    Recarga la configuración laboral desde el archivo.

    Útil para actualizar la configuración sin reiniciar el servidor.
    """
    try:
        configuracion_service.clear_cache()
        configuracion = configuracion_service.load_configuracion()
        return {"message": "Configuración recargada exitosamente", "configuracion": configuracion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recargar configuración: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)