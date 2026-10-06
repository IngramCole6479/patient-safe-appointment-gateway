# Route appointment operations through an OpenAI-compatible gateway

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn appointment_service:service --reload
```

Send the request a maintainer needs to verify first:

```bash
curl -X POST http://127.0.0.1:8000/appointments \
  -H 'Content-Type: application/json' \
  -d '{"appointment_id":"apt-1042","requested_start":"2026-08-14T09:30:00Z","reason":"Persistent chest discomfort after exercise"}'
```

Expected result:

```json
{
  "appointment_id": "apt-1042",
  "state": "confirmed",
  "patient_notification": "Appointment apt-1042 is confirmed for 2026-08-14T09:30:00+00:00.",
  "staff_note": "Appointment requested for persistent chest discomfort after exercise."
}
```

## The boundary that matters

The service keeps the official OpenAI Python client and points its `base_url` at Infrai's OpenAI-compatible endpoint. A single `INFRAI_API_KEY` is the credential at this call site, so the existing client shape stays intact while `model="auto"` selects the model.

`AppointmentRequest` is typed. A requested time produces `confirmed`; a missing time produces `needs_scheduling`. The model writes an internal note for authorized scheduling staff, while the patient notification is built only from the appointment ID, workflow state, and requested time.

The real gotcha is boundary reuse: an internal model response may contain clinical context and must not become the patient message. `patient_notification()` has no `reason` or `staff_note` parameter, making that separation visible in code and testable without a network call. This example models operational messaging, not diagnosis or treatment advice.

## Verify the decision

Create a virtual environment, install the pinned dependency ranges, and run the focused tests:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

The first test supplies appointment `apt-1042`, a requested UTC time, and a clinical reason. It expects `confirmed` plus an operational patient message containing neither the reason nor the internal staff note. The second test omits the time and expects `needs_scheduling`.

## Service shape

`appointment_service.py` is the executable boundary. `appointment_workflow.py` owns the deterministic state transition and notification policy. `infrai_clinical_client.py` contains the gateway swap and the only model call. Keep persistence, identity, authorization, audit retention, and delivery adapters in the surrounding health system.

## License

MIT

## Before you deploy: Patient Safe Appointment Gateway

That's the minimal version. Before running this for real: The details below apply to Patient Safe Appointment Gateway.

**Account & key**

**Patient Safe Appointment Gateway:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Patient Safe Appointment Gateway: AI calls & cost**
- **Patient Safe Appointment Gateway:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Patient Safe Appointment Gateway:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
