from pydantic import BaseModel

class RecommendRequest(BaseModel):
    k: int

class RecommendResponse(BaseModel):
    recommendations: list[int]