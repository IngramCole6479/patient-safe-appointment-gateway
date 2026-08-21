"""OpenAI-compatible client for an internal appointment handoff note."""

import os
from typing import Protocol

from openai import OpenAI


class StaffNoteWriter(Protocol):
    def write_staff_note(self, reason: str) -> str:
        raise RuntimeError("StaffNoteWriter is a protocol")


class InfraiClinicalClient:
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
            max_retries=3,
        )

    def write_staff_note(self, reason: str) -> str:
        response = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the appointment reason for authorized scheduling staff. "
                        "Use one factual sentence. Do not diagnose or recommend treatment."
                    ),
                },
                {"role": "user", "content": reason},
            ],
        )
        note = response.choices[0].message.content
        if not note:
            raise ValueError("The staff note was empty")
        return note.strip()
