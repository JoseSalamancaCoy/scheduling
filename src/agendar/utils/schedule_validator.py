from datetime import date, time
from typing import List, Tuple, Optional


def verificar_dias_comunes(dias_trabajo_empleado: List[str], dias_trabajo_abogado: List[str]) -> bool:
    """
    Verifica si empleado y abogado tienen días de trabajo en común.
    """
    return bool(set(dias_trabajo_empleado) & set(dias_trabajo_abogado))


def calcular_traslape_horario(horario_empleado_inicio: time, horario_empleado_fin: time,
                            horario_abogado_inicio: time, horario_abogado_fin: time) -> Optional[Tuple[time, time]]:
    """
    Calcula el traslape horario entre empleado y abogado.
    Retorna None si no hay traslape, o tupla (inicio, fin) del traslape.
    """
    # Convertir a minutos para facilitar cálculos
    emp_inicio_min = horario_empleado_inicio.hour * 60 + horario_empleado_inicio.minute
    emp_fin_min = horario_empleado_fin.hour * 60 + horario_empleado_fin.minute
    abog_inicio_min = horario_abogado_inicio.hour * 60 + horario_abogado_inicio.minute
    abog_fin_min = horario_abogado_fin.hour * 60 + horario_abogado_fin.minute

    # Calcular inicio y fin del traslape
    inicio_traslape_min = max(emp_inicio_min, abog_inicio_min)
    fin_traslape_min = min(emp_fin_min, abog_fin_min)

    # Si no hay traslape (inicio >= fin)
    if inicio_traslape_min >= fin_traslape_min:
        return None

    # Convertir de vuelta a time
    inicio_traslape = time(inicio_traslape_min // 60, inicio_traslape_min % 60)
    fin_traslape = time(fin_traslape_min // 60, fin_traslape_min % 60)

    return (inicio_traslape, fin_traslape)


def excluir_horario_almuerzo(traslape: Tuple[time, time],
                           almuerzo_inicio: time = time(12, 0),
                           almuerzo_fin: time = time(14, 0)) -> List[Tuple[time, time]]:
    """
    Excluye el horario de almuerzo del traslape horario.
    Retorna una lista de segmentos válidos (puede estar vacía).
    """
    inicio, fin = traslape

    # Convertir a minutos
    inicio_min = inicio.hour * 60 + inicio.minute
    fin_min = fin.hour * 60 + fin.minute
    almuerzo_inicio_min = almuerzo_inicio.hour * 60 + almuerzo_inicio.minute
    almuerzo_fin_min = almuerzo_fin.hour * 60 + almuerzo_fin.minute

    segmentos = []

    # Segmento antes del almuerzo
    if inicio_min < almuerzo_inicio_min and fin_min > inicio_min:
        fin_antes_almuerzo = min(fin_min, almuerzo_inicio_min)
        if fin_antes_almuerzo > inicio_min:
            inicio_seg = time(inicio_min // 60, inicio_min % 60)
            fin_seg = time(fin_antes_almuerzo // 60, fin_antes_almuerzo % 60)
            segmentos.append((inicio_seg, fin_seg))

    # Segmento después del almuerzo
    if fin_min > almuerzo_fin_min and inicio_min < fin_min:
        inicio_despues_almuerzo = max(inicio_min, almuerzo_fin_min)
        if fin_min > inicio_despues_almuerzo:
            inicio_seg = time(inicio_despues_almuerzo // 60, inicio_despues_almuerzo % 60)
            fin_seg = time(fin_min // 60, fin_min % 60)
            segmentos.append((inicio_seg, fin_seg))

    return segmentos


def encontrar_hora_cita_valida(segmentos: List[Tuple[time, time]],
                              duracion_minima_minutos: int = 60) -> Optional[time]:
    """
    Encuentra la primera hora válida para agendar una cita en los segmentos disponibles.
    """
    for inicio, fin in segmentos:
        # Verificar si el segmento tiene duración suficiente
        inicio_min = inicio.hour * 60 + inicio.minute
        fin_min = fin.hour * 60 + fin.minute
        duracion = fin_min - inicio_min

        if duracion >= duracion_minima_minutos:
            return inicio

    return None


def validar_duracion_minima_cita(traslape: Tuple[time, time], duracion_minima_minutos: int = 60) -> bool:
    """
    Valida que el traslape horario sea suficiente para la duración de la cita.
    """
    inicio, fin = traslape

    inicio_min = inicio.hour * 60 + inicio.minute
    fin_min = fin.hour * 60 + fin.minute

    duracion_traslape = fin_min - inicio_min

    return duracion_traslape >= duracion_minima_minutos


def validar_compatibilidad_completa(dias_trabajo_empleado: List[str], dias_trabajo_abogado: List[str],
                                  horario_empleado_inicio: time, horario_empleado_fin: time,
                                  horario_abogado_inicio: time, horario_abogado_fin: time,
                                  fecha_cita: date) -> Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
    """
    Valida la compatibilidad completa entre empleado y abogado.
    Excluye el horario de almuerzo (12:00-14:00).

    Returns:
        Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
        - bool: True si es compatible
        - str: Motivo de incompatibilidad si aplica
        - Tuple[time, time]: (hora_inicio_cita, hora_fin_disponible) si es agendable
    """
    # Verificar días comunes
    if not verificar_dias_comunes(dias_trabajo_empleado, dias_trabajo_abogado):
        return False, "No hay días de trabajo comunes entre empleado y abogado", None

    # Verificar que la fecha de la cita sea un día que ambos trabajen
    dias_semana = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    dia_cita = dias_semana[fecha_cita.weekday()]

    if dia_cita not in dias_trabajo_empleado:
        return False, f"El empleado no trabaja los {dia_cita}", None

    if dia_cita not in dias_trabajo_abogado:
        return False, f"El abogado no trabaja los {dia_cita}", None

    # Calcular traslape horario básico
    traslape_basico = calcular_traslape_horario(
        horario_empleado_inicio, horario_empleado_fin,
        horario_abogado_inicio, horario_abogado_fin
    )

    if traslape_basico is None:
        return False, "No hay traslape de horarios entre empleado y abogado", None

    # Excluir horario de almuerzo del traslape
    segmentos_validos = excluir_horario_almuerzo(traslape_basico)

    # Encontrar hora válida para la cita
    hora_cita_valida = encontrar_hora_cita_valida(segmentos_validos)

    if hora_cita_valida is None:
        return False, "No hay horarios disponibles fuera del horario de almuerzo (12:00-14:00)", None

    # Crear tupla con hora de inicio de cita y fin del primer segmento válido
    primer_segmento = next((seg for seg in segmentos_validos
                           if seg[0] == hora_cita_valida), None)

    if primer_segmento:
        return True, None, primer_segmento
    else:
        return False, "Error al determinar segmento válido", None