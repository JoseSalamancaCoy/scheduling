from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import time
import logging

from models import AgendamientoRequest, AgendamientoResponse
from utils.date_calculator import (
    calcular_fecha_notificacion,
    calcular_fecha_inicio_conteo,
    calcular_fecha_cita_compatible
)
from utils.schedule_validator import validar_compatibilidad_completa
from utils.holiday_handler import filter_holidays_for_employee

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Agendamiento de Citas",
    description="API para calcular fechas de agendamiento según reglas de negocio específicas",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "API de Agendamiento de Citas - v1.0.0"}


@app.post("/agendar-cita", response_model=AgendamientoResponse)
async def agendar_cita(request: AgendamientoRequest):
    """
    Endpoint principal para agendar una cita según las reglas de negocio.

    Calcula:
    - Fecha de notificación al empleado
    - Fecha de inicio del conteo
    - Fecha de la cita
    - Hora de la cita (dentro del traslape horario)
    - Validaciones de compatibilidad
    """
    try:
        # Filtrar feriados según si el empleado trabaja festivos
        dias_feriados_efectivos = filter_holidays_for_employee(
            request.dias_feriados,
            request.empleado.trabaja_festivos
        )

        logger.info(f"Procesando agendamiento para fecha actual: {request.fecha_actual}")

        # 1. Calcular fecha de notificación
        fecha_notificacion = calcular_fecha_notificacion(
            request.fecha_actual,
            request.hora_actual,
            request.empleado.dias_trabajo_empleado,
            dias_feriados_efectivos,
            request.empleado.trabaja_festivos,
            request.empleado.horario_inicio,
            request.empleado.horario_fin
        )

        logger.info(f"Fecha de notificación calculada: {fecha_notificacion}")

        # 2. Calcular fecha de inicio del conteo
        fecha_inicio_conteo = calcular_fecha_inicio_conteo(
            fecha_notificacion,
            request.empleado.dias_trabajo_empleado,
            dias_feriados_efectivos,
            request.empleado.trabaja_festivos
        )

        logger.info(f"Fecha de inicio del conteo: {fecha_inicio_conteo}")

        # 3. Calcular fecha de la cita (considerando compatibilidad)
        try:
            fecha_cita = calcular_fecha_cita_compatible(
                fecha_inicio_conteo,
                request.empleado.dias_trabajo_empleado,
                request.abogado.dias_trabajo_abogado,
                dias_feriados_efectivos,
                request.empleado.trabaja_festivos
            )
            logger.info(f"Fecha de la cita calculada: {fecha_cita}")

            # 4. Validar compatibilidad horaria entre empleado y abogado
            es_compatible, motivo_incompatibilidad, traslape_horario = validar_compatibilidad_completa(
                request.empleado.dias_trabajo_empleado,
                request.abogado.dias_trabajo_abogado,
                request.empleado.horario_inicio,
                request.empleado.horario_fin,
                request.abogado.horario_inicio,
                request.abogado.horario_fin,
                fecha_cita
            )

            if not es_compatible:
                logger.warning(f"Cita no agendable: {motivo_incompatibilidad}")
                return AgendamientoResponse(
                    fecha_actual=request.fecha_actual,
                    fecha_notificacion=fecha_notificacion,
                    fecha_inicio_conteo=fecha_inicio_conteo,
                    fecha_cita=fecha_cita,
                    hora_cita=time(0, 0),  # Hora por defecto cuando no es agendable
                    es_agendable=False,
                    motivo=motivo_incompatibilidad
                )

        except ValueError as ve:
            # No se pudo encontrar fecha compatible
            logger.warning(f"No se pudo encontrar fecha compatible: {str(ve)}")
            from utils.date_calculator import calcular_fecha_cita
            # Calcular fecha basada solo en empleado para propósitos de respuesta
            fecha_cita = calcular_fecha_cita(
                fecha_inicio_conteo,
                request.empleado.dias_trabajo_empleado,
                dias_feriados_efectivos,
                request.empleado.trabaja_festivos
            )

            return AgendamientoResponse(
                fecha_actual=request.fecha_actual,
                fecha_notificacion=fecha_notificacion,
                fecha_inicio_conteo=fecha_inicio_conteo,
                fecha_cita=fecha_cita,
                hora_cita=time(0, 0),  # Hora por defecto cuando no es agendable
                es_agendable=False,
                motivo="No hay días de trabajo comunes entre empleado y abogado"
            )

        # 5. Determinar hora de la cita (inicio del traslape horario)
        hora_cita = traslape_horario[0]

        logger.info(f"Cita agendada exitosamente para {fecha_cita} a las {hora_cita}")

        return AgendamientoResponse(
            fecha_actual=request.fecha_actual,
            fecha_notificacion=fecha_notificacion,
            fecha_inicio_conteo=fecha_inicio_conteo,
            fecha_cita=fecha_cita,
            hora_cita=hora_cita,
            es_agendable=True,
            motivo=None
        )

    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Error interno del servidor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)