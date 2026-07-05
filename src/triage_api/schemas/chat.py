from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from triage_api.schemas.prediction import PredictionResponse


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)
    patient_data: dict[str, Any] = Field(default_factory=dict)


class ChatMessageResponse(BaseModel):
    message: str
    patient_data: dict[str, Any]
    missing_fields: list[str]
    prediction: PredictionResponse | None = None
