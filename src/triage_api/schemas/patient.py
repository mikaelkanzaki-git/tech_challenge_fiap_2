from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ArrivalMode = Literal["walk_in", "wheelchair", "ambulance"]


class PatientInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: float = Field(ge=0, le=120)
    heart_rate: float = Field(ge=0, le=250)
    systolic_blood_pressure: float = Field(ge=0, le=300)
    oxygen_saturation: float = Field(ge=0, le=100)
    body_temperature: float = Field(ge=30, le=45)
    pain_level: int = Field(ge=0, le=10)
    chronic_disease_count: int = Field(ge=0, le=50)
    previous_er_visits: int = Field(ge=0, le=200)
    arrival_mode: ArrivalMode
