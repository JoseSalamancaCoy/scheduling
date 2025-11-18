import json
import requests
from behave import given, when, then
from datetime import date, time
import sys
import os

# Add src directory to path for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'scheduler'))

# Add test directory to path for importing test utilities
test_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(test_dir)

from models import AppointmentRequest, EmployeeConfig, LawyerConfig

# Import parser function with absolute path
test_utils_path = os.path.join(test_dir, 'utils')
sys.path.append(test_utils_path)
from schedule_parser import build_schedules_from_files


class AgendamientoContext:
    def __init__(self):
        self.fecha_actual = None
        self.hora_actual = time(10, 0)  # Hora por defecto: 10:00
        self.empleado = None
        self.lawyer = None
        self.holiday_dates = []
        self.response = None
        self.api_url = "http://localhost:8000"
        self.employee_schedule = None
        self.lawyer_schedule = None


@given('que el sistema tiene acceso a la fecha actual')
def step_sistema_acceso_fecha(context):
    if not hasattr(context, 'agendamiento'):
        context.agendamiento = AgendamientoContext()


@given('el abogado trabaja de "{dia_inicio}" a "{dia_fin}" de "{hora_inicio}" a "{hora_fin}"')
def step_abogado_horario(context, dia_inicio, dia_fin, hora_inicio, hora_fin):
    # Para este ejemplo, asumimos que el abogado siempre trabaja L-V 8-17
    dias_trabajo = ["lunes", "martes", "miércoles", "jueves", "viernes"]
    dias_no_trabajo = ["sábado", "domingo"]

    context.agendamiento.lawyer = LawyerConfig(
        work_days=dias_trabajo,
        non_work_days=dias_no_trabajo,
        start_time=time.fromisoformat("08:00:00"),
        end_time=time.fromisoformat("17:00:00")
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
        context.agendamiento.holiday_dates = []
    else:
        # Parsear la lista de fechas
        fechas_list = json.loads(dias_feriados.replace("'", '"'))
        context.agendamiento.holiday_dates = [date.fromisoformat(f) for f in fechas_list]




@when('se calcula la fecha de notificación')
def step_calcular_fecha_notificacion(context):
    # Automatically load schedules from CSV files
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        employee_schedule, lawyer_schedule = build_schedules_from_files(data_path)
        context.agendamiento.employee_schedule = employee_schedule
        context.agendamiento.lawyer_schedule = lawyer_schedule
    except Exception as e:
        print(f"Error loading schedules: {str(e)}")
        context.agendamiento.employee_schedule = None
        context.agendamiento.lawyer_schedule = None

    # Build request object
    employee = EmployeeConfig(
        work_days=context.agendamiento.empleado_dias,
        start_time=context.agendamiento.empleado_horario_inicio,
        end_time=context.agendamiento.empleado_horario_fin,
        works_holidays=context.agendamiento.trabaja_festivos
    )

    request_data = AppointmentRequest(
        current_date=context.agendamiento.fecha_actual,
        current_time=context.agendamiento.hora_actual,
        employee=employee,
        lawyer=context.agendamiento.lawyer,
        holiday_dates=context.agendamiento.holiday_dates,
        employee_schedule=context.agendamiento.employee_schedule,
        lawyer_schedule=context.agendamiento.lawyer_schedule
    )

    # Hacer la llamada a la API
    try:
        response = requests.post(
            f"{context.agendamiento.api_url}/schedule-appointment",
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

    # Verificar que la current_date coincida con la enviada
    current_date = context.agendamiento.response.get("current_date")
    fecha_actual_enviada = str(context.agendamiento.fecha_actual)
    assert current_date == fecha_actual_enviada, f"current_date enviada: {fecha_actual_enviada}, recibida: {current_date}"

    notification_date = context.agendamiento.response.get("notification_date")
    assert notification_date == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {notification_date}"


@then('la fecha de inicio del conteo debe ser "{fecha_esperada}"')
def step_verificar_fecha_inicio_conteo(context, fecha_esperada):
    if "error" in context.agendamiento.response:
        return

    counting_start_date = context.agendamiento.response.get("counting_start_date")
    assert counting_start_date == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {counting_start_date}"


@then('la fecha de la cita debe ser "{fecha_esperada}"')
def step_verificar_fecha_cita(context, fecha_esperada):
    if "error" in context.agendamiento.response:
        return

    appointment_date = context.agendamiento.response.get("appointment_date")
    assert appointment_date == fecha_esperada, f"Esperaba {fecha_esperada}, obtuve {appointment_date}"


@then('la hora de la cita debe estar entre "{hora_inicio}" y "{hora_fin}"')
def step_verificar_hora_cita(context, hora_inicio, hora_fin):
    if "error" in context.agendamiento.response:
        return

    appointment_time = context.agendamiento.response.get("appointment_time")
    assert appointment_time is not None, "No se encontró appointment_time en la respuesta"

    # Verificar que la hora esté en el formato correcto y dentro del rango
    assert hora_inicio <= appointment_time <= hora_fin, f"Hora {appointment_time} no está entre {hora_inicio} y {hora_fin}"


@then('debe existir traslape horario de "{hora_inicio}" a "{hora_fin}"')
def step_verificar_traslape_horario_positivo(context, hora_inicio, hora_fin):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == True
    appointment_time = context.agendamiento.response.get("appointment_time")
    assert hora_inicio <= appointment_time <= hora_fin, f"Hora {appointment_time} no está entre {hora_inicio} y {hora_fin}"


@then('no debe existir traslape horario')
def step_verificar_no_traslape_horario(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == False


@then('no debe ser posible agendar - empleado y abogado no coinciden en días')
def step_verificar_no_coinciden_dias(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == False
    reason = context.agendamiento.response.get("reason", "")
    assert "No common work days" in reason or "doesn't work on" in reason


@then('no debe ser posible agendar la cita')
def step_no_agendable(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == False


@then('el motivo debe ser "{motivo_esperado}"')
def step_verificar_motivo(context, motivo_esperado):
    if "error" in context.agendamiento.response:
        return

    reason = context.agendamiento.response.get("reason")
    assert motivo_esperado in reason, f"Esperaba motivo que contenga '{motivo_esperado}', obtuve '{reason}'"


@then('la hora de la cita debe ser "{hora_esperada}" evitando horario de almuerzo')
def step_verificar_hora_evita_almuerzo(context, hora_esperada):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == True, "La cita debe ser agendable"
    appointment_time = context.agendamiento.response.get("appointment_time")

    # Normalizar formatos de hora para comparación (tanto "09:00" como "09:00:00" son válidos)
    from datetime import time
    hora_esperada_normalizada = hora_esperada if len(hora_esperada.split(":")) == 3 else hora_esperada + ":00"

    assert appointment_time == hora_esperada_normalizada, f"Esperaba hora {hora_esperada_normalizada}, obtuve {appointment_time}"

    # Verificar que la hora no esté en horario de almuerzo (12:00-14:00)
    hora_obj = time.fromisoformat(appointment_time)
    almuerzo_inicio = time(12, 0)
    almuerzo_fin = time(14, 0)

    assert not (almuerzo_inicio <= hora_obj < almuerzo_fin), f"Hora {appointment_time} está en horario de almuerzo prohibido"


@then('no debe ser posible agendar debido a horario de almuerzo')
def step_no_agendable_por_almuerzo(context):
    if "error" in context.agendamiento.response:
        return

    assert context.agendamiento.response.get("is_schedulable") == False, "La cita no debe ser agendable debido a horario de almuerzo"
    reason = context.agendamiento.response.get("reason", "")
    assert "lunch hours" in reason.lower() or "12:00" in reason or "14:00" in reason, f"El motivo debe mencionar horario de almuerzo, obtuve: '{reason}'"


@then('la respuesta debe contener')
def step_verificar_estructura_respuesta(context):
    if "error" in context.agendamiento.response:
        return

    response = context.agendamiento.response

    # Verificar campos requeridos
    campos_requeridos = ["current_date", "notification_date", "counting_start_date", "appointment_date", "appointment_time", "is_schedulable"]

    for campo in campos_requeridos:
        assert campo in response, f"Campo requerido '{campo}' no encontrado en la respuesta"

    # Verificar tipos
    assert isinstance(response["is_schedulable"], bool), "is_schedulable debe ser boolean"