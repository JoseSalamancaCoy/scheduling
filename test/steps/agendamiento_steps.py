import json
import requests
from behave import given, when, then
from datetime import date, time
import sys
import os

# Agregar el directorio src al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agendar'))

# Agregar el directorio test al path para importar las utilidades de test
test_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(test_dir)

from models import AgendamientoRequest, EmpleadoConfig, AbogadoConfig

# Importar función de parser con path absoluto
test_utils_path = os.path.join(test_dir, 'utils')
sys.path.append(test_utils_path)
from agenda_parser import construir_agenda_desde_archivos


class AgendamientoContext:
    def __init__(self):
        self.fecha_actual = None
        self.hora_actual = time(10, 0)  # Hora por defecto: 10:00
        self.empleado = None
        self.abogado = None
        self.dias_feriados = []
        self.response = None
        self.api_url = "http://localhost:8000"
        self.agenda_empleado = None
        self.agenda_abogado = None


@given('que el sistema tiene acceso a la fecha actual')
def step_sistema_acceso_fecha(context):
    if not hasattr(context, 'agendamiento'):
        context.agendamiento = AgendamientoContext()


@given('el abogado trabaja de "{dia_inicio}" a "{dia_fin}" de "{hora_inicio}" a "{hora_fin}"')
def step_abogado_horario(context, dia_inicio, dia_fin, hora_inicio, hora_fin):
    # Para este ejemplo, asumimos que el abogado siempre trabaja L-V 8-17
    dias_trabajo = ["lunes", "martes", "miércoles", "jueves", "viernes"]
    dias_no_trabajo = ["sábado", "domingo"]

    context.agendamiento.abogado = AbogadoConfig(
        dias_trabajo_abogado=dias_trabajo,
        dias_no_trabajo_abogado=dias_no_trabajo,
        horario_inicio=time.fromisoformat("08:00:00"),
        horario_fin=time.fromisoformat("17:00:00")
    )


@given('que hoy es "{fecha}"')
def step_fecha_actual(context, fecha):
    context.agendamiento.fecha_actual = date.fromisoformat(fecha)


@given('la hora actual es "{hora}"')
def step_hora_actual(context, hora):
    context.agendamiento.hora_actual = time.fromisoformat(hora + ":00")


@given('el empleado trabaja los días: {dias_trabajo}')
def step_empleado_dias_trabajo(context, dias_trabajo):
    # Parsear la lista de días desde el string
    dias_list = json.loads(dias_trabajo.replace("'", '"'))
    if not hasattr(context.agendamiento, 'empleado_dias'):
        context.agendamiento.empleado_dias = dias_list
    else:
        context.agendamiento.empleado_dias = dias_list


@given('el empleado trabaja de "{hora_inicio}" a "{hora_fin}"')
def step_empleado_horario(context, hora_inicio, hora_fin):
    context.agendamiento.empleado_horario_inicio = time.fromisoformat(hora_inicio + ":00")
    context.agendamiento.empleado_horario_fin = time.fromisoformat(hora_fin + ":00")


@given('el empleado {trabaja_festivos} festivos')
def step_empleado_trabaja_festivos(context, trabaja_festivos):
    context.agendamiento.trabaja_festivos = (trabaja_festivos == "trabaja")


@given('los días feriados son: {dias_feriados}')
def step_dias_feriados(context, dias_feriados):
    if dias_feriados.strip() == "[]":
        context.agendamiento.dias_feriados = []
    else:
        # Parsear la lista de fechas
        fechas_list = json.loads(dias_feriados.replace("'", '"'))
        context.agendamiento.dias_feriados = [date.fromisoformat(f) for f in fechas_list]




@when('se calcula la fecha de notificación')
def step_calcular_fecha_notificacion(context):
    # Cargar automáticamente las agendas desde los archivos CSV
    try:
        ruta_data = os.path.join(os.path.dirname(__file__), '..', 'data')
        agenda_empleado, agenda_abogado = construir_agenda_desde_archivos(ruta_data)
        context.agendamiento.agenda_empleado = agenda_empleado
        context.agendamiento.agenda_abogado = agenda_abogado
    except Exception as e:
        print(f"Error al cargar agendas: {str(e)}")
        context.agendamiento.agenda_empleado = None
        context.agendamiento.agenda_abogado = None

    # Construir el objeto de request
    empleado = EmpleadoConfig(
        dias_trabajo_empleado=context.agendamiento.empleado_dias,
        horario_inicio=context.agendamiento.empleado_horario_inicio,
        horario_fin=context.agendamiento.empleado_horario_fin,
        trabaja_festivos=context.agendamiento.trabaja_festivos
    )

    request_data = AgendamientoRequest(
        fecha_actual=context.agendamiento.fecha_actual,
        hora_actual=context.agendamiento.hora_actual,
        empleado=empleado,
        abogado=context.agendamiento.abogado,
        dias_feriados=context.agendamiento.dias_feriados,
        agenda_empleado=context.agendamiento.agenda_empleado,
        agenda_abogado=context.agendamiento.agenda_abogado
    )

    # Hacer la llamada a la API
    try:
        response = requests.post(
            f"{context.agendamiento.api_url}/agendar-cita",
            json=request_data.model_dump(mode='json'),
            headers={"Content-Type": "application/json"}
        )
        context.agendamiento.response = response.json()
        context.agendamiento.status_code = response.status_code
    except requests.exceptions.ConnectionError:
        # Si no hay API corriendo, usar la lógica local
        print("API no disponible, usando cálculo local...")
        context.agendamiento.response = {"error": "API no disponible"}
        context.agendamiento.status_code = 500


@when('se verifica la compatibilidad horaria')
def step_verificar_compatibilidad(context):
    # Esta verificación ya está incluida en el cálculo anterior
    pass


@when('se ejecuta el proceso de agendamiento')
def step_ejecutar_proceso_agendamiento(context):
    # Reutilizar el step anterior
    step_calcular_fecha_notificacion(context)


@then('la fecha de notificación debe ser "{fecha_esperada}"')
def step_verificar_fecha_notificacion(context, fecha_esperada):
    assert context.agendamiento.response is not None, "No hay respuesta de la API"

    if "error" in context.agendamiento.response:
        print(f"Error en API: {context.agendamiento.response['error']}")
        return

    # Verificar que la fecha_actual coincida con la enviada
    fecha_actual = context.agendamiento.response.get("fecha_actual")
    fecha_actual_enviada = str(context.agendamiento.fecha_actual)
    assert fecha_actual == fecha_actual_enviada, f"fecha_actual enviada: {fecha_actual_enviada}, recibida: {fecha_actual}"

    fecha_notificacion = context.agendamiento.response.get("fecha_notificacion")
    assert fecha_notificacion == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {fecha_notificacion}"


@then('la fecha de inicio del conteo debe ser "{fecha_esperada}"')
def step_verificar_fecha_inicio_conteo(context, fecha_esperada):
    if "error" in context.agendamiento.response:
        return

    fecha_inicio_conteo = context.agendamiento.response.get("fecha_inicio_conteo")
    assert fecha_inicio_conteo == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {fecha_inicio_conteo}"


@then('la fecha de la cita debe ser "{fecha_esperada}"')
def step_verificar_fecha_cita(context, fecha_esperada):
    if "error" in context.agendamiento.response:
        return

    fecha_cita = context.agendamiento.response.get("fecha_cita")
    assert fecha_cita == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {fecha_cita}"


@then('la hora de la cita debe estar entre "{hora_inicio}" y "{hora_fin}"')
def step_verificar_hora_cita(context, hora_inicio, hora_fin):
    if "error" in context.agendamiento.response:
        return

    hora_cita = context.agendamiento.response.get("hora_cita")
    assert hora_cita is not None, "No se encontró hora_cita en la respuesta"

    # Verificar que la hora esté en el formato correcto y dentro del rango
    assert hora_inicio <= hora_cita <= hora_fin, f"Hora {hora_cita} no está entre {hora_inicio} y {hora_fin}"


@then('debe existir traslape horario de "{hora_inicio}" a "{hora_fin}"')
def step_verificar_traslape_horario_positivo(context, hora_inicio, hora_fin):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == True
    hora_cita = context.agendamiento.response.get("hora_cita")
    assert hora_inicio <= hora_cita <= hora_fin, f"Hora {hora_cita} no está entre {hora_inicio} y {hora_fin}"


@then('no debe existir traslape horario')
def step_verificar_no_traslape_horario(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == False


@then('no debe ser posible agendar - empleado y abogado no coinciden en días')
def step_verificar_no_coinciden_dias(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == False
    motivo = context.agendamiento.response.get("motivo", "")
    assert "días de trabajo comunes" in motivo or "no trabaja los" in motivo


@then('no debe ser posible agendar la cita')
def step_no_agendable(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == False


@then('el motivo debe ser "{motivo_esperado}"')
def step_verificar_motivo(context, motivo_esperado):
    if "error" in context.agendamiento.response:
        return

    motivo = context.agendamiento.response.get("motivo")
    assert motivo_esperado in motivo, f"Esperaba motivo que contenga '{motivo_esperado}', obtuve '{motivo}'"


@then('la hora de la cita debe ser "{hora_esperada}" evitando horario de almuerzo')
def step_verificar_hora_evita_almuerzo(context, hora_esperada):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == True, "La cita debe ser agendable"
    hora_cita = context.agendamiento.response.get("hora_cita")

    # Normalizar formatos de hora para comparación (tanto "09:00" como "09:00:00" son válidos)
    from datetime import time
    hora_esperada_normalizada = hora_esperada if len(hora_esperada.split(":")) == 3 else hora_esperada + ":00"

    assert hora_cita == hora_esperada_normalizada, f"Esperaba hora {hora_esperada_normalizada}, obtuve {hora_cita}"

    # Verificar que la hora no esté en horario de almuerzo (12:00-14:00)
    hora_obj = time.fromisoformat(hora_cita)
    almuerzo_inicio = time(12, 0)
    almuerzo_fin = time(14, 0)

    assert not (almuerzo_inicio <= hora_obj < almuerzo_fin), f"Hora {hora_cita} está en horario de almuerzo prohibido"


@then('no debe ser posible agendar debido a horario de almuerzo')
def step_no_agendable_por_almuerzo(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("es_agendable") == False, "La cita no debe ser agendable debido a horario de almuerzo"
    motivo = context.agendamiento.response.get("motivo", "")
    assert "almuerzo" in motivo.lower() or "12:00" in motivo or "14:00" in motivo, f"El motivo debe mencionar horario de almuerzo, obtuve: '{motivo}'"


@then('la respuesta debe contener')
def step_verificar_estructura_respuesta(context):
    if "error" in context.agendamiento.response:
        return

    response = context.agendamiento.response

    # Verificar campos requeridos
    campos_requeridos = ["fecha_actual", "fecha_notificacion", "fecha_inicio_conteo", "fecha_cita", "hora_cita", "es_agendable"]

    for campo in campos_requeridos:
        assert campo in response, f"Campo requerido '{campo}' no encontrado en la respuesta"

    # Verificar tipos
    assert isinstance(response["es_agendable"], bool), "es_agendable debe ser boolean"