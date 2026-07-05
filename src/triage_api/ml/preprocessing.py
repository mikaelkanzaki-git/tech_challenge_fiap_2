from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

ARRIVAL_MODE_ENCODING = {
    "walk_in": 0,
    "wheelchair": 1,
    "ambulance": 2,
}

FEATURE_COLUMNS = [
    "age",
    "heart_rate",
    "systolic_blood_pressure",
    "oxygen_saturation",
    "body_temperature",
    "pain_level",
    "chronic_disease_count",
    "previous_er_visits",
    "arrival_mode_label_encoding",
]

TARGET_COLUMN = "triage_level"
ARRIVAL_MODE_COLUMN = "arrival_mode"


def encode_arrival_mode(value: str) -> int:
    try:
        return ARRIVAL_MODE_ENCODING[value]
    except KeyError as exc:
        raise ValueError(f"Unsupported arrival_mode: {value}") from exc


def prepare_training_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    frame = dataframe.copy()
    frame["arrival_mode_label_encoding"] = frame[ARRIVAL_MODE_COLUMN].map(ARRIVAL_MODE_ENCODING)

    if frame["arrival_mode_label_encoding"].isna().any():
        invalid_values = sorted(
            frame.loc[frame["arrival_mode_label_encoding"].isna(), ARRIVAL_MODE_COLUMN]
            .dropna()
            .unique()
            .tolist()
        )
        raise ValueError(f"Unsupported arrival_mode values: {invalid_values}")

    features = frame.drop(columns=[TARGET_COLUMN, ARRIVAL_MODE_COLUMN])
    target = frame[TARGET_COLUMN].astype(int)
    return features[FEATURE_COLUMNS], target


def build_prediction_frame(payload: Mapping[str, Any]) -> pd.DataFrame:
    row = dict(payload)
    row["arrival_mode_label_encoding"] = encode_arrival_mode(str(row.pop(ARRIVAL_MODE_COLUMN)))
    frame = pd.DataFrame([row])
    return frame[FEATURE_COLUMNS]
