import pandas as pd
from datetime import datetime, date, time, timedelta
from typing import List, Dict
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import AgendaResponse, EventoResponse
from services.configuracion_service import configuracion_service


class AgendaService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.time_columns = self._generate_time_columns()

    def _generate_time_columns(self) -> List[str]:
        """Generate column names for 15-minute intervals from 07:00 to 18:00"""
        columns = []
        start_hour = 7
        end_hour = 18

        current_time = datetime.strptime("07:00", "%H:%M")
        end_time = datetime.strptime("18:00", "%H:%M")

        while current_time < end_time:
            columns.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)

        return columns

    def get_agenda_abogado(self, fecha_inicio: datetime, fecha_fin: datetime) -> AgendaResponse:
        """Get lawyer's schedule for the given date range"""
        return self._get_agenda("agenda_abogado.csv", fecha_inicio, fecha_fin)

    def get_agenda_empleado(self, fecha_inicio: datetime, fecha_fin: datetime) -> AgendaResponse:
        """Get employee's schedule for the given date range"""
        return self._get_agenda("agenda_empleado.csv", fecha_inicio, fecha_fin)

    def _get_agenda(self, filename: str, fecha_inicio: datetime, fecha_fin: datetime) -> AgendaResponse:
        """Load agenda from CSV and process occupied time blocks"""
        file_path = self.data_dir / filename

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            return AgendaResponse(eventos=[])

        # Filter by date range
        df['fecha'] = pd.to_datetime(df['fecha'])
        mask = (df['fecha'] >= fecha_inicio.date()) & (df['fecha'] <= fecha_fin.date())
        filtered_df = df.loc[mask]

        # Get work configuration
        config = configuracion_service.load_configuracion()

        eventos = []

        for _, row in filtered_df.iterrows():
            fecha_dia = row['fecha'].date()
            dia_semana = self._get_day_name(fecha_dia)

            # Skip non-working days
            if not config.dias_laborales.get(dia_semana, False):
                continue

            # Process time blocks for this day
            day_eventos = self._process_day_schedule(row, fecha_dia)
            eventos.extend(day_eventos)

        return AgendaResponse(eventos=eventos)

    def _process_day_schedule(self, row: pd.Series, fecha_dia: date) -> List[EventoResponse]:
        """Process a single day's schedule and consolidate occupied blocks"""
        eventos = []
        current_block_start = None

        for time_column in self.time_columns:
            if time_column not in row:
                continue

            is_occupied = self._is_time_occupied(row[time_column])

            if is_occupied and current_block_start is None:
                # Start of new occupied block
                current_block_start = time_column
            elif not is_occupied and current_block_start is not None:
                # End of occupied block
                eventos.append(self._create_evento(fecha_dia, current_block_start, time_column))
                current_block_start = None

        # Handle case where day ends with occupied block
        if current_block_start is not None:
            # Use next 15-minute interval as end time
            last_time = datetime.strptime(self.time_columns[-1], "%H:%M")
            end_time = (last_time + timedelta(minutes=15)).strftime("%H:%M")
            eventos.append(self._create_evento(fecha_dia, current_block_start, end_time))

        return eventos

    def _is_time_occupied(self, value) -> bool:
        """Check if a time slot is occupied"""
        if pd.isna(value):
            return False

        if isinstance(value, bool):
            return value

        str_value = str(value).lower().strip()
        return str_value in ['true', '1', 'yes', 'si', 'occupied']

    def _create_evento(self, fecha_dia: date, start_time_str: str, end_time_str: str) -> EventoResponse:
        """Create an EventoResponse from date and time strings"""
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        fecha_inicio = datetime.combine(fecha_dia, start_time)
        fecha_fin = datetime.combine(fecha_dia, end_time)

        return EventoResponse(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

    def _get_day_name(self, fecha: date) -> str:
        """Get Spanish day name from date"""
        day_names = {
            0: "lunes",
            1: "martes",
            2: "miercoles",
            3: "jueves",
            4: "viernes",
            5: "sabado",
            6: "domingo"
        }
        return day_names[fecha.weekday()]


# Global instance
agenda_service = AgendaService()