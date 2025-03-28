from fastapi import APIRouter
from app.api.v1.endpoints import assessment, content

api_router = APIRouter()

# Include assessment routes
api_router.include_router(
    assessment.router,
    prefix="/assessment",
    tags=["assessment"]
)

# Include content routes
api_router.include_router(
    content.router,
    prefix="/content",
    tags=["content"]
)