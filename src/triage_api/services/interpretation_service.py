from __future__ import annotations

import json

from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse
from triage_api.services.openai_client import OpenAIResponseClient


class InterpretationService:
    def __init__(self, openai_client: OpenAIResponseClient):
        self.openai_client = openai_client

    def interpret(
        self,
        patient_input: PatientInput,
        prediction: PredictionResponse,
    ) -> PredictionResponse:
        if not self.openai_client.is_configured():
            raise RuntimeError(
                "OPENAI_API_KEY must be configured for triage interpretation."
            )

        interpretation = self.openai_client.create_message(
            instructions=_build_instructions(),
            user_input=_build_user_input(patient_input, prediction),
        )
        if not interpretation:
            raise RuntimeError("OpenAI did not return a triage interpretation.")

        return prediction.model_copy(update={"interpretation": interpretation})


def _build_instructions() -> str:
    return (
        "Voce e um assistente de apoio a decisao para triagem hospitalar. "
        "Responda em portugues do Brasil, com linguagem objetiva para profissionais de saude. "
        "Explique a classificacao de risco estimada pelo modelo com base nos sinais vitais, "
        "dados clinicos e probabilidades fornecidas. "
        "Nao crie diagnosticos, nao prescreva condutas e nao afirme certeza clinica. "
        "Inclua que o resultado apoia priorizacao e nao substitui avaliacao clinica. "
        "Use no maximo 3 paragrafos curtos."
    )


def _build_user_input(
    patient_input: PatientInput, prediction: PredictionResponse
) -> str:
    payload = {
        "patient_data": patient_input.model_dump(),
        "model_prediction": {
            "triage_level": prediction.triage_level,
            "triage_label": prediction.triage_label,
            "probabilities": prediction.probabilities,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
