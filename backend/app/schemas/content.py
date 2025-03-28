from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

# Base models
class ContentTagBase(BaseModel):
    name: str
    description: Optional[str] = None

class ContentTag(ContentTagBase):
    id: int
    
    class Config:
        from_attributes = True

# 明确定义标签响应模型
class ContentTagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    subject: str
    difficulty_level: int = Field(1, ge=1, le=5)
    content_data: Dict[str, Any]
    visual_affinity: float = Field(25.0, ge=0, le=100)
    auditory_affinity: float = Field(25.0, ge=0, le=100)
    kinesthetic_affinity: float = Field(25.0, ge=0, le=100)
    reading_affinity: float = Field(25.0, ge=0, le=100)
    author: Optional[str] = None
    source_url: Optional[str] = None
    is_premium: bool = False

class ContentCreate(ContentBase):
    tags: Optional[List[str]] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    subject: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    content_data: Optional[Dict[str, Any]] = None
    visual_affinity: Optional[float] = Field(None, ge=0, le=100)
    auditory_affinity: Optional[float] = Field(None, ge=0, le=100)
    kinesthetic_affinity: Optional[float] = Field(None, ge=0, le=100)
    reading_affinity: Optional[float] = Field(None, ge=0, le=100)
    author: Optional[str] = None
    source_url: Optional[str] = None
    is_premium: Optional[bool] = None
    tags: Optional[List[str]] = None

class Content(ContentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[ContentTag] = []
    
    class Config:
        from_attributes = True

class ContentResponse(ContentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[ContentTagResponse] = []  # 使用明确的标签响应类型

    class Config:
        from_attributes = True

class ContentRecommendation(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content_type: str
    subject: str
    match_score: float
    explanation: str
    content_data: Optional[Dict[str, Any]] = None

# Interaction models
class ContentInteractionBase(BaseModel):
    content_id: int
    interaction_type: str
    progress: Optional[float] = Field(0.0, ge=0, le=100)
    rating: Optional[int] = Field(None, ge=1, le=5)
    time_spent: Optional[float] = None
    difficulty_feedback: Optional[int] = Field(None, ge=1, le=5)
    relevance_feedback: Optional[int] = Field(None, ge=1, le=5)
    engagement_feedback: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

class ContentInteractionCreate(ContentInteractionBase):
    pass

class ContentInteraction(ContentInteractionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Recommendation models
class ContentRecommendationRequest(BaseModel):
    user_id: int
    subject: Optional[str] = None
    content_type: Optional[str] = None
    difficulty_range: Optional[List[int]] = None
    limit: int = 10
    exclude_viewed: bool = True
    exclude_ids: Optional[List[int]] = None

class RecommendationItem(BaseModel):
    content: Content
    explanation: str
    approach_suggestion: str

class ContentRecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    recommendation_factors: Dict[str, Any]

    class Config:
        from_attributes = True

# Content search models
class ContentSearchParams(BaseModel):
    query: Optional[str] = None
    subject: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty_min: Optional[int] = Field(None, ge=1, le=5)
    difficulty_max: Optional[int] = Field(None, ge=1, le=5)
    learning_style: Optional[str] = None
    limit: int = 20
    offset: int = 0

class ContentSearchResponse(BaseModel):
    results: List[Content]
    total: int
    limit: int
    offset: int