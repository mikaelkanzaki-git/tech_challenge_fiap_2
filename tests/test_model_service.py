from pathlib import Path
from types import SimpleNamespace

import numpy as np

from triage_api.schemas.patient import PatientInput
from triage_api.services.model_service import ModelService


class FakeModel:
    classes_ = np.array([0, 1, 2, 3])

    def predict(self, feature_frame):
        return np.array([2])

    def predict_proba(self, feature_frame):
        return np.array([[0.1, 0.2, 0.5, 0.2]])


def test_model_service_predicts_response() -> None:
    service = ModelService(Path("missing.joblib"))
    service._model = FakeModel()

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

    response = service.predict(payload)

    assert response.message == "Resultado calculado com sucesso."
    assert response.triage_level == 2
    assert response.triage_label == "level_2"
    assert response.probabilities["level_2"] == 0.5
