from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[3]
    data_path: Path = project_root / "data" / "synthetic_medical_triage.csv"
    model_dir: Path = project_root / "models"
    model_path: Path = model_dir / "triage_model.joblib"
    metadata_path: Path = model_dir / "triage_model_metadata.json"


settings = Settings()
