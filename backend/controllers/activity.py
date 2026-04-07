from fastapi import APIRouter, Depends

from dependencies import get_current_user, get_activity_service
from schemas.activity import ClickRequest, RateRequest, OrderRequest, OrderResponse
from services.activity import ActivityService


router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/click")
def click(
        request: ClickRequest,
        user_id: int = Depends(get_current_user),
        service: ActivityService = Depends(get_activity_service),
):
    return service.click(request, user_id)

@router.post("/order", response_model=OrderResponse)
def order(
        request: OrderRequest,
        user_id: int = Depends(get_current_user),
        service: ActivityService = Depends(get_activity_service),
):
    return service.order(request, user_id)

@router.post("/rate")
def rate(
        request: RateRequest,
        user_id: int = Depends(get_current_user),
        service: ActivityService = Depends(get_activity_service),
):
    return service.rate(request, user_id)