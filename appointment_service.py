"""Executable HTTP service for the appointment workflow."""

from fastapi import FastAPI

from appointment_workflow import (
    AppointmentRequest,
    AppointmentResult,
    decide_state,
    patient_notification,
)
from infrai_clinical_client import InfraiClinicalClient, StaffNoteWriter

service = FastAPI(title="Appointment operations gateway")


def run_workflow(request: AppointmentRequest, writer: StaffNoteWriter) -> AppointmentResult:
    state = decide_state(request.requested_start)
    return AppointmentResult(
        appointment_id=request.appointment_id,
        state=state,
        patient_notification=patient_notification(
            request.appointment_id,
            state,
            request.requested_start,
        ),
        staff_note=writer.write_staff_note(request.reason),
    )


@service.post("/appointments", response_model=AppointmentResult)
def create_appointment(request: AppointmentRequest) -> AppointmentResult:
    return run_workflow(request, InfraiClinicalClient())

