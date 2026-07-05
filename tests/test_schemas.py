import pytest
from pydantic import ValidationError

from triage_api.schemas.patient import PatientInput


def test_patient_input_accepts_valid_payload() -> None:
    payload = PatientInput(
        age=30.0,
        heart_rate=90.0,
        systolic_blood_pressure=120.0,
        oxygen_saturation=98.0,
        body_temperature=36.8,
        pain_level=3,
        chronic_disease_count=1,
        previous_er_visits=0,
        arrival_mode="walk_in",
    )

    assert payload.arrival_mode == "walk_in"


def test_patient_input_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        PatientInput.model_validate(
            {
                "age": 30.0,
                "heart_rate": 90.0,
                "systolic_blood_pressure": 120.0,
                "oxygen_saturation": 98.0,
                "body_temperature": 36.8,
                "pain_level": 3,
                "chronic_disease_count": 1,
                "previous_er_visits": 0,
                "arrival_mode": "walk_in",
                "unknown_field": "value",
            }
        )
