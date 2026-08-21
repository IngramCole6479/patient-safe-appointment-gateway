"""Deterministic appointment state and patient-safe notification policy."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AppointmentState(StrEnum):
    CONFIRMED = "confirmed"
    NEEDS_SCHEDULING = "needs_scheduling"


class AppointmentRequest(BaseModel):
    appointment_id: str = Field(min_length=1, max_length=80)
    requested_start: datetime | None = None
    reason: str = Field(min_length=1, max_length=1000)


class AppointmentResult(BaseModel):
    appointment_id: str
    state: AppointmentState
    patient_notification: str
    staff_note: str


def decide_state(requested_start: datetime | None) -> AppointmentState:
    """A supplied slot can be confirmed; otherwise scheduling must follow up."""
    if requested_start is None:
        return AppointmentState.NEEDS_SCHEDULING
    return AppointmentState.CONFIRMED


def patient_notification(
    appointment_id: str,
    state: AppointmentState,
    requested_start: datetime | None,
) -> str:
    """Render operational facts only. Clinical text never enters this boundary."""
    if state is AppointmentState.CONFIRMED:
        assert requested_start is not None
        start = requested_start.isoformat()
        return f"Appointment {appointment_id} is confirmed for {start}."
    return f"Appointment {appointment_id} was received. Scheduling will contact you."

