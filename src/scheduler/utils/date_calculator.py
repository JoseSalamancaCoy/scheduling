from datetime import date, timedelta, time
from typing import List


def is_employee_work_day(date_to_check: date, work_days: List[str], holiday_dates: List[date], works_holidays: bool) -> bool:
    """
    Determines if a date is a work day for the employee.
    """
    # Convert date to day name in Spanish (keeping original day names for compatibility)
    week_days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    day_name = week_days[date_to_check.weekday()]

    # Check if employee works this day of the week
    if day_name not in work_days:
        return False

    # If it's a holiday and employee doesn't work holidays, it's not a work day
    if date_to_check in holiday_dates and not works_holidays:
        return False

    return True


def calculate_notification_date(current_date: date, current_time: time, work_days: List[str],
                               holiday_dates: List[date], works_holidays: bool,
                               start_time: time, end_time: time) -> date:
    """
    Calculates notification date according to business rules.
    Considers both work day and employee's work hours.
    """
    # If today is a work day and we're within work hours, notification is today
    if (is_employee_work_day(current_date, work_days, holiday_dates, works_holidays) and
        start_time <= current_time <= end_time):
        return current_date

    # If not a work day or work hours have passed, find next work day
    candidate_date = current_date + timedelta(days=1)

    while not is_employee_work_day(candidate_date, work_days, holiday_dates, works_holidays):
        candidate_date += timedelta(days=1)

        # Avoid infinite loop (maximum 30 days search)
        if (candidate_date - current_date).days > 30:
            raise ValueError("Could not find a work day in the next 30 days")

    return candidate_date


def calculate_counting_start_date(notification_date: date, work_days: List[str],
                                 holiday_dates: List[date], works_holidays: bool) -> date:
    """
    Calculates counting start date (notification date + 1 work day).
    """
    candidate_date = notification_date + timedelta(days=1)

    while not is_employee_work_day(candidate_date, work_days, holiday_dates, works_holidays):
        candidate_date += timedelta(days=1)

        # Avoid infinite loop
        if (candidate_date - notification_date).days > 30:
            raise ValueError("Could not find counting start date in the next 30 days")

    return candidate_date


def calculate_appointment_date(counting_start_date: date, work_days: List[str],
                              holiday_dates: List[date], works_holidays: bool) -> date:
    """
    Calculates appointment date (5 work days after counting start date).
    """
    work_days_counted = 0
    candidate_date = counting_start_date + timedelta(days=1)  # Start the day after

    while work_days_counted < 5:
        if is_employee_work_day(candidate_date, work_days, holiday_dates, works_holidays):
            work_days_counted += 1
            if work_days_counted == 5:
                break

        candidate_date += timedelta(days=1)

        # Avoid infinite loop
        if (candidate_date - counting_start_date).days > 60:
            raise ValueError("Could not calculate appointment date in the next 60 days")

    return candidate_date


def find_next_compatible_date(start_date: date, employee_work_days: List[str],
                             lawyer_work_days: List[str], holiday_dates: List[date],
                             works_holidays: bool, max_days: int = 30) -> date:
    """
    Finds the next date when both employee and lawyer can work.
    """
    week_days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    candidate_date = start_date
    days_searched = 0

    while days_searched < max_days:
        day_name = week_days[candidate_date.weekday()]

        # Check if employee can work this day
        employee_can_work = is_employee_work_day(candidate_date, employee_work_days, holiday_dates, works_holidays)

        # Check if lawyer can work this day
        lawyer_can_work = day_name in lawyer_work_days

        if employee_can_work and lawyer_can_work:
            return candidate_date

        candidate_date += timedelta(days=1)
        days_searched += 1

    raise ValueError(f"No compatible date found in {max_days} days")


def calculate_compatible_appointment_date(counting_start_date: date, employee_work_days: List[str],
                                         lawyer_work_days: List[str], holiday_dates: List[date],
                                         works_holidays: bool) -> date:
    """
    Calculates appointment date considering compatibility between employee and lawyer.
    First counts 5 employee work days, then finds compatible date if necessary.
    """
    # First calculate ideal date based on employee
    ideal_date = calculate_appointment_date(counting_start_date, employee_work_days, holiday_dates, works_holidays)

    # Check if lawyer can work on that date
    week_days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    ideal_day = week_days[ideal_date.weekday()]

    # If lawyer can also work that date, use that date
    if ideal_day in lawyer_work_days:
        return ideal_date

    # If not, find next compatible date
    return find_next_compatible_date(ideal_date, employee_work_days, lawyer_work_days,
                                   holiday_dates, works_holidays)