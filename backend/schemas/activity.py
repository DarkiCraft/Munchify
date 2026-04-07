from datetime import datetime

from pydantic import BaseModel


class ClickRequest(BaseModel):
    item_id: int

class OrderRequest(BaseModel):
    item_id: int

class RateRequest(BaseModel):
    order_id: int
    rating: int

class OrderResponse(BaseModel):
    order_id: int
    item_id: int
    timestamp: datetime