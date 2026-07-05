from fastapi import FastAPI

from triage_api.api.routes.predict import router as predict_router
from triage_api.core.config import settings
from triage_api.repositories.prediction_repository import PostgresPredictionRepository
from triage_api.services.model_service import ModelService


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
    app.include_router(predict_router)

    @app.get("/health")
    def health_check() -> dict[str, object]:
        return {
            "status": "ok",
            "model_ready": settings.model_path.exists(),
        }

    return app


app = create_app()
