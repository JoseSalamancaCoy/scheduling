from datetime import date, timedelta
from typing import List


def is_dia_habil_empleado(fecha: date, dias_trabajo: List[str], dias_feriados: List[date], trabaja_festivos: bool) -> bool:
    """
    Determina si una fecha es día hábil para el empleado.
    """
    # Convertir fecha a nombre del día en español
    dias_semana = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    nombre_dia = dias_semana[fecha.weekday()]

    # Verificar si el empleado trabaja este día de la semana
    if nombre_dia not in dias_trabajo:
        return False

    # Si es festivo y el empleado no trabaja festivos, no es hábil
    if fecha in dias_feriados and not trabaja_festivos:
        return False

    return True


def calcular_fecha_notificacion(fecha_actual: date, dias_trabajo: List[str],
                               dias_feriados: List[date], trabaja_festivos: bool) -> date:
    """
    Calcula la fecha de notificación según las reglas de negocio.
    """
    # Si hoy es día hábil, la notificación es hoy
    if is_dia_habil_empleado(fecha_actual, dias_trabajo, dias_feriados, trabaja_festivos):
        return fecha_actual

    # Si no es día hábil, buscar el siguiente día hábil
    fecha_candidata = fecha_actual + timedelta(days=1)

    while not is_dia_habil_empleado(fecha_candidata, dias_trabajo, dias_feriados, trabaja_festivos):
        fecha_candidata += timedelta(days=1)

        # Evitar bucle infinito (máximo 30 días de búsqueda)
        if (fecha_candidata - fecha_actual).days > 30:
            raise ValueError("No se pudo encontrar un día hábil en los próximos 30 días")

    return fecha_candidata


def calcular_fecha_inicio_conteo(fecha_notificacion: date, dias_trabajo: List[str],
                                dias_feriados: List[date], trabaja_festivos: bool) -> date:
    """
    Calcula la fecha de inicio del conteo (fecha notificación + 1 día hábil).
    """
    fecha_candidata = fecha_notificacion + timedelta(days=1)

    while not is_dia_habil_empleado(fecha_candidata, dias_trabajo, dias_feriados, trabaja_festivos):
        fecha_candidata += timedelta(days=1)

        # Evitar bucle infinito
        if (fecha_candidata - fecha_notificacion).days > 30:
            raise ValueError("No se pudo encontrar fecha de inicio de conteo en los próximos 30 días")

    return fecha_candidata


def calcular_fecha_cita(fecha_inicio_conteo: date, dias_trabajo: List[str],
                       dias_feriados: List[date], trabaja_festivos: bool) -> date:
    """
    Calcula la fecha de la cita (fecha inicio conteo + 5 días hábiles).
    """
    dias_habiles_contados = 0
    fecha_candidata = fecha_inicio_conteo

    while dias_habiles_contados < 5:
        if is_dia_habil_empleado(fecha_candidata, dias_trabajo, dias_feriados, trabaja_festivos):
            dias_habiles_contados += 1

        if dias_habiles_contados < 5:
            fecha_candidata += timedelta(days=1)

        # Evitar bucle infinito
        if (fecha_candidata - fecha_inicio_conteo).days > 60:
            raise ValueError("No se pudo calcular fecha de cita en los próximos 60 días")

    return fecha_candidata