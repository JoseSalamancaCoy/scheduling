import os
import sys
import subprocess
import time
import requests
from threading import Thread

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agendar'))

API_URL = "http://localhost:8000"
API_PROCESS = None


def start_api_server():
    """Inicia el servidor de la API en segundo plano"""
    global API_PROCESS
    try:
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'agendar')
        API_PROCESS = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd=src_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Esperar a que la API esté lista
        for _ in range(30):  # 30 intentos, 1 segundo cada uno
            try:
                response = requests.get(f"{API_URL}/")
                if response.status_code == 200:
                    print("✅ API iniciada correctamente")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                continue

        print("❌ No se pudo conectar a la API")
        return False
    except Exception as e:
        print(f"❌ Error al iniciar API: {e}")
        return False


def stop_api_server():
    """Detiene el servidor de la API"""
    global API_PROCESS
    if API_PROCESS:
        try:
            API_PROCESS.terminate()
            API_PROCESS.wait(timeout=5)
            print("✅ API detenida correctamente")
        except subprocess.TimeoutExpired:
            API_PROCESS.kill()
            print("⚠️  API forzada a detenerse")
        except Exception as e:
            print(f"❌ Error al detener API: {e}")


def before_all(context):
    """Se ejecuta antes de todas las pruebas"""
    print("\n🚀 Iniciando pruebas de agendamiento...")
    print("📡 Iniciando servidor API...")

    api_started = start_api_server()
    context.api_available = api_started

    if not api_started:
        print("⚠️  Las pruebas se ejecutarán sin API (modo simulación)")


def after_all(context):
    """Se ejecuta después de todas las pruebas"""
    print("\n🔄 Limpiando recursos...")
    stop_api_server()
    print("✅ Pruebas finalizadas")


def before_scenario(context, scenario):
    """Se ejecuta antes de cada escenario"""
    context.scenario_name = scenario.name


def after_scenario(context, scenario):
    """Se ejecuta después de cada escenario"""
    if scenario.status == "failed":
        print(f"❌ Escenario fallido: {scenario.name}")
        if hasattr(context, 'agendamiento') and hasattr(context.agendamiento, 'response'):
            print(f"   Respuesta: {context.agendamiento.response}")
    else:
        print(f"✅ Escenario exitoso: {scenario.name}")


def before_step(context, step):
    """Se ejecuta antes de cada step"""
    pass


def after_step(context, step):
    """Se ejecuta después de cada step"""
    if step.status == "failed":
        print(f"   ❌ Step fallido: {step.name}")
        if hasattr(step, 'exception'):
            print(f"   Error: {step.exception}")