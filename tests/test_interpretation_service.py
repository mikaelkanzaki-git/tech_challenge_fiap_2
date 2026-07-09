import pytest

from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse
from triage_api.services.interpretation_service import InterpretationService


class FakeOpenAIClient:
    def __init__(
        self, configured: bool = True, message: str | None = "Interpretacao LLM."
    ):
        self.configured = configured
        self.message = message
        self.instructions = None
        self.user_input = None

    def is_configured(self) -> bool:
        return self.configured

    def create_message(self, instructions: str, user_input: str) -> str | None:
        self.instructions = instructions
        self.user_input = user_input
        return self.message


def patient_input() -> PatientInput:
    return PatientInput(
        age=79.0,
        heart_rate=147.0,
        systolic_blood_pressure=158.0,
        oxygen_saturation=96.0,
        body_temperature=39.3,
        pain_level=10,
        chronic_disease_count=4,
        previous_er_visits=2,
        arrival_mode="ambulance",
    )


def prediction_response() -> PredictionResponse:
    return PredictionResponse(
        message="Resultado calculado com sucesso.",
        triage_level=3,
        triage_label="level_3",
        probabilities={
            "level_0": 0.0,
            "level_1": 0.0,
            "level_2": 0.1,
            "level_3": 0.9,
        },
    )


def test_interpretation_service_adds_llm_interpretation() -> None:
    openai_client = FakeOpenAIClient(message="Risco critico explicado.")
    service = InterpretationService(openai_client)

    response = service.interpret(patient_input(), prediction_response())

    assert response.interpretation == "Risco critico explicado."
    assert "Nao crie diagnosticos" in openai_client.instructions
    assert "triage_level" in openai_client.user_input


def test_interpretation_service_requires_openai_api_key() -> None:
    service = InterpretationService(FakeOpenAIClient(configured=False))

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        service.interpret(patient_input(), prediction_response())


def test_interpretation_service_requires_openai_response_text() -> None:
    service = InterpretationService(FakeOpenAIClient(message=None))

    with pytest.raises(RuntimeError, match="did not return"):
        service.interpret(patient_input(), prediction_response())
