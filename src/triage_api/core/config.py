from dataclasses import dataclass
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_environment_file(path: Path = PROJECT_ROOT / ".env") -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def get_int_environment(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


load_environment_file()


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    data_path: Path = project_root / "data" / "synthetic_medical_triage.csv"
    static_dir: Path = project_root / "frontend"
    model_dir: Path = project_root / "models"
    model_path: Path = model_dir / "triage_model.joblib"
    metadata_path: Path = model_dir / "triage_model_metadata.json"
    optimized_params_path: Path = model_dir / "optimized_params.json"
    database_url: str | None = os.getenv("DATABASE_URL")
    model_version: str = os.getenv("MODEL_VERSION", "local")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-local-secret")
    access_token_expire_minutes: int = get_int_environment(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 60
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


settings = Settings()
