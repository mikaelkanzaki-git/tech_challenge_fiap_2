from typing import Dict

from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    triage_level: int
    triage_label: str
    probabilities: Dict[str, float]
    interpretation: str | None = None
