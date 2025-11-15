# 📅 Sistema de Agendamiento de Citas con Empleados

API para calcular automáticamente fechas de notificación y agendamiento de citas entre empleados y abogados según reglas de negocio específicas.

## 🎯 Descripción General

Este sistema automatiza el proceso de agendamiento de citas considerando:
- Horarios laborales de empleados y abogados
- Días festivos y su impacto según configuración del empleado
- Restricciones de horario (almuerzo)
- Compatibilidad de horarios entre partes
- Secuencia temporal: notificación → inicio de conteo → cita

## 📋 Reglas de Negocio

### 1. **Cálculo de Fecha de Notificación**
- **Si es día hábil del empleado Y dentro de horario laboral**: La notificación se envía el mismo día
- **Si es día no hábil O fuera del horario laboral**: La notificación se envía el siguiente día hábil del empleado
- **Consideración de horario**: Si el abogado crea el caso después del horario laboral del empleado (ej: empleado trabaja hasta 16:00, caso creado a las 16:30), la notificación se posterga al siguiente día hábil

### 2. **Días Hábiles del Empleado**
- Definidos por la lista `dias_trabajo_empleado` (exactamente 5 días)
- Días válidos: `["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]`
- **Festivos**: Depende de la configuración `trabaja_festivos`:
  - `trabaja_festivos = true`: Los días festivos son considerados hábiles
  - `trabaja_festivos = false`: Los días festivos NO son considerados hábiles

### 3. **Secuencia Temporal**
1. **Fecha de Notificación**: Cuando se notifica al empleado sobre la cita
2. **Fecha de Inicio del Conteo**: Siguiente día hábil después de la notificación
3. **Fecha de la Cita**: 5 días hábiles del empleado después del inicio del conteo

### 4. **Configuración del Abogado**
- **Días de trabajo**: Lunes a Viernes (`["lunes", "martes", "miércoles", "jueves", "viernes"]`)
- **Horario**: 08:00 a 17:00
- **Festivos**: Los abogados no trabajan días festivos

### 5. **Restricción de Horario de Almuerzo**
- **Prohibido agendar citas entre 12:00 PM y 2:00 PM**
- Si el traslape horario cae en este rango:
  - **Antes del almuerzo**: Se agenda al inicio del traslape (ej: 11:00-13:00 → agenda a las 11:00)
  - **Después del almuerzo**: Se agenda después del almuerzo (ej: 13:00-15:00 → agenda a las 14:00)
  - **Solo durante almuerzo**: No es agendable (ej: 12:00-14:00 → error)

### 6. **Compatibilidad de Horarios**
- **Días comunes**: Empleado y abogado deben tener al menos un día de trabajo en común
- **Traslape horario**: Debe existir al menos 1 hora de traslape entre horarios
- **Duración mínima**: El traslape debe permitir una cita de al menos 60 minutos
- **Exclusión de almuerzo**: El traslape se calcula excluyendo 12:00-14:00

### 7. **Casos No Agendables**
La cita NO se puede agendar si:
- No hay días de trabajo comunes entre empleado y abogado
- No hay traslape de horarios entre empleado y abogado
- El traslape horario es insuficiente para una cita de 1 hora
- El único traslape disponible es durante el horario de almuerzo (12:00-14:00)

## 🏗️ Arquitectura Técnica

### Componentes Principales
```
src/
├── main.py                    # FastAPI application y endpoint principal
├── models.py                  # Modelos Pydantic para request/response
└── utils/
    ├── date_calculator.py     # Lógica de cálculo de fechas
    ├── schedule_validator.py   # Validación de compatibilidad horaria
    └── holiday_handler.py     # Manejo de días festivos
```

### Endpoints

#### `POST /agendar-cita`
Calcula fechas de agendamiento según las reglas de negocio.

**Request Body:**
```json
{
  "fecha_actual": "2024-03-04",
  "hora_actual": "10:00",
  "empleado": {
    "dias_trabajo_empleado": ["lunes", "martes", "miércoles", "jueves", "viernes"],
    "horario_inicio": "09:00",
    "horario_fin": "18:00",
    "trabaja_festivos": false
  },
  "abogado": {
    "dias_trabajo_abogado": ["lunes", "martes", "miércoles", "jueves", "viernes"],
    "dias_no_trabajo_abogado": ["sábado", "domingo"],
    "horario_inicio": "08:00",
    "horario_fin": "17:00"
  },
  "dias_feriados": []
}
```

**Response Body:**
```json
{
  "fecha_actual": "2024-03-04",
  "fecha_notificacion": "2024-03-04",
  "fecha_inicio_conteo": "2024-03-05",
  "fecha_cita": "2024-03-12",
  "hora_cita": "09:00:00",
  "es_agendable": true,
  "motivo": null
}
```

## 📊 Casos de Uso Cubiertos

### ✅ Casos Exitosos
- Empleado en horario laboral → notificación inmediata
- Empleado fuera de horario → notificación siguiente día hábil
- Manejo de días festivos según configuración del empleado
- Traslape horario con exclusión de almuerzo
- Múltiples días festivos consecutivos
- Diferentes combinaciones de horarios de trabajo

### ❌ Casos No Agendables
- Sin días comunes entre empleado y abogado
- Sin traslape horario entre partes
- Traslape insuficiente (< 60 minutos)
- Solo traslape durante horario de almuerzo

## 🚀 Uso

### Instalación
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install fastapi uvicorn pydantic

# Ejecutar servidor
python src/main.py
```

### Servidor disponible en: `http://localhost:8000`

### Documentación API: `http://localhost:8000/docs`

## 🧪 Testing

El sistema incluye pruebas BDD con Behave:

```bash
# Ejecutar todas las pruebas
source venv/bin/activate && behave test/

# Ejecutar pruebas específicas
behave test/ -n "horario de almuerzo"
```

### Cobertura de Pruebas
- ✅ **26 escenarios** cubriendo todas las reglas de negocio
- ✅ **298 steps** validando comportamiento detallado
- ✅ **0 fallos** - todas las pruebas pasan

## 📝 Ejemplos de Uso

### Ejemplo 1: Cita Agendable
**Entrada:**
- Fecha actual: Lunes 2024-03-04 a las 10:00
- Empleado: L-V, 09:00-18:00, no trabaja festivos
- Abogado: L-V, 08:00-17:00

**Resultado:**
- Notificación: 2024-03-04 (mismo día)
- Inicio conteo: 2024-03-05 (siguiente día hábil)
- Cita: 2024-03-12 (5 días hábiles después)
- Hora: 09:00 (inicio del traslape, evitando almuerzo)

### Ejemplo 2: Horario Vencido
**Entrada:**
- Fecha actual: Lunes 2024-03-04 a las 16:30
- Empleado: L-V, 09:00-16:00 (horario ya terminó)

**Resultado:**
- Notificación: 2024-03-05 (siguiente día hábil)
- Secuencia ajustada automáticamente

### Ejemplo 3: No Agendable
**Entrada:**
- Empleado: S-D (solo fines de semana)
- Abogado: L-V (solo días laborales)

**Resultado:**
- `es_agendable: false`
- `motivo: "No hay días de trabajo comunes entre empleado y abogado"`

## 🔧 Configuración

### Variables de Horario de Almuerzo
Por defecto configurado en `schedule_validator.py`:
- Inicio: 12:00 PM
- Fin: 2:00 PM

### Duración Mínima de Cita
- Por defecto: 60 minutos
- Configurable en funciones de validación

---

**Versión:** 1.0.0
**Estado:** ✅ Producción - Todas las pruebas pasan
**Última actualización:** Implementación de restricción de horario de almuerzo