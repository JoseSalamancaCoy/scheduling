# Reglas de Negocio - Sistema de Agendamiento de Citas

## Resumen General
Este documento describe las reglas de negocio implementadas en el sistema de agendamiento de citas. El sistema gestiona la programación de citas entre empleados y abogados según requisitos empresariales específicos.

## Entidades Principales

### Configuración del Empleado
- **Días Laborales**: Lista de días de trabajo (ej: ["lunes", "martes", "miércoles", "jueves", "viernes"])
- **Horario Laboral**: Hora de inicio y fin de la jornada laboral del empleado
- **Política de Festivos**: Indicador booleano si el empleado trabaja en días festivos
- **Agenda Ocupada**: Calendario opcional con reuniones/compromisos existentes

### Configuración del Abogado
- **Días Laborales**: Lista de días de trabajo del abogado
- **Días No Laborales**: Lista explícita de días que el abogado no trabaja
- **Horario Laboral**: Hora de inicio y fin de disponibilidad del abogado
- **Agenda Ocupada**: Calendario opcional con reuniones/compromisos existentes

## 1. Proceso Central de Agendamiento

El agendamiento de citas sigue un **proceso secuencial de 5 pasos**:

### Paso 1: Calcular Fecha de Notificación
**Regla**: Determinar cuándo se debe notificar al empleado sobre la cita
- **Si el día actual es día laboral del empleado Y está dentro del horario**: Notificación = Hoy
- **En caso contrario**: Notificación = Siguiente día laboral del empleado

**Implementación**: `src/scheduler/utils/date_calculator.py:calculate_notification_date()`

### Paso 2: Calcular Fecha de Inicio del Conteo
**Regla**: Primer día hábil después de la notificación para cálculos de programación
- **Fórmula**: Fecha de Notificación + 1 día laboral del empleado
- **Propósito**: Establece la línea base para el requisito de 5 días de anticipación

**Implementación**: `src/scheduler/utils/date_calculator.py:calculate_counting_start_date()`

### Paso 3: Calcular Fecha Base de la Cita
**Regla**: Requisito de programación con 5 días hábiles de anticipación
- **Fórmula**: Fecha de Inicio del Conteo + 5 días laborales del empleado
- **Excluye**: Fines de semana, festivos (según política de festivos del empleado)

**Implementación**: `src/scheduler/utils/date_calculator.py:calculate_appointment_date()`

### Paso 4: Validar Compatibilidad
**Regla**: Asegurar que tanto empleado como abogado puedan reunirse en la fecha calculada
- **Días Laborales Comunes**: Ambas partes deben trabajar el mismo día de la semana
- **Traslape de Horarios**: Las horas de trabajo deben tener segmentos de tiempo superpuestos
- **Exclusión de Hora de Almuerzo**: No hay citas entre 12:00-14:00
- **Conflictos de Agenda Ocupada**: Sin conflictos con reuniones existentes

**Implementación**: `src/scheduler/utils/schedule_validator.py:validate_compatibility_with_schedules()`

### Paso 5: Determinar Hora Final de la Cita
**Regla**: Programar la cita en la primera hora de traslape disponible
- **Preferencia**: Inicio del primer segmento de tiempo válido
- **Duración Mínima**: 60 minutos requeridos
- **Exclusiones**: Horas de almuerzo y períodos ocupados

## 2. Reglas de Cálculo de Fechas

### 2.1 Validación de Días Laborales
**Criterios para Día Laboral del Empleado**:
```
es_dia_laboral = (nombre_dia in dias_trabajo_empleado) AND
                 (NOT festivo OR empleado_trabaja_festivos)
```

**Mapeo de Nombres de Días**:
- Lunes = "lunes"
- Martes = "martes"
- Miércoles = "miércoles"
- Jueves = "jueves"
- Viernes = "viernes"
- Sábado = "sábado"
- Domingo = "domingo"

### 2.2 Manejo de Festivos
**Regla**: El tratamiento de festivos depende de la configuración del empleado

**Si el Empleado Trabaja Festivos** (`works_holidays = true`):
- Los festivos se tratan como días laborales normales
- No se requiere manejo especial

**Si el Empleado No Trabaja Festivos** (`works_holidays = false`):
- Los festivos se excluyen de los cálculos de días laborales
- La programación de citas omite los festivos

**Implementación**: `src/scheduler/utils/holiday_handler.py:filter_holidays_for_employee()`

### 2.3 Límites de Búsqueda
**Regla**: Prevenir bucles infinitos en cálculos de fechas
- **Búsqueda de Fecha de Notificación**: Máximo 30 días
- **Búsqueda de Fecha de Inicio del Conteo**: Máximo 30 días
- **Búsqueda de Fecha de Cita**: Máximo 60 días
- **Búsqueda de Fecha Compatible**: Máximo 30 días

## 3. Reglas de Traslape de Horarios y Compatibilidad

### 3.1 Cálculo de Traslape de Horarios
**Regla**: Encontrar la intersección de tiempo entre los horarios del empleado y el abogado

**Fórmula**:
```
inicio_traslape = MAX(hora_inicio_empleado, hora_inicio_abogado)
fin_traslape = MIN(hora_fin_empleado, hora_fin_abogado)
traslape_valido = inicio_traslape < fin_traslape
```

**Implementación**: `src/scheduler/utils/schedule_validator.py:calculate_schedule_overlap()`

### 3.2 Exclusión de Hora de Almuerzo
**Regla**: No hay citas durante las horas de almuerzo (12:00-14:00)

**Segmentos de Tiempo**:
- **Antes del Almuerzo**: inicio_traslape hasta 12:00 (si está disponible)
- **Después del Almuerzo**: 14:00 hasta fin_traslape (si está disponible)

**Validación**: Cada segmento debe tener una duración mínima de 60 minutos

**Implementación**: `src/scheduler/utils/schedule_validator.py:exclude_lunch_hours()`

### 3.3 Validación de Días Laborales Comunes
**Regla**: El empleado y el abogado deben compartir al menos un día laboral común

**Validación**:
```
dias_comunes = SET(dias_trabajo_empleado) ∩ SET(dias_trabajo_abogado)
es_compatible = len(dias_comunes) > 0
```

**Fallo**: Retorna error "No common work days between employee and lawyer"

### 3.4 Validación del Día de la Fecha de Cita
**Regla**: La fecha de cita calculada debe caer en un día cuando ambas partes trabajen

**Pasos de Validación**:
1. Convertir fecha de cita al nombre del día
2. Verificar si el día está en dias_trabajo_empleado
3. Verificar si el día está en dias_trabajo_abogado
4. Ambos deben ser verdaderos para que proceda la programación

## 4. Integración de Agenda Ocupada

### 4.1 Estructura de Agenda Ocupada
**Formato de Reunión**:
```json
{
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM:SS",
  "end_time": "HH:MM:SS"
}
```

**Formato de Agenda**:
```json
{
  "meetings": [
    {
      "date": "2024-03-15",
      "start_time": "09:00:00",
      "end_time": "10:30:00"
    }
  ]
}
```

### 4.2 Detección de Conflictos
**Regla**: Sin traslape de tiempo entre nueva cita y reuniones existentes

**Fórmula de Conflicto**:
```
tiene_conflicto = (inicio_cita < fin_reunion) AND
                  (fin_cita > inicio_reunion)
```

**Implementación**: `src/scheduler/utils/schedule_validator.py:verify_schedule_conflict()`

### 4.3 Cálculo de Segmentos Libres
**Regla**: Identificar franjas horarias disponibles considerando todas las restricciones

**Proceso**:
1. Comenzar con traslape básico de horarios
2. Excluir horas de almuerzo (12:00-14:00)
3. Remover períodos ocupados del empleado
4. Remover períodos ocupados del abogado
5. Filtrar segmentos con duración mínima de 60 minutos

**Implementación**: `src/scheduler/utils/schedule_validator.py:find_free_segments()`

## 5. Reglas de Validación y Manejo de Errores

### 5.1 Jerarquía de Validación de Compatibilidad
1. **Días Laborales Comunes**: Deben compartir al menos un día laboral
2. **Validación del Día de la Cita**: La fecha específica debe funcionar para ambas partes
3. **Traslape de Horarios**: Las horas laborales deben intersecarse
4. **Cumplimiento de Hora de Almuerzo**: Tiempo disponible fuera de 12:00-14:00
5. **Duración Mínima**: Al menos 60 minutos disponibles
6. **Agenda Ocupada**: Sin conflictos con reuniones existentes

### 5.2 Mensajes de Error
**Respuestas de Error Estándar**:
- `"No common work days between employee and lawyer"`
- `"Employee doesn't work on {day_name}"`
- `"Lawyer doesn't work on {day_name}"`
- `"No schedule overlap between employee and lawyer"`
- `"No available times outside lunch hours (12:00-14:00)"`
- `"No available times considering busy schedules"`

### 5.3 Mecanismos de Respaldo
**Cuando es Incompatible**:
- Retornar `is_schedulable = false`
- Proporcionar razón específica de incompatibilidad
- Incluir fechas calculadas para referencia
- Establecer `appointment_time = "00:00:00"` como marcador de posición

## 6. Requisitos Mínimos

### 6.1 Duración de la Cita
**Regla**: Se requiere una duración mínima de 60 minutos para la cita
- **Validación**: `(hora_fin - hora_inicio) >= 60 minutos`
- **Aplicación**: Aplicado a todos los segmentos de tiempo antes de la programación

### 6.2 Definición de Día Laboral
**Regla**: Un día laboral válido debe satisfacer TODAS las condiciones:
1. El nombre del día aparece en la lista dias_trabajo
2. No es festivo (a menos que el empleado trabaje festivos)
3. Dentro de los límites de búsqueda de fechas

### 6.3 Precisión de Tiempo
**Regla**: Todos los tiempos usan formato de 24 horas con precisión de minutos
- **Formato**: "HH:MM:SS" (ej: "09:30:00")
- **Granularidad**: Operaciones realizadas en cálculos a nivel de minutos

## 7. Integración de Agenda CSV

### 7.1 Requisitos de Formato CSV
**Estructura**:
- **Columna 1**: Fecha en formato YYYY-MM-DD
- **Columnas Restantes**: Franjas de 15 minutos (1 = ocupado, 0 = libre)
- **Encabezados de Tiempo**: Formato "HH:MM" (ej: "09:00", "09:15")

**Ejemplo**:
```
date,07:00,07:15,07:30,08:00,08:15,08:30,09:00
2024-03-15,0,0,0,1,1,0,1
```

### 7.2 Detección de Bloques Ocupados
**Regla**: Convertir valores "1" consecutivos en bloques de tiempo
- **Inicio del Bloque**: Primer "1" en la secuencia
- **Fin del Bloque**: Último "1" en la secuencia + 15 minutos
- **Múltiples Bloques**: Bloques separados para períodos ocupados no consecutivos

**Implementación**: `test/utils/schedule_parser.py:find_busy_blocks()`

## 8. Estructura de Respuesta de la API

### 8.1 Respuesta de Agendamiento Exitoso
```json
{
  "current_date": "2024-03-04",
  "notification_date": "2024-03-04",
  "counting_start_date": "2024-03-05",
  "appointment_date": "2024-03-12",
  "appointment_time": "09:00:00",
  "is_schedulable": true,
  "reason": null
}
```

### 8.2 Respuesta de Agendamiento Fallido
```json
{
  "current_date": "2024-03-04",
  "notification_date": "2024-03-04",
  "counting_start_date": "2024-03-05",
  "appointment_date": "2024-03-12",
  "appointment_time": "00:00:00",
  "is_schedulable": false,
  "reason": "No common work days between employee and lawyer"
}
```

## 9. Referencias de Implementación

### Archivos Principales
- **API Principal**: `src/scheduler/main.py`
- **Modelos de Datos**: `src/scheduler/models.py`
- **Lógica de Fechas**: `src/scheduler/utils/date_calculator.py`
- **Validación de Horarios**: `src/scheduler/utils/schedule_validator.py`
- **Manejo de Festivos**: `src/scheduler/utils/holiday_handler.py`
- **Parser CSV**: `test/utils/schedule_parser.py`

### Cobertura de Pruebas
- **Pruebas BDD**: `test/appointment_scheduling.feature`
- **Pasos de Prueba**: `test/steps/appointment_steps.py`
- **Datos de Prueba**: `test/data/employee_schedule.csv`, `test/data/lawyer_schedule.csv`

---

*Última Actualización: Noviembre 2024*
*Versión del Sistema: 1.0.0*