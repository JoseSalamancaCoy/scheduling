import csv
import sys
import os
from datetime import date, time, timedelta, datetime
from typing import List, Tuple

# Add src directory to path for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'scheduler'))

from models import BusyMeeting, BusySchedule


def parse_time_from_header(header_time: str) -> time:
    """
    Converts a time string from CSV header (e.g., '07:00') to a time object.
    """
    return time.fromisoformat(header_time + ":00")


def find_busy_blocks(row_data: List[str], time_headers: List[str]) -> List[Tuple[time, time]]:
    """
    Finds consecutive blocks where the value is '1' (busy).
    Returns a list of tuples (start_time, end_time).
    """
    blocks = []
    block_start = None

    for i, value in enumerate(row_data):
        if value == '1':  # Busy
            if block_start is None:
                block_start = i
        else:  # Free or end of data
            if block_start is not None:
                # End current block
                start_time = parse_time_from_header(time_headers[block_start])
                # End time is start of next slot (15 min after last busy slot)
                last_busy_slot = i - 1
                last_slot_time = parse_time_from_header(time_headers[last_busy_slot])
                # Add 15 minutes to get end time
                datetime_temp = datetime.combine(date.today(), last_slot_time)
                datetime_end = datetime_temp + timedelta(minutes=15)
                end_time = datetime_end.time()

                blocks.append((start_time, end_time))
                block_start = None

    # If file ends with a busy block
    if block_start is not None:
        start_time = parse_time_from_header(time_headers[block_start])
        last_busy_slot = len(row_data) - 1
        last_slot_time = parse_time_from_header(time_headers[last_busy_slot])
        # Add 15 minutes to get end time
        datetime_temp = datetime.combine(date.today(), last_slot_time)
        datetime_end = datetime_temp + timedelta(minutes=15)
        end_time = datetime_end.time()

        blocks.append((start_time, end_time))

    return blocks


def parse_csv_schedule(file_path: str) -> BusySchedule:
    """
    Parses a schedule CSV file and returns a BusySchedule object.

    Expected CSV format:
    - First column: date in YYYY-MM-DD format
    - Rest of columns: 15-minute time slots (1 = busy, 0 = free)
    """
    meetings = []

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # First row with headers

        # Extract time headers (ignore first column 'date')
        time_headers = headers[1:]

        for row in reader:
            date_str = row[0]
            date_obj = date.fromisoformat(date_str)

            # Occupancy data (ignore first column which is date)
            occupancy_data = row[1:]

            # Find busy time blocks
            busy_blocks = find_busy_blocks(occupancy_data, time_headers)

            # Create meetings for each busy block
            for start_time, end_time in busy_blocks:
                meeting = BusyMeeting(
                    date=date_obj,
                    start_time=start_time,
                    end_time=end_time
                )
                meetings.append(meeting)

    return BusySchedule(meetings=meetings)


def build_schedules_from_files(data_path: str) -> Tuple[BusySchedule, BusySchedule]:
    """
    Builds employee and lawyer schedules from CSV files.

    Args:
        data_path: Base path where data files are located

    Returns:
        Tuple with (employee_schedule, lawyer_schedule)
    """
    employee_path = os.path.join(data_path, "employee_schedule.csv")
    lawyer_path = os.path.join(data_path, "lawyer_schedule.csv")

    employee_schedule = parse_csv_schedule(employee_path)
    lawyer_schedule = parse_csv_schedule(lawyer_path)

    return employee_schedule, lawyer_schedule