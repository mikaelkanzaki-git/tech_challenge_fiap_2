import pytest

from triage_api.schemas.prediction import PredictionResponse
from triage_api.services.chat_agent_service import TriageChatAgentService


class FakeOpenAIClient:
    def __init__(self, message: str | None = None):
        self.message = message

    def create_message(self, instructions: str, user_input: str) -> str | None:
        return self.message


class FakeModelService:
    def predict(self, payload):
        return PredictionResponse(
            message="Resultado calculado com sucesso.",
            triage_level=3,
            triage_label="level_3",
            probabilities={
                "level_0": 0.0,
                "level_1": 0.0,
                "level_2": 0.0,
                "level_3": 1.0,
            },
        )


class FakePredictionRepository:
    def __init__(self):
        self.saved_payload = None
        self.saved_response = None

    def save_prediction(self, payload, response) -> None:
        self.saved_payload = payload
        self.saved_response = response


def test_chat_agent_collects_next_field_and_asks_next_question() -> None:
    service = TriageChatAgentService(FakeOpenAIClient())

    response = service.handle_message(
        message="79",
        patient_data={},
        model_service=FakeModelService(),
        prediction_repository=None,
    )

    assert response.patient_data["age"] == 79.0
    assert response.missing_fields[0] == "heart_rate"
    assert response.prediction is None
    assert "frequencia cardiaca" in response.message


def test_chat_agent_uses_openai_message_when_available() -> None:
    service = TriageChatAgentService(FakeOpenAIClient("Pergunta humanizada."))

    response = service.handle_message(
        message="79",
        patient_data={},
        model_service=FakeModelService(),
        prediction_repository=None,
    )

    assert response.message == "Pergunta humanizada."


def test_chat_agent_rejects_out_of_range_value() -> None:
    service = TriageChatAgentService(FakeOpenAIClient())

    response = service.handle_message(
        message="200",
        patient_data={},
        model_service=FakeModelService(),
        prediction_repository=None,
    )

    assert "age" in response.missing_fields
    assert "age" not in response.patient_data


def test_chat_agent_predicts_when_required_fields_are_complete() -> None:
    service = TriageChatAgentService(FakeOpenAIClient())
    prediction_repository = FakePredictionRepository()
    patient_data = {
        "age": 79.0,
        "heart_rate": 147.0,
        "systolic_blood_pressure": 158.0,
        "oxygen_saturation": 96.0,
        "body_temperature": 39.3,
        "pain_level": 10,
        "chronic_disease_count": 4,
        "previous_er_visits": 2,
    }

    response = service.handle_message(
        message="ambulancia",
        patient_data=patient_data,
        model_service=FakeModelService(),
        prediction_repository=prediction_repository,
    )

    assert response.prediction is not None
    assert response.prediction.triage_level == 3
    assert response.patient_data["arrival_mode"] == "ambulance"
    assert prediction_repository.saved_payload.arrival_mode == "ambulance"


def test_chat_agent_raises_when_complete_payload_is_invalid() -> None:
    service = TriageChatAgentService(FakeOpenAIClient())
    patient_data = {
        "age": 79.0,
        "heart_rate": 147.0,
        "systolic_blood_pressure": 158.0,
        "oxygen_saturation": 96.0,
        "body_temperature": 39.3,
        "pain_level": 10,
        "chronic_disease_count": 4,
        "previous_er_visits": 2,
        "arrival_mode": "flying",
    }

    with pytest.raises(Exception):
        service.handle_message(
            message="confirmar",
            patient_data=patient_data,
            model_service=FakeModelService(),
            prediction_repository=None,
        )
