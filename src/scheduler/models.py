from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time


class BusyMeeting(BaseModel):
    date: date
    start_time: time
    end_time: time


class BusySchedule(BaseModel):
    meetings: List[BusyMeeting]


class EmployeeConfig(BaseModel):
    work_days: List[str]
    start_time: time
    end_time: time
    works_holidays: bool


class LawyerConfig(BaseModel):
    work_days: List[str]
    non_work_days: List[str]
    start_time: time
    end_time: time


class AppointmentRequest(BaseModel):
    current_date: date
    current_time: time
    employee: EmployeeConfig
    lawyer: LawyerConfig
    holiday_dates: List[date]
    employee_schedule: Optional[BusySchedule] = None
    lawyer_schedule: Optional[BusySchedule] = None


class AppointmentResponse(BaseModel):
    current_date: date
    notification_date: date
    counting_start_date: date
    appointment_date: date
    appointment_time: time
    is_schedulable: bool
    reason: Optional[str] = None