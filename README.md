# 📅 Sistema de Agendamiento de Citas

API para calcular automáticamente fechas de notificación y agendamiento de citas entre empleados y abogados según reglas de negocio específicas.

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **FastAPI** | 0.104.1 | Framework web para API REST |
| **Pydantic** | 2.5.0 | Validación de datos y modelos |
| **Uvicorn** | 0.24.0 | Servidor ASGI para FastAPI |
| **Behave** | 1.2.6 | Pruebas BDD (Behavior Driven Development) |
| **Requests** | 2.31.0 | Cliente HTTP para pruebas |
| **Pandas** | 2.1.3 | Manipulación de datos CSV |
| **PyYAML** | 6.0.1 | Procesamiento de archivos YAML |
| **Python-multipart** | 0.0.6 | Soporte para formularios multipart |
| **Colorama** | 0.4.6 | Colores en terminal para pruebas |

## 🚀 Guía de Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone <repository-url>
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python src/scheduler/main.py
```

### 5. Verificar funcionamiento
- **API disponible en**: `http://localhost:8000`
- **Documentación interactiva**: `http://localhost:8000/docs`
- **Endpoint principal**: `POST /schedule-appointment`

### 6. Ejecutar pruebas
```bash
behave test/
```

## 📖 Documentación Detallada

Para información completa sobre el sistema, consulta:

📋 **[Reglas de Negocio - Documentación Completa](docs/business-rules.md)**

🧪 **[Guía de Configuración de Pruebas](docs/testing-guide.md)**

---

**Versión:** 1.0.0 | **Estado:** ✅ Producción