import csv
import sys
import os
from datetime import date, time, timedelta, datetime
from typing import List, Tuple

# Agregar el directorio src al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agendar'))

from models import ReunioneOcupada, AgendaOcupada


def parsear_tiempo_desde_header(header_time: str) -> time:
    """
    Convierte un string de tiempo del header del CSV (ej: '07:00') a un objeto time.
    """
    return time.fromisoformat(header_time + ":00")


def encontrar_bloques_ocupados(fila_datos: List[str], headers_tiempo: List[str]) -> List[Tuple[time, time]]:
    """
    Encuentra bloques consecutivos donde el valor es '1' (ocupado).
    Retorna una lista de tuplas (hora_inicio, hora_fin).
    """
    bloques = []
    inicio_bloque = None

    for i, valor in enumerate(fila_datos):
        if valor == '1':  # Ocupado
            if inicio_bloque is None:
                inicio_bloque = i
        else:  # Libre o fin de datos
            if inicio_bloque is not None:
                # Terminar el bloque actual
                hora_inicio = parsear_tiempo_desde_header(headers_tiempo[inicio_bloque])
                # La hora fin es el inicio del slot siguiente (15 min después del último slot ocupado)
                ultimo_slot_ocupado = i - 1
                hora_ultimo_slot = parsear_tiempo_desde_header(headers_tiempo[ultimo_slot_ocupado])
                # Añadir 15 minutos para obtener la hora de fin
                datetime_temp = datetime.combine(date.today(), hora_ultimo_slot)
                datetime_fin = datetime_temp + timedelta(minutes=15)
                hora_fin = datetime_fin.time()

                bloques.append((hora_inicio, hora_fin))
                inicio_bloque = None

    # Si el archivo termina con un bloque ocupado
    if inicio_bloque is not None:
        hora_inicio = parsear_tiempo_desde_header(headers_tiempo[inicio_bloque])
        ultimo_slot_ocupado = len(fila_datos) - 1
        hora_ultimo_slot = parsear_tiempo_desde_header(headers_tiempo[ultimo_slot_ocupado])
        # Añadir 15 minutos para obtener la hora de fin
        datetime_temp = datetime.combine(date.today(), hora_ultimo_slot)
        datetime_fin = datetime_temp + timedelta(minutes=15)
        hora_fin = datetime_fin.time()

        bloques.append((hora_inicio, hora_fin))

    return bloques


def parsear_csv_agenda(ruta_archivo: str) -> AgendaOcupada:
    """
    Parsea un archivo CSV de agenda y retorna un objeto AgendaOcupada.

    Formato esperado del CSV:
    - Primera columna: fecha en formato YYYY-MM-DD
    - Resto de columnas: slots de tiempo de 15 minutos (1 = ocupado, 0 = libre)
    """
    reuniones = []

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        reader = csv.reader(archivo)
        headers = next(reader)  # Primera fila con headers

        # Extraer headers de tiempo (ignorar la primera columna 'fecha')
        headers_tiempo = headers[1:]

        for fila in reader:
            fecha_str = fila[0]
            fecha_obj = date.fromisoformat(fecha_str)

            # Datos de ocupación (ignorar la primera columna que es la fecha)
            datos_ocupacion = fila[1:]

            # Encontrar bloques de tiempo ocupados
            bloques_ocupados = encontrar_bloques_ocupados(datos_ocupacion, headers_tiempo)

            # Crear reuniones para cada bloque ocupado
            for hora_inicio, hora_fin in bloques_ocupados:
                reunion = ReunioneOcupada(
                    fecha=fecha_obj,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                reuniones.append(reunion)

    return AgendaOcupada(reuniones=reuniones)


def construir_agenda_desde_archivos(ruta_base: str) -> Tuple[AgendaOcupada, AgendaOcupada]:
    """
    Construye las agendas del empleado y abogado desde los archivos CSV.

    Args:
        ruta_base: Ruta base donde se encuentran los archivos de datos

    Returns:
        Tupla con (agenda_empleado, agenda_abogado)
    """
    ruta_empleado = os.path.join(ruta_base, "agenda_empleado.csv")
    ruta_abogado = os.path.join(ruta_base, "agenda_abogado.csv")

    agenda_empleado = parsear_csv_agenda(ruta_empleado)
    agenda_abogado = parsear_csv_agenda(ruta_abogado)

    return agenda_empleado, agenda_abogado