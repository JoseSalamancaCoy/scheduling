from datetime import date, timedelta
from typing import List


def is_holiday(date_to_check: date, holiday_dates: List[date]) -> bool:
    """
    Verifies if a date is a holiday.
    """
    return date_to_check in holiday_dates


def get_next_non_holiday(start_date: date, holiday_dates: List[date], max_days: int = 30) -> date:
    """
    Finds the next date that is not a holiday.
    """
    candidate_date = start_date
    days_searched = 0

    while is_holiday(candidate_date, holiday_dates) and days_searched < max_days:
        candidate_date += timedelta(days=1)
        days_searched += 1

    if days_searched >= max_days:
        raise ValueError(f"No non-holiday date found in {max_days} days")

    return candidate_date


def filter_holidays_for_employee(holiday_dates: List[date], works_holidays: bool) -> List[date]:
    """
    Filters holiday dates based on whether employee works holidays or not.

    Returns:
        List[date]: List of dates that should be considered as non-work days for the employee
    """
    if works_holidays:
        return []  # If works holidays, no holiday counts as non-work day
    else:
        return holiday_dates  # If doesn't work holidays, all holidays are non-work days


def count_holidays_in_period(start_date: date, end_date: date, holiday_dates: List[date]) -> int:
    """
    Counts how many holidays are in a specific period.
    """
    count = 0
    for holiday in holiday_dates:
        if start_date <= holiday <= end_date:
            count += 1
    return count


def get_holidays_in_period(start_date: date, end_date: date, holiday_dates: List[date]) -> List[date]:
    """
    Gets all holidays in a specific period.
    """
    holidays_in_period = []
    for holiday in holiday_dates:
        if start_date <= holiday <= end_date:
            holidays_in_period.append(holiday)

    return sorted(holidays_in_period)