from __future__ import annotations

from typing import Protocol

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse


class PredictionRepository(Protocol):
    def save_prediction(self, payload: PatientInput, response: PredictionResponse) -> None:
        """Persist a prediction request and response."""


class PostgresPredictionRepository:
    def __init__(self, database_url: str, model_version: str = "local"):
        self.database_url = database_url
        self.model_version = model_version

    def save_prediction(self, payload: PatientInput, response: PredictionResponse) -> None:
        query = """
            INSERT INTO triage_prediction_requests (
                age,
                heart_rate,
                systolic_blood_pressure,
                oxygen_saturation,
                body_temperature,
                pain_level,
                chronic_disease_count,
                previous_er_visits,
                arrival_mode,
                triage_level,
                triage_label,
                probabilities,
                model_version
            )
            VALUES (
                %(age)s,
                %(heart_rate)s,
                %(systolic_blood_pressure)s,
                %(oxygen_saturation)s,
                %(body_temperature)s,
                %(pain_level)s,
                %(chronic_disease_count)s,
                %(previous_er_visits)s,
                %(arrival_mode)s,
                %(triage_level)s,
                %(triage_label)s,
                %(probabilities)s,
                %(model_version)s
            )
        """
        params = {
            **payload.model_dump(),
            "triage_level": response.triage_level,
            "triage_label": response.triage_label,
            "probabilities": Jsonb(response.probabilities),
            "model_version": self.model_version,
        }
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
