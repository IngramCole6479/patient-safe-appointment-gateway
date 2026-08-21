from datetime import datetime, timezone

from appointment_service import run_workflow
from appointment_workflow import AppointmentRequest, AppointmentState


class RecordingWriter:
    def __init__(self) -> None:
        self.reason = ""

    def write_staff_note(self, reason: str) -> str:
        self.reason = reason
        return "Internal scheduling context."


def test_confirmed_notification_excludes_clinical_reason_and_staff_note() -> None:
    writer = RecordingWriter()
    request = AppointmentRequest(
        appointment_id="apt-1042",
        requested_start=datetime(2026, 8, 14, 9, 30, tzinfo=timezone.utc),
        reason="Persistent chest discomfort after exercise",
    )

    result = run_workflow(request, writer)

    assert result.state is AppointmentState.CONFIRMED
    assert result.patient_notification == (
        "Appointment apt-1042 is confirmed for 2026-08-14T09:30:00+00:00."
    )
    assert request.reason not in result.patient_notification
    assert result.staff_note not in result.patient_notification
    assert writer.reason == request.reason


def test_missing_slot_requests_scheduling_follow_up() -> None:
    result = run_workflow(
        AppointmentRequest(
            appointment_id="apt-1043",
            reason="Annual medication review",
        ),
        RecordingWriter(),
    )

    assert result.state is AppointmentState.NEEDS_SCHEDULING
    assert result.patient_notification == (
        "Appointment apt-1043 was received. Scheduling will contact you."
    )

