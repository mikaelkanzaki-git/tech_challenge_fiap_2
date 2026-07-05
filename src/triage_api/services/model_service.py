from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from triage_api.ml.preprocessing import build_prediction_frame
from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse


class ModelService:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self._model: Any | None = None

    def load_model(self) -> Any:
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            self._model = joblib.load(self.model_path)
        return self._model

    def predict(self, payload: PatientInput) -> PredictionResponse:
        model = self.load_model()
        feature_frame = build_prediction_frame(payload.model_dump())
        prediction = int(model.predict(feature_frame)[0])
        probabilities = model.predict_proba(feature_frame)[0]
        class_labels = [int(label) for label in model.classes_]
        probability_map = {
            f"level_{label}": float(probability)
            for label, probability in zip(class_labels, probabilities)
        }

        return PredictionResponse(
            message="Resultado calculado com sucesso.",
            triage_level=prediction,
            triage_label=f"level_{prediction}",
            probabilities=probability_map,
        )
