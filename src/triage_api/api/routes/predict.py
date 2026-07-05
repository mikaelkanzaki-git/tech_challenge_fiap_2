from fastapi import APIRouter, HTTPException, Request

from triage_api.schemas.patient import PatientInput
from triage_api.schemas.prediction import PredictionResponse

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/triage", response_model=PredictionResponse)
def predict_triage(payload: PatientInput, request: Request) -> PredictionResponse:
    model_service = request.app.state.model_service
    try:
        response = model_service.predict(payload)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="O modelo ainda nao foi treinado. Execute o script de treino antes de consultar a API.",
        ) from None

    prediction_repository = request.app.state.prediction_repository
    if prediction_repository is not None:
        prediction_repository.save_prediction(payload, response)

    return response
