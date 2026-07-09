from fastapi import APIRouter, Depends, HTTPException, Request

from triage_api.api.dependencies.auth import get_current_user
from triage_api.core.logging import get_logger
from triage_api.schemas.auth import AuthenticatedUser
from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse

router = APIRouter(prefix="/predict", tags=["prediction"])
logger = get_logger(__name__)


@router.post("/triage", response_model=PredictionResponse)
def predict_triage(
    payload: PatientInput,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PredictionResponse:
    model_service = request.app.state.model_service
    payload_data = payload.model_dump()
    logger.info(
        "Requisicao de triagem recebida.",
        extra={
            "step": "predict_triage_received",
            "payload": {**payload_data, "authenticated_user": current_user.email},
        },
    )
    try:
        response = model_service.predict(payload)
    except FileNotFoundError:
        logger.exception(
            "Modelo nao encontrado para executar a predicao.",
            extra={"step": "predict_triage_model_missing", "payload": payload_data},
        )
        raise HTTPException(
            status_code=503,
            detail="O modelo ainda nao foi treinado. Execute o script de treino antes de consultar a API.",
        ) from None
    try:
        response = request.app.state.interpretation_service.interpret(payload, response)
    except Exception as exc:
        logger.exception(
            "Nao foi possivel gerar a interpretacao da triagem com LLM.",
            extra={
                "step": "predict_triage_interpretation_failed",
                "payload": payload_data,
                "server_response": {
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                },
            },
        )
        raise HTTPException(
            status_code=503,
            detail="Nao foi possivel gerar a interpretacao da triagem com LLM.",
        ) from None

    response_data = response.model_dump()
    logger.info(
        "Predicao calculada com sucesso.",
        extra={
            "step": "predict_triage_completed",
            "payload": payload_data,
            "server_response": response_data,
        },
    )

    prediction_repository = request.app.state.prediction_repository
    if prediction_repository is None:
        logger.info(
            "Persistencia desabilitada porque DATABASE_URL nao foi configurada.",
            extra={
                "step": "prediction_persistence_skipped",
                "payload": payload_data,
                "server_response": response_data,
            },
        )
    else:
        try:
            prediction_repository.save_prediction(payload, response)
        except Exception as exc:
            logger.exception(
                "Nao foi possivel registrar a predicao no banco de dados.",
                extra={
                    "step": "prediction_persistence_failed",
                    "payload": payload_data,
                    "server_response": {
                        "error_type": exc.__class__.__name__,
                        "error_message": str(exc),
                        "prediction": response_data,
                    },
                },
            )
            raise HTTPException(
                status_code=503,
                detail="Nao foi possivel registrar a predicao no banco de dados.",
            ) from None
        logger.info(
            "Registro de triagem persistido com sucesso.",
            extra={
                "step": "prediction_persistence_completed",
                "payload": payload_data,
                "server_response": response_data,
            },
        )

    return response
