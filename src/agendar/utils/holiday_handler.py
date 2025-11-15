from datetime import date, timedelta
from typing import List


def is_holiday(fecha: date, dias_feriados: List[date]) -> bool:
    """
    Verifica si una fecha es un día feriado.
    """
    return fecha in dias_feriados


def get_next_non_holiday(fecha_inicio: date, dias_feriados: List[date], max_days: int = 30) -> date:
    """
    Encuentra la siguiente fecha que no sea feriado.
    """
    fecha_candidata = fecha_inicio
    dias_buscados = 0

    while is_holiday(fecha_candidata, dias_feriados) and dias_buscados < max_days:
        fecha_candidata += timedelta(days=1)
        dias_buscados += 1

    if dias_buscados >= max_days:
        raise ValueError(f"No se encontró fecha no feriada en {max_days} días")

    return fecha_candidata


def filter_holidays_for_employee(dias_feriados: List[date], trabaja_festivos: bool) -> List[date]:
    """
    Filtra los días feriados según si el empleado trabaja festivos o no.

    Returns:
        List[date]: Lista de fechas que deben considerarse como días no hábiles para el empleado
    """
    if trabaja_festivos:
        return []  # Si trabaja festivos, ningún feriado cuenta como día no hábil
    else:
        return dias_feriados  # Si no trabaja festivos, todos los feriados son días no hábiles


def count_holidays_in_period(fecha_inicio: date, fecha_fin: date, dias_feriados: List[date]) -> int:
    """
    Cuenta cuántos días feriados hay en un período específico.
    """
    contador = 0
    for feriado in dias_feriados:
        if fecha_inicio <= feriado <= fecha_fin:
            contador += 1
    return contador


def get_holidays_in_period(fecha_inicio: date, fecha_fin: date, dias_feriados: List[date]) -> List[date]:
    """
    Obtiene todos los días feriados en un período específico.
    """
    feriados_en_periodo = []
    for feriado in dias_feriados:
        if fecha_inicio <= feriado <= fecha_fin:
            feriados_en_periodo.append(feriado)

    return sorted(feriados_en_periodo)