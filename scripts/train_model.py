import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from triage_api.core.config import settings
from triage_api.ml.training import train_and_persist_model

BEST_GA_PARAMS_PATH = ROOT_DIR / "models" / "best_ga_params.json"


def _load_ga_params() -> dict | None:
    if not BEST_GA_PARAMS_PATH.exists():
        return None
    with open(BEST_GA_PARAMS_PATH, encoding="utf-8") as f:
        params = json.load(f)
    # JSON serializes None as null and booleans correctly; restore Python types
    for key in ("bootstrap",):
        if key in params and isinstance(params[key], str):
            params[key] = params[key].lower() == "true"
    for key in ("n_estimators", "max_depth", "min_samples_split", "min_samples_leaf"):
        if key in params:
            params[key] = int(params[key])
    if params.get("class_weight") == "None":
        params["class_weight"] = None
    if params.get("max_features") == "None":
        params["max_features"] = None
    return params


def main() -> None:
    model_params = _load_ga_params()
    if model_params is not None:
        print(f"Hiperparâmetros otimizados pelo AG carregados de: {BEST_GA_PARAMS_PATH}")
        print(f"Parâmetros: {model_params}")
    else:
        print("Nenhum arquivo de parâmetros do AG encontrado — usando defaults.")
        print(f"  (Execute o notebook algoritmo_genetico.ipynb para gerar {BEST_GA_PARAMS_PATH.name})")

    result = train_and_persist_model(
        data_path=settings.data_path,
        model_path=settings.model_path,
        metadata_path=settings.metadata_path,
        model_params=model_params,
    )
    print("\nModelo treinado com sucesso.")
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
