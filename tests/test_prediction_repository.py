from triage_api.repositories.prediction_repository import PostgresPredictionRepository
from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse


class FakeCursor:
    def __init__(self, calls):
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params):
        self.calls.append((query, params))


class FakeConnection:
    def __init__(self, calls):
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def cursor(self):
        return FakeCursor(self.calls)


def test_postgres_prediction_repository_inserts_payload_and_prediction(monkeypatch) -> None:
    calls = []

    def fake_connect(database_url, row_factory):
        assert database_url == "postgresql://localhost/tech_challenge_fiap_2"
        assert row_factory is not None
        return FakeConnection(calls)

    monkeypatch.setattr("triage_api.repositories.prediction_repository.psycopg.connect", fake_connect)

    repository = PostgresPredictionRepository(
        "postgresql://localhost/tech_challenge_fiap_2",
        model_version="test-model",
    )
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
    response = PredictionResponse(
        message="Resultado calculado com sucesso.",
        triage_level=1,
        triage_label="level_1",
        probabilities={"level_0": 0.1, "level_1": 0.7, "level_2": 0.1, "level_3": 0.1},
    )

    repository.save_prediction(payload, response)

    query, params = calls[0]
    assert "INSERT INTO triage_prediction_requests" in query
    assert params["arrival_mode"] == "walk_in"
    assert params["triage_level"] == 1
    assert params["triage_label"] == "level_1"
    assert params["model_version"] == "test-model"
