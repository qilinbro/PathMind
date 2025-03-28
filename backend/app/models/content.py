from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
# 添加导入以解决循环引用问题
import app.models.content_interaction
import app.models.learning_path

# Association table for many-to-many relationship between content and tags
content_tag_association = Table(
    "content_tag_associations",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("learning_contents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("learning_tags.id"), primary_key=True)
)

class LearningContent(Base):
    """Model for learning content items (articles, videos, exercises, etc.)"""
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)  # article, video, exercise, etc.
    subject = Column(String, nullable=False)  # math, science, language, etc.
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    
    # Content data - could be text, URL, or structured data
    content_data = Column(JSON, nullable=False)
    
    # Learning style affinities (0-100 scale)
    visual_affinity = Column(Float, default=25.0)
    auditory_affinity = Column(Float, default=25.0)
    kinesthetic_affinity = Column(Float, default=25.0)
    reading_affinity = Column(Float, default=25.0)
    
    # Metadata
    author = Column(String)
    source_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_premium = Column(Boolean, default=False)
    
    # Relationships
    tags = relationship("ContentTag", secondary=content_tag_association, back_populates="contents")
    user_interactions = relationship("UserContentInteraction", back_populates="content")
    interactions = relationship("ContentInteraction", back_populates="content")
    learning_paths = relationship("LearningPath", secondary="path_content_associations", back_populates="contents")
    
    def __repr__(self):
        return f"<LearningContent {self.id}: {self.title}>"

class ContentTag(Base):
    """Model for content tags/categories"""
    __tablename__ = "learning_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    # Relationships
    contents = relationship("LearningContent", secondary=content_tag_association, back_populates="tags")
    
    def __repr__(self):
        return f"<ContentTag {self.id}: {self.name}>"

class UserContentInteraction(Base):
    """Model for tracking user interactions with content"""
    __tablename__ = "user_content_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("learning_contents.id"))
    
    # Interaction data
    interaction_type = Column(String, nullable=False)  # view, complete, like, bookmark, etc.
    progress = Column(Float, default=0.0)  # 0-100% completion
    rating = Column(Integer)  # 1-5 stars
    time_spent = Column(Float)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Feedback data
    difficulty_feedback = Column(Integer)  # 1-5 scale (too easy to too hard)
    relevance_feedback = Column(Integer)  # 1-5 scale
    engagement_feedback = Column(Integer)  # 1-5 scale
    notes = Column(Text)
    
    # Relationships
    user = relationship("app.models.user.User", back_populates="content_interactions")
    content = relationship("LearningContent", back_populates="user_interactions")
    
    def __repr__(self):
        return f"<UserContentInteraction {self.id}: User {self.user_id} - Content {self.content_id}>"