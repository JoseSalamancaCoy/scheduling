from datetime import date, timedelta, time
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


def calcular_fecha_notificacion(fecha_actual: date, hora_actual: time, dias_trabajo: List[str],
                               dias_feriados: List[date], trabaja_festivos: bool,
                               horario_inicio: time, horario_fin: time) -> date:
    """
    Calcula la fecha de notificación según las reglas de negocio.
    Considera tanto el día hábil como el horario de trabajo del empleado.
    """
    # Si hoy es día hábil y estamos dentro del horario laboral, la notificación es hoy
    if (is_dia_habil_empleado(fecha_actual, dias_trabajo, dias_feriados, trabaja_festivos) and
        horario_inicio <= hora_actual <= horario_fin):
        return fecha_actual

    # Si no es día hábil o ya pasó el horario laboral, buscar el siguiente día hábil
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
    Calcula la fecha de la cita (5 días hábiles después de fecha inicio conteo).
    """
    dias_habiles_contados = 0
    fecha_candidata = fecha_inicio_conteo + timedelta(days=1)  # Empezar el día después

    while dias_habiles_contados < 5:
        if is_dia_habil_empleado(fecha_candidata, dias_trabajo, dias_feriados, trabaja_festivos):
            dias_habiles_contados += 1
            if dias_habiles_contados == 5:
                break

        fecha_candidata += timedelta(days=1)

        # Evitar bucle infinito
        if (fecha_candidata - fecha_inicio_conteo).days > 60:
            raise ValueError("No se pudo calcular fecha de cita en los próximos 60 días")

    return fecha_candidata


def find_next_compatible_date(fecha_inicio: date, dias_trabajo_empleado: List[str],
                             dias_trabajo_abogado: List[str], dias_feriados: List[date],
                             trabaja_festivos: bool, max_days: int = 30) -> date:
    """
    Encuentra la siguiente fecha en que tanto el empleado como el abogado pueden trabajar.
    """
    dias_semana = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    fecha_candidata = fecha_inicio
    dias_buscados = 0

    while dias_buscados < max_days:
        dia_nombre = dias_semana[fecha_candidata.weekday()]

        # Verificar si el empleado puede trabajar este día
        empleado_puede = is_dia_habil_empleado(fecha_candidata, dias_trabajo_empleado, dias_feriados, trabaja_festivos)

        # Verificar si el abogado puede trabajar este día
        abogado_puede = dia_nombre in dias_trabajo_abogado

        if empleado_puede and abogado_puede:
            return fecha_candidata

        fecha_candidata += timedelta(days=1)
        dias_buscados += 1

    raise ValueError(f"No se encontró fecha compatible en {max_days} días")


def calcular_fecha_cita_compatible(fecha_inicio_conteo: date, dias_trabajo_empleado: List[str],
                                  dias_trabajo_abogado: List[str], dias_feriados: List[date],
                                  trabaja_festivos: bool) -> date:
    """
    Calcula la fecha de la cita considerando compatibilidad entre empleado y abogado.
    Primero cuenta 5 días hábiles del empleado, luego busca una fecha compatible si es necesario.
    """
    # Primero calcular la fecha ideal basada en el empleado
    fecha_ideal = calcular_fecha_cita(fecha_inicio_conteo, dias_trabajo_empleado, dias_feriados, trabaja_festivos)

    # Verificar si el abogado puede trabajar en esa fecha
    dias_semana = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    dia_ideal = dias_semana[fecha_ideal.weekday()]

    # Si el abogado también puede trabajar esa fecha, usar esa fecha
    if dia_ideal in dias_trabajo_abogado:
        return fecha_ideal

    # Si no, buscar la siguiente fecha compatible
    return find_next_compatible_date(fecha_ideal, dias_trabajo_empleado, dias_trabajo_abogado,
                                   dias_feriados, trabaja_festivos)