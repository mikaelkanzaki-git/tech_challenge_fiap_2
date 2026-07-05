from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from triage_api.schemas.chat import ChatMessageResponse
from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse
from triage_api.services.openai_client import OpenAIResponseClient


@dataclass(frozen=True)
class FieldPrompt:
    field_name: str
    display_name: str
    question: str
    invalid_message: str
    minimum_value: float | None = None
    maximum_value: float | None = None


FIELD_PROMPTS = [
    FieldPrompt(
        "age",
        "idade",
        "Qual é a idade do paciente? Informe um valor entre 0 e 120 anos.",
        "Informe uma idade entre 0 e 120 anos.",
        0,
        120,
    ),
    FieldPrompt(
        "heart_rate",
        "frequência cardíaca",
        "Qual é a frequência cardíaca em batimentos por minuto? Informe um valor entre 0 e 250.",
        "Informe uma frequência cardíaca entre 0 e 250.",
        0,
        250,
    ),
    FieldPrompt(
        "systolic_blood_pressure",
        "pressão sistólica",
        "Qual é a pressão arterial sistólica? Informe um valor entre 0 e 300.",
        "Informe uma pressão sistólica entre 0 e 300.",
        0,
        300,
    ),
    FieldPrompt(
        "oxygen_saturation",
        "saturação de oxigênio",
        "Qual é a saturação de oxigênio? Informe um valor entre 0 e 100.",
        "Informe uma saturação entre 0 e 100.",
        0,
        100,
    ),
    FieldPrompt(
        "body_temperature",
        "temperatura corporal",
        "Qual é a temperatura corporal? Informe um valor entre 30 e 45 graus.",
        "Informe uma temperatura entre 30 e 45 graus.",
        30,
        45,
    ),
    FieldPrompt(
        "pain_level",
        "nível de dor",
        "Em uma escala de 0 a 10, qual é o nível de dor?",
        "Informe o nível de dor entre 0 e 10.",
        0,
        10,
    ),
    FieldPrompt(
        "chronic_disease_count",
        "quantidade de doenças crônicas",
        "Quantas doenças crônicas o paciente possui? Informe um valor entre 0 e 50.",
        "Informe um número de doenças crônicas entre 0 e 50.",
        0,
        50,
    ),
    FieldPrompt(
        "previous_er_visits",
        "visitas anteriores ao pronto atendimento",
        "Quantas visitas anteriores ao pronto atendimento o paciente teve? Informe um valor entre 0 e 200.",
        "Informe um número de visitas anteriores entre 0 e 200.",
        0,
        200,
    ),
    FieldPrompt(
        "arrival_mode",
        "modo de chegada",
        "Como o paciente chegou: andando, cadeira de rodas ou ambulancia?",
        "Informe o modo de chegada: andando, cadeira de rodas ou ambulancia.",
    ),
]

ARRIVAL_MODE_KEYWORDS = {
    "walk_in": ["andando", "a pe", "sozinho", "walk_in"],
    "wheelchair": ["cadeira", "wheelchair"],
    "ambulance": ["ambulancia", "ambulance", "resgate", "samu"],
}

TRIAGE_LABELS = {
    0: "risco baixo",
    1: "risco moderado",
    2: "risco alto",
    3: "risco critico",
}


class TriageChatAgentService:
    def __init__(self, openai_client: OpenAIResponseClient):
        self.openai_client = openai_client

    def handle_message(
        self,
        message: str,
        patient_data: dict[str, Any],
        model_service,
        prediction_repository,
    ) -> ChatMessageResponse:
        updated_data = self._collect_patient_data(message, dict(patient_data))
        missing_fields = self._missing_fields(updated_data)

        if missing_fields:
            next_prompt = self._prompt_for_field(missing_fields[0])
            reply = self._format_reply(
                base_message=next_prompt.question,
                user_message=message,
                patient_data=updated_data,
                missing_fields=missing_fields,
            )
            return ChatMessageResponse(
                message=reply,
                patient_data=updated_data,
                missing_fields=missing_fields,
            )

        patient_input = PatientInput.model_validate(updated_data)
        prediction = model_service.predict(patient_input)
        if prediction_repository is not None:
            prediction_repository.save_prediction(patient_input, prediction)

        reply = self._format_prediction_message(prediction)
        return ChatMessageResponse(
            message=reply,
            patient_data=patient_input.model_dump(),
            missing_fields=[],
            prediction=prediction,
        )

    def _collect_patient_data(self, message: str, patient_data: dict[str, Any]) -> dict[str, Any]:
        normalized_message = _normalize_text(message)
        for field_prompt in FIELD_PROMPTS:
            if field_prompt.field_name in patient_data:
                continue
            value = self._extract_field_value(field_prompt, normalized_message)
            if value is not None:
                patient_data[field_prompt.field_name] = value
                break
        return patient_data

    def _extract_field_value(self, field_prompt: FieldPrompt, normalized_message: str) -> Any | None:
        if field_prompt.field_name == "arrival_mode":
            return _extract_arrival_mode(normalized_message)

        number = _extract_first_number(normalized_message)
        if number is None:
            return None

        if not _is_valid_range(number, field_prompt):
            return None

        if field_prompt.field_name in {"pain_level", "chronic_disease_count", "previous_er_visits"}:
            return int(number)
        return float(number)

    def _missing_fields(self, patient_data: dict[str, Any]) -> list[str]:
        return [field.field_name for field in FIELD_PROMPTS if field.field_name not in patient_data]

    def _prompt_for_field(self, field_name: str) -> FieldPrompt:
        return next(field for field in FIELD_PROMPTS if field.field_name == field_name)

    def _format_reply(
        self,
        base_message: str,
        user_message: str,
        patient_data: dict[str, Any],
        missing_fields: list[str],
    ) -> str:
        instructions = (
            "Você é um agente de triagem hospitalar. Responda em português do Brasil, "
            "com tom acolhedor e objetivo. Não diagnostique. Apenas conduza a coleta "
            "dos dados para a classificação automatizada de risco."
        )
        openai_message = self.openai_client.create_message(
            instructions=instructions,
            user_input=(
                f"Mensagem do usuário: {user_message}\n"
                f"Dados coletados: {patient_data}\n"
                f"Campos faltantes: {missing_fields}\n"
                f"Proxima pergunta obrigatoria: {base_message}"
            ),
        )
        return openai_message or base_message

    def _format_prediction_message(self, prediction: PredictionResponse) -> str:
        risk_label = TRIAGE_LABELS.get(prediction.triage_level, prediction.triage_label)
        return (
            "Consegui calcular a triagem. "
            f"A categoria estimada é {prediction.triage_label} ({risk_label}). "
            "Esse resultado apoia a priorização, mas não substitui avaliação clínica."
        )


def _extract_first_number(value: str) -> float | None:
    match = re.search(r"-?\d+(?:[\.,]\d+)?", value)
    if match is None:
        return None
    return float(match.group(0).replace(",", "."))


def _extract_arrival_mode(value: str) -> str | None:
    for arrival_mode, keywords in ARRIVAL_MODE_KEYWORDS.items():
        if any(keyword in value for keyword in keywords):
            return arrival_mode
    return None


def _is_valid_range(value: float, field_prompt: FieldPrompt) -> bool:
    if field_prompt.minimum_value is not None and value < field_prompt.minimum_value:
        return False
    if field_prompt.maximum_value is not None and value > field_prompt.maximum_value:
        return False
    return True


def _normalize_text(value: str) -> str:
    return value.strip().lower()
