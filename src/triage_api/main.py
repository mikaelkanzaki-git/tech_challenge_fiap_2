from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from triage_api.api.routes.auth import router as auth_router
from triage_api.api.routes.chat import router as chat_router
from triage_api.api.routes.predict import router as predict_router
from triage_api.core.config import settings
from triage_api.core.logging import get_logger
from triage_api.repositories.prediction_repository import PostgresPredictionRepository
from triage_api.repositories.user_repository import PostgresUserRepository
from triage_api.services.chat_agent_service import TriageChatAgentService
from triage_api.services.interpretation_service import InterpretationService
from triage_api.services.model_service import ModelService
from triage_api.services.openai_client import OpenAIResponseClient

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Triage Prediction API",
        version="0.1.0",
        description="Prediction API for the emergency triage model.",
    )
    app.state.model_service = ModelService(settings.model_path)
    app.state.prediction_repository = (
        PostgresPredictionRepository(
            settings.database_url, model_version=settings.model_version
        )
        if settings.database_url
        else None
    )
    app.state.user_repository = (
        PostgresUserRepository(settings.database_url) if settings.database_url else None
    )
    openai_client = OpenAIResponseClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    app.state.chat_agent_service = TriageChatAgentService(openai_client)
    app.state.interpretation_service = InterpretationService(openai_client)
    logger.info(
        "Aplicacao iniciada.",
        extra={
            "step": "application_started",
            "payload": {
                "model_path": str(settings.model_path),
                "model_ready": settings.model_path.exists(),
                "database_configured": bool(settings.database_url),
                "model_version": settings.model_version,
                "authentication_enabled": app.state.user_repository is not None,
                "openai_configured": bool(settings.openai_api_key),
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
    if app.state.user_repository is None:
        logger.info(
            "Autenticacao em banco desabilitada.",
            extra={"step": "auth_repository_disabled"},
        )
    else:
        logger.info(
            "Autenticacao em banco habilitada.",
            extra={"step": "auth_repository_enabled"},
        )
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(predict_router)

    @app.get("/health")
    def health_check() -> dict[str, object]:
        return {
            "status": "ok",
            "model_ready": settings.model_path.exists(),
            "prediction_persistence_enabled": app.state.prediction_repository
            is not None,
            "authentication_enabled": app.state.user_repository is not None,
            "chat_agent_enabled": True,
        }

    app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="static")

    return app


app = create_app()
