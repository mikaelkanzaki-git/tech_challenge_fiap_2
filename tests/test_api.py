import pytest
from fastapi.testclient import TestClient

from triage_api.main import create_app
from triage_api.schemas.prediction import PredictionResponse


class FakeModelService:
    def predict(self, payload):
        return PredictionResponse(
            message="Resultado calculado com sucesso.",
            triage_level=1,
            triage_label="level_1",
            probabilities={
                "level_0": 0.1,
                "level_1": 0.7,
                "level_2": 0.1,
                "level_3": 0.1,
            },
        )


class MissingModelService:
    def predict(self, payload):
        raise FileNotFoundError("missing model")


class FakePredictionRepository:
    def __init__(self):
        self.saved_payload = None
        self.saved_response = None

    def save_prediction(self, payload, response) -> None:
        self.saved_payload = payload
        self.saved_response = response


@pytest.fixture
def valid_payload() -> dict[str, object]:
    return {
        "age": 30.0,
        "heart_rate": 90.0,
        "systolic_blood_pressure": 120.0,
        "oxygen_saturation": 98.0,
        "body_temperature": 36.8,
        "pain_level": 3,
        "chronic_disease_count": 1,
        "previous_er_visits": 0,
        "arrival_mode": "walk_in",
    }


def test_health_check_returns_status() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model_ready" in response.json()


def test_predict_triage_returns_prediction(valid_payload: dict[str, object]) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 200
    assert response.json()["triage_level"] == 1
    assert response.json()["message"] == "Resultado calculado com sucesso."


def test_predict_triage_saves_prediction_when_repository_is_configured(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    prediction_repository = FakePredictionRepository()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = prediction_repository
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 200
    assert prediction_repository.saved_payload.arrival_mode == "walk_in"
    assert prediction_repository.saved_response.triage_level == 1


def test_predict_triage_returns_service_unavailable_when_model_is_missing(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = MissingModelService()
    app.state.prediction_repository = None
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 503
    assert response.json()["detail"].startswith("O modelo ainda nao foi treinado")
