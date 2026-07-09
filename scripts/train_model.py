from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from triage_api.core.config import settings
from triage_api.ml.training import train_and_persist_model


def main() -> None:
    result = train_and_persist_model(
        data_path=settings.data_path,
        model_path=settings.model_path,
        metadata_path=settings.metadata_path,
        model_params_path=settings.optimized_params_path,
    )
    print("Modelo treinado com sucesso.")
    print(f"Modelo salvo em: {result.model_path}")
    print(f"Metadados salvos em: {result.metadata_path}")
    print(f"Fonte dos hiperparametros: {result.model_params_source}")
    print("Hiperparametros usados:")
    for param_name, param_value in result.model_params.items():
        print(f"- {param_name}: {param_value}")
    print("Metricas de validacao:")
    for metric_name, metric_value in result.metrics.items():
        print(f"- {metric_name}: {metric_value:.4f}")


if __name__ == "__main__":
    main()
