from fastapi import APIRouter, Depends

from dependencies import get_current_user, get_recommendation_service
from schemas.recommend import RecommendRequest
from services.recommend import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
def get_recommendations(
        request: RecommendRequest,
        user_id: int = Depends(get_current_user),
        service: RecommendationService = Depends(get_recommendation_service)
):
    item_ids = service.recommend(request, user_id)
    return {"recommendations": item_ids}


@router.post("/retrain")
def retrain(
        user_id: int = Depends(get_current_user), # some admin check later
        service: RecommendationService = Depends(get_recommendation_service)
):
    service.retrain()
    return {"message": "Retrain complete"}