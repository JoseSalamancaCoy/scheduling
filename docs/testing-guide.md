# 🧪 Guía de Pruebas - Sistema de Agendamiento

Esta guía explica cómo configurar, ejecutar y personalizar las pruebas del sistema de agendamiento de citas para validar completamente las reglas de negocio.

## 📁 Estructura de Pruebas

```
test/
├── appointment_scheduling.feature     # Escenarios BDD en español
├── steps/
│   └── appointment_steps.py          # Implementación de pasos de prueba
├── data/                             # Datos de configuración
│   ├── employee_schedule.csv         # Agenda ocupada del empleado
│   ├── lawyer_schedule.csv           # Agenda ocupada del abogado
│   └── work_configuration.json       # Configuración de días laborales
└── utils/
    └── schedule_parser.py            # Parser para archivos CSV
```

## 🛠️ Configuración de Datos de Prueba

### 1. Configuración de Agendas Ocupadas (CSV)

Los archivos CSV definen los períodos ocupados para empleado y abogado en franjas de 15 minutos.

#### Formato CSV Requerido

```csv
fecha,07:00,07:15,07:30,07:45,08:00,08:15,08:30,08:45,09:00,09:15,09:30,09:45,10:00,10:15,10:30,10:45,11:00,11:15,11:30,11:45,12:00,12:15,12:30,12:45,13:00,13:15,13:30,13:45,14:00,14:15,14:30,14:45,15:00,15:15,15:30,15:45,16:00,16:15,16:30,16:45,17:00,17:15,17:30,17:45
```

#### Reglas de Configuración CSV

- **Columna 1**: `fecha` en formato YYYY-MM-DD
- **Columnas 2-N**: Franjas de 15 minutos desde 07:00 hasta 17:45
- **Valores**:
  - `1` = Ocupado (reunión existente)
  - `0` = Libre (disponible para citas)

#### Ejemplo de Configuración

```csv
fecha,07:00,07:15,07:30,07:45,08:00,08:15,08:30,08:45,09:00,09:15,09:30,09:45,10:00,10:15,10:30,10:45,11:00,11:15,11:30,11:45,12:00,12:15,12:30,12:45,13:00,13:15,13:30,13:45,14:00,14:15,14:30,14:45,15:00,15:15,15:30,15:45,16:00,16:15,16:30,16:45,17:00,17:15,17:30,17:45
2024-03-15,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0
2024-03-16,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0
```

**Interpretación del ejemplo**:
- **2024-03-15**: Ocupado de 08:00-09:00 y 15:00-16:00
- **2024-03-16**: Ocupado de 09:00-10:00 y 16:00-17:00


## 📅 Sincronización de Rangos de Fechas

### Principio Fundamental

**CRÍTICO**: Los datos de prueba CSV deben cubrir el mismo rango de fechas que se usa en los escenarios de prueba para garantizar validación completa de las reglas de negocio.

### Cálculo de Rango de Fechas Necesario

Para cada escenario de prueba con `fecha_actual = "2024-03-04"`:

1. **Fecha Base**: 2024-03-04 (lunes)
2. **Fecha de Cita Calculada**: ~2024-03-12 (después de 5 días hábiles)
3. **Rango CSV Requerido**: 2024-03-04 hasta 2024-03-12 (mínimo)

### Ejemplo de Sincronización

Si tienes un escenario de prueba:
```gherkin
Given que hoy es "2024-03-04"
```

Tu CSV debe incluir **al menos** estas fechas:
```csv
fecha,07:00,07:15,[...],17:45
2024-03-04,0,0,[...],0
2024-03-05,0,0,[...],0
2024-03-06,0,0,[...],0
2024-03-07,0,0,[...],0
2024-03-08,0,0,[...],0
2024-03-09,0,0,[...],0
2024-03-10,0,0,[...],0
2024-03-11,0,0,[...],0
2024-03-12,0,0,[...],0
```

### Herramienta de Validación de Rango

Puedes verificar que tus CSVs cubren las fechas necesarias:

```python
def validar_cobertura_fechas(fecha_actual, csv_empleado, csv_abogado):
    from datetime import datetime, timedelta

    # Calcular rango necesario (fecha actual + 15 días para margen)
    inicio = datetime.strptime(fecha_actual, "%Y-%m-%d")
    fin = inicio + timedelta(days=15)

    # Verificar que ambos CSVs cubren el rango
    fechas_necesarias = []
    current = inicio
    while current <= fin:
        fechas_necesarias.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    print(f"Fechas necesarias: {fechas_necesarias}")
    # Verificar contra fechas en CSV...
```

## 🎯 Configuración de Escenarios de Prueba

### 1. Escenarios Básicos

Para probar la lógica fundamental sin conflictos de agenda:

```csv
# Empleado completamente libre
fecha,07:00,07:15,07:30,07:45,08:00,08:15,08:30,08:45,09:00,09:15,09:30,09:45,10:00,10:15,10:30,10:45,11:00,11:15,11:30,11:45,12:00,12:15,12:30,12:45,13:00,13:15,13:30,13:45,14:00,14:15,14:30,14:45,15:00,15:15,15:30,15:45,16:00,16:15,16:30,16:45,17:00,17:15,17:30,17:45
2024-03-04,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
2024-03-05,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### 2. Escenarios de Conflicto

Para probar detección de conflictos en horarios específicos:

```csv
# Conflicto en horario matutino (09:00-10:00)
fecha,07:00,07:15,07:30,07:45,08:00,08:15,08:30,08:45,09:00,09:15,09:30,09:45,10:00,10:15,10:30,10:45,11:00,11:15,11:30,11:45,12:00,12:15,12:30,12:45,13:00,13:15,13:30,13:45,14:00,14:15,14:30,14:45,15:00,15:15,15:30,15:45,16:00,16:15,16:30,16:45,17:00,17:15,17:30,17:45
2024-03-12,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### 3. Escenarios de Almuerzo

Para validar exclusión de horario 12:00-14:00:

```csv
# Solo disponible durante horario de almuerzo
fecha,07:00,07:15,07:30,07:45,08:00,08:15,08:30,08:45,09:00,09:15,09:30,09:45,10:00,10:15,10:30,10:45,11:00,11:15,11:30,11:45,12:00,12:15,12:30,12:45,13:00,13:15,13:30,13:45,14:00,14:15,14:30,14:45,15:00,15:15,15:30,15:45,16:00,16:15,16:30,16:45,17:00,17:15,17:30,17:45
2024-03-12,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
```

## ⚙️ Ejecución de Pruebas

### Comandos Básicos

```bash
# Ejecutar todas las pruebas
behave test/

# Ejecutar con salida detallada
behave test/ -v

# Ejecutar escenarios específicos
behave test/ -n "horario de almuerzo"

# Ejecutar con tags específicos
behave test/ --tags=@crítico
```

### Configuración de Entorno

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias de testing
pip install behave colorama

# Verificar configuración
python -c "import behave; print('Behave configurado correctamente')"
```

## 📊 Tipos de Validación

### 1. Validación de Reglas Fundamentales

- ✅ Cálculo de fechas (notificación, conteo, cita)
- ✅ Días laborales y festivos
- ✅ Horarios de trabajo y compatibilidad

### 2. Validación de Conflictos

- ✅ Detección de reuniones existentes
- ✅ Traslape de horarios
- ✅ Exclusión de almuerzo (12:00-14:00)

### 3. Validación de Casos Extremos

- ✅ Sin días comunes entre empleado y abogado
- ✅ Sin traslape horario
- ✅ Múltiples festivos consecutivos

## 🔧 Personalización de Pruebas

### Crear Nuevos Escenarios

1. **Definir el caso de uso**
2. **Calcular fechas necesarias**
3. **Crear datos CSV correspondientes**
4. **Agregar escenario en .feature**

### Ejemplo de Personalización

Para probar un empleado que trabaja sábados:

```gherkin
Scenario: Empleado trabaja sábados
  Given que hoy es "2024-03-09"  # sábado
  And el empleado trabaja los días: ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
  When se calcula la fecha de notificación
  Then la fecha de notificación debe ser "2024-03-09"
```

CSV correspondiente:
```csv
fecha,07:00,[...],17:45
2024-03-09,0,0,[...],0  # sábado libre
2024-03-11,0,0,[...],0  # lunes libre
2024-03-18,0,0,[...],0  # fecha de cita
```

## 📋 Checklist de Configuración

Antes de ejecutar pruebas, verifica:

- [ ] **Rango de fechas**: CSV cubre todas las fechas de los escenarios
- [ ] **Formato correcto**: Columnas de tiempo en formato HH:MM
- [ ] **Valores válidos**: Solo 0 y 1 en celdas de ocupación
- [ ] **Consistencia**: Datos de empleado y abogado en mismo rango
- [ ] **Horarios laborales**: JSON sincronizado con horarios de prueba
- [ ] **Dependencias**: behave y colorama instalados
- [ ] **Rutas**: Archivos en ubicaciones correctas (`test/data/`)

## 🎯 Mejores Prácticas

### 1. Mantenimiento de Datos

- **Actualizar fechas regularmente** para evitar fechas vencidas
- **Usar fechas relativas** cuando sea posible
- **Documentar escenarios complejos** con comentarios

### 2. Organización de Escenarios

- **Agrupar por funcionalidad** (básicos, conflictos, extremos)
- **Usar nombres descriptivos** para escenarios
- **Mantener datos mínimos** necesarios para cada prueba

### 3. Validación Continua

- **Ejecutar pruebas regularmente** durante desarrollo
- **Verificar cobertura completa** de reglas de negocio
- **Documentar cambios** en datos de prueba

---

**Configuración validada**: ✅ Todas las reglas de negocio
**Última actualización**: Noviembre 2024