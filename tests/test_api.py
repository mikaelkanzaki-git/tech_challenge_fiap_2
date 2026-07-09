import pytest
from fastapi.testclient import TestClient

from triage_api.api.dependencies.auth import get_current_user
from triage_api.core.config import settings
from triage_api.core.security import create_access_token
from triage_api.main import create_app
from triage_api.repositories.user_repository import UserRecord
from triage_api.schemas.auth import AuthenticatedUser
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


class FailingPredictionRepository:
    def save_prediction(self, payload, response) -> None:
        raise RuntimeError("database unavailable")


class FakeInterpretationService:
    def interpret(self, payload, response):
        return response.model_copy(
            update={"interpretation": "Interpretacao gerada pela LLM."}
        )


class FailingInterpretationService:
    def interpret(self, payload, response):
        raise RuntimeError("openai unavailable")


class FakeUserRepository:
    def __init__(self, user: UserRecord | None = None):
        self.user = user

    def get_user_by_email(self, email: str) -> UserRecord | None:
        if self.user is None or self.user.email != email:
            return None
        return self.user


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


@pytest.fixture
def valid_user() -> UserRecord:
    return UserRecord(
        email="fiap@tech2.com",
        password_hash="139469b8f294c7212ca901e29a3dca86b68a0803c5c362e6b6baf3f0711b3e06",
        password_salt="tech_challenge_fiap_2_fiap_user",
        password_iterations=260000,
        is_active=True,
    )


def authenticated_user() -> AuthenticatedUser:
    return AuthenticatedUser(email="fiap@tech2.com")


def test_health_check_returns_status() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model_ready" in response.json()


def test_root_serves_login_page() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Tech Challenge FIAP" in response.text


def test_predict_triage_returns_prediction(valid_payload: dict[str, object]) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.interpretation_service = FakeInterpretationService()
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 200
    assert response.json()["triage_level"] == 1
    assert response.json()["message"] == "Resultado calculado com sucesso."
    assert response.json()["interpretation"] == "Interpretacao gerada pela LLM."


def test_predict_triage_saves_prediction_when_repository_is_configured(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    prediction_repository = FakePredictionRepository()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = prediction_repository
    app.state.interpretation_service = FakeInterpretationService()
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 200
    assert prediction_repository.saved_payload.arrival_mode == "walk_in"
    assert prediction_repository.saved_response.triage_level == 1
    assert (
        prediction_repository.saved_response.interpretation
        == "Interpretacao gerada pela LLM."
    )


def test_predict_triage_returns_service_unavailable_when_model_is_missing(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = MissingModelService()
    app.state.prediction_repository = None
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 503
    assert response.json()["detail"].startswith("O modelo ainda não foi treinado")


def test_predict_triage_returns_service_unavailable_when_repository_fails(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = FailingPredictionRepository()
    app.state.interpretation_service = FakeInterpretationService()
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "Não foi possível registrar a predição no banco de dados."
    )


def test_predict_triage_returns_service_unavailable_when_interpretation_fails(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.interpretation_service = FailingInterpretationService()
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 503
    assert response.json()["detail"] == "Nao foi possivel gerar a interpretacao da triagem com LLM."


def test_predict_triage_requires_bearer_token(valid_payload: dict[str, object]) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    client = TestClient(app)

    response = client.post("/predict/triage", json=valid_payload)

    assert response.status_code == 401


def test_predict_triage_rejects_invalid_bearer_token(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    client = TestClient(app)

    response = client.post(
        "/predict/triage",
        json=valid_payload,
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais invalidas."


def test_predict_triage_returns_unavailable_when_user_repository_is_missing(
    valid_payload: dict[str, object],
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.user_repository = None
    client = TestClient(app)
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key=settings.jwt_secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )

    response = client.post(
        "/predict/triage",
        json=valid_payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Repositório de usuários não configurado."


def test_predict_triage_rejects_inactive_user(
    valid_payload: dict[str, object],
    valid_user: UserRecord,
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.user_repository = FakeUserRepository(
        UserRecord(
            email=valid_user.email,
            password_hash=valid_user.password_hash,
            password_salt=valid_user.password_salt,
            password_iterations=valid_user.password_iterations,
            is_active=False,
        )
    )
    client = TestClient(app)
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key=settings.jwt_secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )

    response = client.post(
        "/predict/triage",
        json=valid_payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_returns_access_token(valid_user: UserRecord) -> None:
    app = create_app()
    app.state.user_repository = FakeUserRepository(valid_user)
    client = TestClient(app)

    response = client.post(
        "/token",
        data={"username": "fiap@tech2.com", "password": "fiap@Tech_2"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_token_returns_unprocessable_when_password_is_missing() -> None:
    app = create_app()
    app.state.user_repository = FakeUserRepository()
    client = TestClient(app)

    response = client.post("/token", data={"username": "fiap@tech2.com"})

    assert response.status_code == 422
    assert response.json()["detail"] == "Informe usuário e senha para autenticação."


def test_predict_triage_accepts_valid_bearer_token(
    valid_payload: dict[str, object],
    valid_user: UserRecord,
) -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.user_repository = FakeUserRepository(valid_user)
    app.state.interpretation_service = FakeInterpretationService()
    client = TestClient(app)
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key=settings.jwt_secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )

    response = client.post(
        "/predict/triage",
        json=valid_payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["triage_level"] == 1


def test_login_returns_unauthorized_when_password_is_invalid(
    valid_user: UserRecord,
) -> None:
    app = create_app()
    app.state.user_repository = FakeUserRepository(valid_user)
    client = TestClient(app)

    response = client.post(
        "/login",
        json={"username": "fiap@tech2.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha inválidos."


def test_token_returns_service_unavailable_when_user_repository_is_missing() -> None:
    app = create_app()
    app.state.user_repository = None
    client = TestClient(app)

    response = client.post(
        "/token",
        data={"username": "fiap@tech2.com", "password": "fiap@Tech_2"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Repositório de usuários não configurado."


def test_chat_message_requires_bearer_token() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/chat/message",
        json={"message": "79", "patient_data": {}},
    )

    assert response.status_code == 401


def test_chat_message_collects_patient_data() -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post(
        "/chat/message",
        json={"message": "79", "patient_data": {}},
    )

    assert response.status_code == 200
    assert response.json()["patient_data"]["age"] == 79.0
    assert response.json()["missing_fields"][0] == "heart_rate"


def test_chat_message_returns_interpreted_prediction_when_complete() -> None:
    app = create_app()
    app.state.model_service = FakeModelService()
    app.state.prediction_repository = None
    app.state.interpretation_service = FakeInterpretationService()
    app.dependency_overrides[get_current_user] = authenticated_user
    client = TestClient(app)

    response = client.post(
        "/chat/message",
        json={
            "message": "ambulancia",
            "patient_data": {
                "age": 79.0,
                "heart_rate": 147.0,
                "systolic_blood_pressure": 158.0,
                "oxygen_saturation": 96.0,
                "body_temperature": 39.3,
                "pain_level": 10,
                "chronic_disease_count": 4,
                "previous_er_visits": 2,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["prediction"]["triage_level"] == 1
    assert (
        response.json()["prediction"]["interpretation"]
        == "Interpretacao gerada pela LLM."
    )
    assert "Interpretacao da LLM" in response.json()["message"]
