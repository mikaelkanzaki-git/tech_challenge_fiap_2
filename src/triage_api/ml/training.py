from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split

from triage_api.ml.preprocessing import prepare_training_data

DEFAULT_MODEL_PARAMS: dict[str, Any] = {
    "n_estimators": 20,
    "max_depth": 10,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "criterion": "entropy",
    "class_weight": "balanced",
    "max_features": "sqrt",
    "bootstrap": True,
}


@dataclass(frozen=True)
class TrainingResult:
    model_path: Path
    metadata_path: Path
    metrics: dict[str, float]
    model_params: dict[str, Any]
    model_params_source: str


def load_model_params(params_path: Path) -> dict[str, Any] | None:
    if not params_path.exists():
        return None

    raw_params = json.loads(params_path.read_text(encoding="utf-8"))
    if not isinstance(raw_params, dict):
        raise ValueError("Optimized model params file must contain a JSON object.")

    return {**DEFAULT_MODEL_PARAMS, **raw_params}


def build_model(
    model_params: dict[str, Any], random_state: int
) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=int(model_params["n_estimators"]),
        max_depth=int(model_params["max_depth"]),
        min_samples_split=int(model_params["min_samples_split"]),
        min_samples_leaf=int(model_params["min_samples_leaf"]),
        criterion=model_params["criterion"],
        class_weight=model_params["class_weight"],
        max_features=model_params["max_features"],
        bootstrap=bool(model_params["bootstrap"]),
        random_state=random_state,
        n_jobs=-1,
    )


def fit_model(
    features: pd.DataFrame,
    target: pd.Series,
    model_params: dict[str, Any] | None = None,
    random_state: int = 7,
) -> RandomForestClassifier:
    params = DEFAULT_MODEL_PARAMS if model_params is None else model_params
    model = build_model(params, random_state=random_state)
    resampled_features, resampled_target = SMOTE(
        random_state=random_state
    ).fit_resample(features, target)
    model.fit(resampled_features, resampled_target)
    return model


def evaluate_model(
    model: RandomForestClassifier, features: pd.DataFrame, target: pd.Series
) -> dict[str, float]:
    predictions = model.predict(features)
    return {
        "accuracy": float(accuracy_score(target, predictions)),
        "macro_f1": float(f1_score(target, predictions, average="macro")),
        "recall_2": float(
            recall_score(
                target, predictions, labels=[2], average="macro", zero_division=0
            )
        ),
        "recall_3": float(
            recall_score(
                target, predictions, labels=[3], average="macro", zero_division=0
            )
        ),
    }


def train_and_persist_model(
    data_path: Path,
    model_path: Path,
    metadata_path: Path,
    model_params: dict[str, Any] | None = None,
    model_params_path: Path | None = None,
    random_state: int = 7,
) -> TrainingResult:
    loaded_model_params = (
        None
        if model_params is not None or model_params_path is None
        else load_model_params(model_params_path)
    )
    effective_model_params = model_params or loaded_model_params or DEFAULT_MODEL_PARAMS
    model_params_source = (
        "argument"
        if model_params is not None
        else (
            str(model_params_path)
            if loaded_model_params is not None and model_params_path is not None
            else "default"
        )
    )

    data = pd.read_csv(data_path)
    features, target = prepare_training_data(data)

    train_features, test_features, train_target, test_target = train_test_split(
        features,
        target,
        test_size=0.2,
        stratify=target,
        random_state=random_state,
    )

    evaluation_model = fit_model(
        train_features,
        train_target,
        model_params=effective_model_params,
        random_state=random_state,
    )
    metrics = evaluate_model(evaluation_model, test_features, test_target)

    final_model = fit_model(
        features,
        target,
        model_params=effective_model_params,
        random_state=random_state,
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(final_model, model_path)

    metadata = {
        "data_path": str(data_path),
        "model_path": str(model_path),
        "random_state": random_state,
        "feature_columns": list(features.columns),
        "model_params": effective_model_params,
        "model_params_source": model_params_source,
        "metrics": metrics,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return TrainingResult(
        model_path=model_path,
        metadata_path=metadata_path,
        metrics=metrics,
        model_params=effective_model_params,
        model_params_source=model_params_source,
    )
