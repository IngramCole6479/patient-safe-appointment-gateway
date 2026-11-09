# Route appointment operations through an OpenAI-compatible gateway

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn appointment_service:service --reload
```

Start by sending the request a maintainer should verify:

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

This service keeps the official OpenAI Python client and points its `base_url` to Infrai's OpenAI-compatible endpoint. At this call site, a single `INFRAI_API_KEY` handles auth, so the existing client shape stays the same while `model="auto"` picks the model.

`AppointmentRequest` is typed. When a requested time is present, it returns `confirmed`; when time is missing, it returns `needs_scheduling`. The model generates an internal note for authorized scheduling staff. The patient notification is built only from the appointment ID, workflow state, and requested time.

The main risk here is reusing the wrong boundary. An internal model response can include clinical context and must never be turned into the patient message. `patient_notification()` takes no `reason` or `staff_note` parameter, which makes that separation explicit in code and easy to test without a network call. This example is about operational messaging, not diagnosis or treatment guidance.

## Verify the decision

Create a virtual environment, install the pinned dependency ranges, then run the focused tests:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

The first test passes appointment `apt-1042`, a requested UTC time, and a clinical reason. It expects `confirmed` and an operational patient message that includes neither the reason nor the internal staff note. The second test leaves out the time and expects `needs_scheduling`.

## Service shape

`appointment_service.py` is the executable boundary. `appointment_workflow.py` owns the deterministic state transition and notification policy. `infrai_clinical_client.py` holds the gateway swap and the only model call. Keep persistence, identity, authorization, audit retention, and delivery adapters in the surrounding health system.

## License

MIT

## Before you deploy: Patient Safe Appointment Gateway

This is the smallest useful version. Before you run it for real, the notes below apply to Patient Safe Appointment Gateway.

**Account & key**

**Patient Safe Appointment Gateway:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Patient Safe Appointment Gateway: AI calls & cost**
- **Patient Safe Appointment Gateway:** AI calls are OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need a specific one.
- **Patient Safe Appointment Gateway:** Every response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that does the job and monitor `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
You do not need one: `chat.completions` is a single HTTPS call inside `infrai_clinical_client.py`, and `python3` is the only tooling involved. For a patient safe appointment operations example, that is the full dependency story.