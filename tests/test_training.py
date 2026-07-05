import json

import pandas as pd

from triage_api.ml.training import (
    DEFAULT_MODEL_PARAMS,
    build_model,
    evaluate_model,
    train_and_persist_model,
)


class StaticModel:
    def __init__(self, predictions):
        self.predictions = predictions

    def predict(self, features):
        return self.predictions[: len(features)]


def test_build_model_applies_params() -> None:
    model = build_model(DEFAULT_MODEL_PARAMS, random_state=7)

    assert model.n_estimators == DEFAULT_MODEL_PARAMS["n_estimators"]
    assert model.max_depth == DEFAULT_MODEL_PARAMS["max_depth"]
    assert model.criterion == DEFAULT_MODEL_PARAMS["criterion"]
    assert model.random_state == 7


def test_evaluate_model_returns_metrics() -> None:
    features = pd.DataFrame({"feature": [1, 2, 3, 4]})
    target = pd.Series([0, 1, 2, 3])
    model = StaticModel([0, 1, 2, 3])

    metrics = evaluate_model(model, features, target)

    assert metrics["accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0
    assert metrics["recall_2"] == 1.0
    assert metrics["recall_3"] == 1.0


def test_train_and_persist_model_writes_artifacts(tmp_path, monkeypatch) -> None:
    data_path = tmp_path / "training.csv"
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"
    data = pd.DataFrame(
        [
            {
                "age": 20.0 + index,
                "heart_rate": 80.0 + index,
                "systolic_blood_pressure": 120.0,
                "oxygen_saturation": 98.0,
                "body_temperature": 36.5,
                "pain_level": index % 10,
                "chronic_disease_count": index % 3,
                "previous_er_visits": index % 4,
                "arrival_mode": ["walk_in", "wheelchair", "ambulance"][index % 3],
                "triage_level": index % 4,
            }
            for index in range(40)
        ]
    )
    data.to_csv(data_path, index=False)

    class FakeFittedModel:
        def predict(self, features):
            return [0 for _ in range(len(features))]

    monkeypatch.setattr("triage_api.ml.training.fit_model", lambda *args, **kwargs: FakeFittedModel())
    monkeypatch.setattr(
        "triage_api.ml.training.evaluate_model",
        lambda *args, **kwargs: {
            "accuracy": 0.5,
            "macro_f1": 0.5,
            "recall_2": 0.5,
            "recall_3": 0.5,
        },
    )
    monkeypatch.setattr(
        "triage_api.ml.training.joblib.dump",
        lambda model, path: path.write_text("fake model", encoding="utf-8"),
    )

    result = train_and_persist_model(data_path, model_path, metadata_path, random_state=7)

    assert result.model_path == model_path
    assert model_path.exists()
    assert metadata_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["metrics"]["accuracy"] == 0.5
