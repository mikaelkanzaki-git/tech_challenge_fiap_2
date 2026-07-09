from fastapi import APIRouter, Depends, HTTPException, Request, status

from triage_api.api.dependencies.auth import get_current_user
from triage_api.core.logging import get_logger
from triage_api.schemas.auth import AuthenticatedUser
from triage_api.schemas.chat import ChatMessageRequest, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("/message", response_model=ChatMessageResponse)
def create_chat_message(
    payload: ChatMessageRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ChatMessageResponse:
    logger.info(
        "Mensagem de chat recebida.",
        extra={
            "step": "chat_message_received",
            "payload": {
                "authenticated_user": current_user.email,
                "patient_data_fields": list(payload.patient_data.keys()),
            },
        },
    )
    chat_agent_service = request.app.state.chat_agent_service
    model_service = request.app.state.model_service
    prediction_repository = request.app.state.prediction_repository
    interpretation_service = request.app.state.interpretation_service

    try:
        response = chat_agent_service.handle_message(
            message=payload.message,
            patient_data=payload.patient_data,
            model_service=model_service,
            prediction_repository=prediction_repository,
            interpretation_service=interpretation_service,
        )
    except Exception as exc:
        logger.exception(
            "Nao foi possivel processar a conversa de triagem.",
            extra={
                "step": "chat_message_failed",
                "payload": {"authenticated_user": current_user.email},
                "server_response": {
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                },
            },
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel processar a conversa de triagem.",
        ) from None

    logger.info(
        "Mensagem de chat processada.",
        extra={
            "step": "chat_message_completed",
            "payload": {
                "authenticated_user": current_user.email,
                "missing_fields": response.missing_fields,
            },
            "server_response": {"has_prediction": response.prediction is not None},
        },
    )
    return response
