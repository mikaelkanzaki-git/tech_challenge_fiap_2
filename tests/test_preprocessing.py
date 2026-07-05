import pandas as pd
import pytest

from triage_api.ml.preprocessing import build_prediction_frame, encode_arrival_mode, prepare_training_data


def test_encode_arrival_mode() -> None:
    assert encode_arrival_mode("walk_in") == 0
    assert encode_arrival_mode("wheelchair") == 1
    assert encode_arrival_mode("ambulance") == 2


def test_build_prediction_frame_returns_expected_columns() -> None:
    payload = {
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

    frame = build_prediction_frame(payload)

    assert list(frame.columns) == [
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
    assert frame.iloc[0]["arrival_mode_label_encoding"] == 0


def test_prepare_training_data_encodes_arrival_mode() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "age": 30.0,
                "heart_rate": 90.0,
                "systolic_blood_pressure": 120.0,
                "oxygen_saturation": 98.0,
                "body_temperature": 36.8,
                "pain_level": 3,
                "chronic_disease_count": 1,
                "previous_er_visits": 0,
                "arrival_mode": "walk_in",
                "triage_level": 0,
            }
        ]
    )

    features, target = prepare_training_data(dataframe)

    assert "arrival_mode_label_encoding" in features.columns
    assert target.iloc[0] == 0


def test_prepare_training_data_rejects_unknown_arrival_mode() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "age": 30.0,
                "heart_rate": 90.0,
                "systolic_blood_pressure": 120.0,
                "oxygen_saturation": 98.0,
                "body_temperature": 36.8,
                "pain_level": 3,
                "chronic_disease_count": 1,
                "previous_er_visits": 0,
                "arrival_mode": "helicopter",
                "triage_level": 0,
            }
        ]
    )

    with pytest.raises(ValueError, match="Unsupported arrival_mode values"):
        prepare_training_data(dataframe)


def test_encode_arrival_mode_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        encode_arrival_mode("unknown")
