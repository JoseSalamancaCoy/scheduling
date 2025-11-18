from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import time
import logging

from models import AppointmentRequest, AppointmentResponse
from utils.date_calculator import (
    calculate_notification_date,
    calculate_counting_start_date,
    calculate_compatible_appointment_date
)
from utils.schedule_validator import validate_full_compatibility, validate_compatibility_with_schedules
from utils.holiday_handler import filter_holidays_for_employee

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appointment Scheduling API",
    description="API for calculating scheduling dates according to specific business rules",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Appointment Scheduling API - v1.0.0"}


@app.post("/schedule-appointment", response_model=AppointmentResponse)
async def schedule_appointment(request: AppointmentRequest):
    """
    Main endpoint for scheduling an appointment according to business rules.

    Calculates:
    - Employee notification date
    - Counting start date
    - Appointment date
    - Appointment time (within overlap hours)
    - Compatibility validations
    """
    try:
        # Filter holidays according to whether employee works holidays
        effective_holiday_dates = filter_holidays_for_employee(
            request.holiday_dates,
            request.employee.works_holidays
        )

        logger.info(f"Processing appointment for current date: {request.current_date}")

        # 1. Calculate notification date
        notification_date = calculate_notification_date(
            request.current_date,
            request.current_time,
            request.employee.work_days,
            effective_holiday_dates,
            request.employee.works_holidays,
            request.employee.start_time,
            request.employee.end_time
        )

        logger.info(f"Calculated notification date: {notification_date}")

        # 2. Calculate counting start date
        counting_start_date = calculate_counting_start_date(
            notification_date,
            request.employee.work_days,
            effective_holiday_dates,
            request.employee.works_holidays
        )

        logger.info(f"Counting start date: {counting_start_date}")

        # 3. Calculate appointment date (considering compatibility)
        try:
            appointment_date = calculate_compatible_appointment_date(
                counting_start_date,
                request.employee.work_days,
                request.lawyer.work_days,
                effective_holiday_dates,
                request.employee.works_holidays
            )
            logger.info(f"Calculated appointment date: {appointment_date}")

            # 4. Validate schedule compatibility between employee and lawyer considering schedules
            if request.employee_schedule or request.lawyer_schedule:
                # Use validation with schedules if provided
                is_compatible, incompatibility_reason, schedule_overlap = validate_compatibility_with_schedules(
                    request.employee.work_days,
                    request.lawyer.work_days,
                    request.employee.start_time,
                    request.employee.end_time,
                    request.lawyer.start_time,
                    request.lawyer.end_time,
                    appointment_date,
                    request.employee_schedule,
                    request.lawyer_schedule
                )
            else:
                # Use traditional validation if no schedules provided
                is_compatible, incompatibility_reason, schedule_overlap = validate_full_compatibility(
                    request.employee.work_days,
                    request.lawyer.work_days,
                    request.employee.start_time,
                    request.employee.end_time,
                    request.lawyer.start_time,
                    request.lawyer.end_time,
                    appointment_date
                )

            if not is_compatible:
                logger.warning(f"Appointment not schedulable: {incompatibility_reason}")
                return AppointmentResponse(
                    current_date=request.current_date,
                    notification_date=notification_date,
                    counting_start_date=counting_start_date,
                    appointment_date=appointment_date,
                    appointment_time=time(0, 0),  # Default time when not schedulable
                    is_schedulable=False,
                    reason=incompatibility_reason
                )

        except ValueError as ve:
            # Could not find compatible date
            logger.warning(f"Could not find compatible date: {str(ve)}")
            from utils.date_calculator import calculate_appointment_date
            # Calculate date based only on employee for response purposes
            appointment_date = calculate_appointment_date(
                counting_start_date,
                request.employee.work_days,
                effective_holiday_dates,
                request.employee.works_holidays
            )

            return AppointmentResponse(
                current_date=request.current_date,
                notification_date=notification_date,
                counting_start_date=counting_start_date,
                appointment_date=appointment_date,
                appointment_time=time(0, 0),  # Default time when not schedulable
                is_schedulable=False,
                reason="No common work days between employee and lawyer"
            )

        # 5. Determine appointment time (start of schedule overlap)
        appointment_time = schedule_overlap[0]

        logger.info(f"Appointment successfully scheduled for {appointment_date} at {appointment_time}")

        return AppointmentResponse(
            current_date=request.current_date,
            notification_date=notification_date,
            counting_start_date=counting_start_date,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            is_schedulable=True,
            reason=None
        )

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)