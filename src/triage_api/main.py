from fastapi import FastAPI

from triage_api.api.routes.predict import router as predict_router
from triage_api.core.config import settings
from triage_api.core.logging import get_logger
from triage_api.repositories.prediction_repository import PostgresPredictionRepository
from triage_api.services.model_service import ModelService

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Triage Prediction API",
        version="0.1.0",
        description="Prediction API for the emergency triage model.",
    )
    app.state.model_service = ModelService(settings.model_path)
    app.state.prediction_repository = (
        PostgresPredictionRepository(settings.database_url, model_version=settings.model_version)
        if settings.database_url
        else None
    )
    logger.info(
        "Aplicacao iniciada.",
        extra={
            "step": "application_started",
            "payload": {
                "model_path": str(settings.model_path),
                "model_ready": settings.model_path.exists(),
                "database_configured": bool(settings.database_url),
                "model_version": settings.model_version,
            },
        },
    )
    if app.state.prediction_repository is None:
        logger.info(
            "Persistencia em banco desabilitada.",
            extra={"step": "prediction_persistence_disabled"},
        )
    else:
        logger.info(
            "Persistencia em banco habilitada.",
            extra={
                "step": "prediction_persistence_enabled",
                "payload": {"model_version": settings.model_version},
            },
        )
    app.include_router(predict_router)

    @app.get("/health")
    def health_check() -> dict[str, object]:
        return {
            "status": "ok",
            "model_ready": settings.model_path.exists(),
            "prediction_persistence_enabled": app.state.prediction_repository is not None,
        }

    return app


app = create_app()
