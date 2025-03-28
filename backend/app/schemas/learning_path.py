from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ContentItem(BaseModel):
    content_id: int
    required: bool = True
    order_index: int
    
    class Config:
        from_attributes = True

class LearningPathBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    difficulty_level: int = Field(1, ge=1, le=5)
    estimated_hours: Optional[float] = None

class LearningPathCreate(LearningPathBase):
    goals: List[str]
    difficulty: str = "medium"  # beginner, easy, medium, advanced, expert

class LearningPathUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    estimated_hours: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class LearningPath(LearningPathBase):
    id: int
    is_ai_generated: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    
    class Config:
        from_attributes = True

class PathEnrollmentCreate(BaseModel):
    user_id: int
    path_id: int
    personalization_settings: Optional[Dict[str, Any]] = None

class PathProgressUpdate(BaseModel):
    content_id: int
    progress: float = Field(..., ge=0, le=100)

class PathEnrollment(BaseModel):
    id: int
    user_id: int
    path_id: int
    progress: float
    content_progress: Dict[str, float] = {}
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PathWithContents(LearningPath):
    contents: List[Dict[str, Any]]
    user_progress: Optional[Dict[str, Any]] = None
