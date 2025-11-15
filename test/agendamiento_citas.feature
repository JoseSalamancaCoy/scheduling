Feature: Sistema de Agendamiento de Citas con Empleados
  Como un sistema de gestión de recursos humanos
  Quiero calcular automáticamente las fechas de notificación y agendamiento de citas
  Para cumplir con las reglas de negocio establecidas

  Background:
    Given que el sistema tiene acceso a la fecha actual
    And el abogado trabaja de "lunes" a "viernes" de "08:00" a "17:00"

  Scenario Outline: Calcular fecha de notificación cuando hoy es día hábil del empleado
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    Then la fecha de notificación debe ser "<fecha_notificacion>"
    And la fecha de inicio del conteo debe ser "<fecha_inicio_conteo>"
    And la fecha de la cita debe ser "<fecha_cita>"
    And la hora de la cita debe estar entre "<hora_cita_inicio>" y "<hora_cita_fin>"

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados | fecha_notificacion | fecha_inicio_conteo | fecha_cita | hora_cita_inicio | hora_cita_fin |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | []            | 2024-03-04         | 2024-03-05          | 2024-03-12 | 09:00           | 17:00         |
      | 2024-03-05   | ["lunes", "martes", "miércoles"]        | 10:00          | 19:00       | trabaja          | []            | 2024-03-05         | 2024-03-06          | 2024-03-13 | 10:00           | 17:00         |

  Scenario Outline: Calcular fecha de notificación cuando hoy es día no hábil del empleado
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    Then la fecha de notificación debe ser "<fecha_notificacion>"
    And la fecha de inicio del conteo debe ser "<fecha_inicio_conteo>"
    And la fecha de la cita debe ser "<fecha_cita>"

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados | fecha_notificacion | fecha_inicio_conteo | fecha_cita |
      | 2024-03-03   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | []            | 2024-03-04         | 2024-03-05          | 2024-03-12 |
      | 2024-03-07   | ["lunes", "miércoles", "viernes"]       | 10:00          | 16:00       | trabaja          | []            | 2024-03-08         | 2024-03-11          | 2024-03-20 |

  Scenario Outline: Manejo de días festivos
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    Then la fecha de notificación debe ser "<fecha_notificacion>"
    And la fecha de inicio del conteo debe ser "<fecha_inicio_conteo>"
    And la fecha de la cita debe ser "<fecha_cita>"

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados           | fecha_notificacion | fecha_inicio_conteo | fecha_cita |
      | 2024-12-25   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | trabaja          | ["2024-12-25"]         | 2024-12-25         | 2024-12-26          | 2025-01-02 |
      | 2024-12-25   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | ["2024-12-25"]         | 2024-12-26         | 2024-12-27          | 2025-01-03 |
      | 2024-01-01   | ["lunes", "martes", "miércoles"]        | 10:00          | 17:00       | no trabaja       | ["2024-01-01"]         | 2024-01-02         | 2024-01-03          | 2024-01-10 |

  Scenario Outline: Validación de compatibilidad horaria empleado-abogado
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    And se verifica la compatibilidad horaria
    Then <resultado_compatibilidad>

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados | resultado_compatibilidad                                                   |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | []            | debe existir traslape horario de "09:00" a "17:00"                       |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 18:00          | 22:00       | no trabaja       | []            | no debe existir traslape horario                                          |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 06:00          | 10:00       | no trabaja       | []            | debe existir traslape horario de "08:00" a "10:00"                       |
      | 2024-03-04   | ["sábado", "domingo"]                   | 09:00          | 18:00       | trabaja          | []            | no debe ser posible agendar - empleado y abogado no coinciden en días   |

  Scenario Outline: Casos extremos - Múltiples festivos consecutivos
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    Then la fecha de notificación debe ser "<fecha_notificacion>"
    And la fecha de inicio del conteo debe ser "<fecha_inicio_conteo>"
    And la fecha de la cita debe ser "<fecha_cita>"

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados                                    | fecha_notificacion | fecha_inicio_conteo | fecha_cita |
      | 2024-12-23   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | ["2024-12-25", "2024-12-26", "2025-01-01"]     | 2024-12-23         | 2024-12-24          | 2025-01-02 |
      | 2024-12-24   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | ["2024-12-25", "2024-12-26", "2025-01-01"]     | 2024-12-27         | 2024-12-30          | 2025-01-08 |

  Scenario Outline: Casos extremos - Empleado trabaja solo fines de semana
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    And se verifica la compatibilidad horaria
    Then no debe ser posible agendar la cita
    And el motivo debe ser "No hay días de trabajo comunes entre empleado y abogado"

    Examples:
      | fecha_actual | dias_trabajo_empleado     | horario_inicio | horario_fin | trabaja_festivos | dias_feriados |
      | 2024-03-04   | ["sábado", "domingo"]    | 09:00          | 18:00       | no trabaja       | []            |
      | 2024-03-09   | ["sábado", "domingo"]    | 10:00          | 16:00       | trabaja          | []            |

  Scenario Outline: Casos extremos - Sin traslape horario
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se calcula la fecha de notificación
    And se verifica la compatibilidad horaria
    Then no debe ser posible agendar la cita
    And el motivo debe ser "No hay traslape de horarios entre empleado y abogado"

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 18:00          | 22:00       | no trabaja       | []            |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 05:00          | 07:00       | trabaja          | []            |

  Scenario Outline: Validación de estructura de respuesta de la API
    Given que hoy es "<fecha_actual>"
    And el empleado trabaja los días: <dias_trabajo_empleado>
    And el empleado trabaja de "<horario_inicio>" a "<horario_fin>"
    And el empleado <trabaja_festivos> festivos
    And los días feriados son: <dias_feriados>
    When se ejecuta el proceso de agendamiento
    Then la respuesta debe contener:
      | campo                | tipo     | requerido |
      | fechaNotificacion   | string   | sí        |
      | fechaInicioConteo   | string   | sí        |
      | fechaCita           | string   | sí        |
      | horaCita            | string   | sí        |
      | esAgendable         | boolean  | sí        |
      | motivo              | string   | no        |

    Examples:
      | fecha_actual | dias_trabajo_empleado                    | horario_inicio | horario_fin | trabaja_festivos | dias_feriados |
      | 2024-03-04   | ["lunes", "martes", "miércoles"]        | 09:00          | 18:00       | no trabaja       | []            |