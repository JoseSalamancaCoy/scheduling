from datetime import date, time
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import BusySchedule


def verify_common_days(employee_work_days: List[str], lawyer_work_days: List[str]) -> bool:
    """
    Verifies if employee and lawyer have common work days.
    """
    return bool(set(employee_work_days) & set(lawyer_work_days))


def calculate_schedule_overlap(employee_start_time: time, employee_end_time: time,
                              lawyer_start_time: time, lawyer_end_time: time) -> Optional[Tuple[time, time]]:
    """
    Calculates schedule overlap between employee and lawyer.
    Returns None if no overlap, or tuple (start, end) of overlap.
    """
    # Convert to minutes for easier calculations
    emp_start_min = employee_start_time.hour * 60 + employee_start_time.minute
    emp_end_min = employee_end_time.hour * 60 + employee_end_time.minute
    lawyer_start_min = lawyer_start_time.hour * 60 + lawyer_start_time.minute
    lawyer_end_min = lawyer_end_time.hour * 60 + lawyer_end_time.minute

    # Calculate overlap start and end
    overlap_start_min = max(emp_start_min, lawyer_start_min)
    overlap_end_min = min(emp_end_min, lawyer_end_min)

    # If no overlap (start >= end)
    if overlap_start_min >= overlap_end_min:
        return None

    # Convert back to time
    overlap_start = time(overlap_start_min // 60, overlap_start_min % 60)
    overlap_end = time(overlap_end_min // 60, overlap_end_min % 60)

    return (overlap_start, overlap_end)


def exclude_lunch_hours(overlap: Tuple[time, time],
                       lunch_start: time = time(12, 0),
                       lunch_end: time = time(14, 0)) -> List[Tuple[time, time]]:
    """
    Excludes lunch hours from schedule overlap.
    Returns a list of valid segments (may be empty).
    """
    start, end = overlap

    # Convert to minutes
    start_min = start.hour * 60 + start.minute
    end_min = end.hour * 60 + end.minute
    lunch_start_min = lunch_start.hour * 60 + lunch_start.minute
    lunch_end_min = lunch_end.hour * 60 + lunch_end.minute

    segments = []

    # Segment before lunch
    if start_min < lunch_start_min and end_min > start_min:
        end_before_lunch = min(end_min, lunch_start_min)
        if end_before_lunch > start_min:
            start_seg = time(start_min // 60, start_min % 60)
            end_seg = time(end_before_lunch // 60, end_before_lunch % 60)
            segments.append((start_seg, end_seg))

    # Segment after lunch
    if end_min > lunch_end_min and start_min < end_min:
        start_after_lunch = max(start_min, lunch_end_min)
        if end_min > start_after_lunch:
            start_seg = time(start_after_lunch // 60, start_after_lunch % 60)
            end_seg = time(end_min // 60, end_min % 60)
            segments.append((start_seg, end_seg))

    return segments


def find_valid_appointment_time(segments: List[Tuple[time, time]],
                               minimum_duration_minutes: int = 60) -> Optional[time]:
    """
    Finds the first valid time to schedule an appointment in available segments.
    """
    for start, end in segments:
        # Check if segment has sufficient duration
        start_min = start.hour * 60 + start.minute
        end_min = end.hour * 60 + end.minute
        duration = end_min - start_min

        if duration >= minimum_duration_minutes:
            return start

    return None


def validate_minimum_appointment_duration(overlap: Tuple[time, time], minimum_duration_minutes: int = 60) -> bool:
    """
    Validates that schedule overlap is sufficient for appointment duration.
    """
    start, end = overlap

    start_min = start.hour * 60 + start.minute
    end_min = end.hour * 60 + end.minute

    overlap_duration = end_min - start_min

    return overlap_duration >= minimum_duration_minutes


def validate_full_compatibility(employee_work_days: List[str], lawyer_work_days: List[str],
                               employee_start_time: time, employee_end_time: time,
                               lawyer_start_time: time, lawyer_end_time: time,
                               appointment_date: date) -> Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
    """
    Validates full compatibility between employee and lawyer.
    Excludes lunch hours (12:00-14:00).

    Returns:
        Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
        - bool: True if compatible
        - str: Incompatibility reason if applicable
        - Tuple[time, time]: (appointment_start_time, available_end_time) if schedulable
    """
    # Verify common days
    if not verify_common_days(employee_work_days, lawyer_work_days):
        return False, "No common work days between employee and lawyer", None

    # Verify that appointment date is a day both work
    week_days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    appointment_day = week_days[appointment_date.weekday()]

    if appointment_day not in employee_work_days:
        return False, f"Employee doesn't work on {appointment_day}", None

    if appointment_day not in lawyer_work_days:
        return False, f"Lawyer doesn't work on {appointment_day}", None

    # Calculate basic schedule overlap
    basic_overlap = calculate_schedule_overlap(
        employee_start_time, employee_end_time,
        lawyer_start_time, lawyer_end_time
    )

    if basic_overlap is None:
        return False, "No schedule overlap between employee and lawyer", None

    # Exclude lunch hours from overlap
    valid_segments = exclude_lunch_hours(basic_overlap)

    # Find valid time for appointment
    valid_appointment_time = find_valid_appointment_time(valid_segments)

    if valid_appointment_time is None:
        return False, "No available times outside lunch hours (12:00-14:00)", None

    # Create tuple with appointment start time and end of first valid segment
    first_segment = next((seg for seg in valid_segments
                         if seg[0] == valid_appointment_time), None)

    if first_segment:
        return True, None, first_segment
    else:
        return False, "Error determining valid segment", None


def verify_schedule_conflict(start_time: time, end_time: time,
                            schedule: 'BusySchedule', appointment_date: date) -> bool:
    """
    Verifies if there's conflict with existing meetings in schedule for specific date.

    Returns:
        True if there's conflict, False if no conflict
    """
    if schedule is None or not schedule.meetings:
        return False

    # Filter meetings for specific date
    date_meetings = [m for m in schedule.meetings if m.date == appointment_date]

    for meeting in date_meetings:
        # Check if there's overlap
        if (start_time < meeting.end_time and end_time > meeting.start_time):
            return True

    return False


def find_free_segments(overlap_segments: List[Tuple[time, time]],
                      employee_schedule: Optional['BusySchedule'],
                      lawyer_schedule: Optional['BusySchedule'],
                      appointment_date: date) -> List[Tuple[time, time]]:
    """
    Filters overlap segments excluding busy periods
    from employee and lawyer schedules.
    """
    free_segments = []

    for segment_start, segment_end in overlap_segments:
        # Divide segment into free periods
        free_periods = [(segment_start, segment_end)]

        # Process employee schedule
        if employee_schedule and employee_schedule.meetings:
            employee_meetings = [m for m in employee_schedule.meetings if m.date == appointment_date]
            for meeting in employee_meetings:
                updated_periods = []
                for period_start, period_end in free_periods:
                    # If there's overlap, divide the period
                    if (period_start < meeting.end_time and period_end > meeting.start_time):
                        # Period before meeting
                        if period_start < meeting.start_time:
                            updated_periods.append((period_start, meeting.start_time))
                        # Period after meeting
                        if period_end > meeting.end_time:
                            updated_periods.append((meeting.end_time, period_end))
                    else:
                        # No overlap, keep the period
                        updated_periods.append((period_start, period_end))
                free_periods = updated_periods

        # Process lawyer schedule
        if lawyer_schedule and lawyer_schedule.meetings:
            lawyer_meetings = [m for m in lawyer_schedule.meetings if m.date == appointment_date]
            for meeting in lawyer_meetings:
                updated_periods = []
                for period_start, period_end in free_periods:
                    # If there's overlap, divide the period
                    if (period_start < meeting.end_time and period_end > meeting.start_time):
                        # Period before meeting
                        if period_start < meeting.start_time:
                            updated_periods.append((period_start, meeting.start_time))
                        # Period after meeting
                        if period_end > meeting.end_time:
                            updated_periods.append((meeting.end_time, period_end))
                    else:
                        # No overlap, keep the period
                        updated_periods.append((period_start, period_end))
                free_periods = updated_periods

        free_segments.extend(free_periods)

    # Filter segments with minimum duration and sort
    valid_segments = []
    for start, end in free_segments:
        start_min = start.hour * 60 + start.minute
        end_min = end.hour * 60 + end.minute
        if end_min - start_min >= 60:  # Minimum 1 hour
            valid_segments.append((start, end))

    return sorted(valid_segments, key=lambda x: (x[0].hour * 60 + x[0].minute))


def validate_compatibility_with_schedules(employee_work_days: List[str],
                                         lawyer_work_days: List[str],
                                         employee_start_time: time,
                                         employee_end_time: time,
                                         lawyer_start_time: time,
                                         lawyer_end_time: time,
                                         appointment_date: date,
                                         employee_schedule: Optional['BusySchedule'] = None,
                                         lawyer_schedule: Optional['BusySchedule'] = None
                                         ) -> Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
    """
    Validates full compatibility between employee and lawyer considering their busy schedules.
    Excludes lunch hours (12:00-14:00) and existing meetings.

    Returns:
        Tuple[bool, Optional[str], Optional[Tuple[time, time]]]:
        - bool: True if compatible
        - str: Incompatibility reason if applicable
        - Tuple[time, time]: (appointment_start_time, available_end_time) if schedulable
    """
    # Verify common days
    if not verify_common_days(employee_work_days, lawyer_work_days):
        return False, "No common work days between employee and lawyer", None

    # Verify that appointment date is a day both work
    week_days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    appointment_day = week_days[appointment_date.weekday()]

    if appointment_day not in employee_work_days:
        return False, f"Employee doesn't work on {appointment_day}", None

    if appointment_day not in lawyer_work_days:
        return False, f"Lawyer doesn't work on {appointment_day}", None

    # Calculate basic schedule overlap
    basic_overlap = calculate_schedule_overlap(
        employee_start_time, employee_end_time,
        lawyer_start_time, lawyer_end_time
    )

    if basic_overlap is None:
        return False, "No schedule overlap between employee and lawyer", None

    # Exclude lunch hours from overlap
    segments_without_lunch = exclude_lunch_hours(basic_overlap)

    if not segments_without_lunch:
        return False, "No available times outside lunch hours (12:00-14:00)", None

    # Exclude busy periods from schedules
    free_segments = find_free_segments(
        segments_without_lunch, employee_schedule, lawyer_schedule, appointment_date
    )

    # Find valid time for appointment
    valid_appointment_time = find_valid_appointment_time(free_segments)

    if valid_appointment_time is None:
        return False, "No available times considering busy schedules", None

    # Create tuple with appointment start time and end of first valid segment
    first_segment = next((seg for seg in free_segments
                         if seg[0] == valid_appointment_time), None)

    if first_segment:
        return True, None, first_segment
    else:
        return False, "Error determining valid segment", None