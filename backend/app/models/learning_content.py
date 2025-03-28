from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class LearningContent(Base):
    """学习内容模型"""
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # video, text, quiz, etc.
    description = Column(Text)
    content_url = Column(String)
    content_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user_interactions = relationship("ContentInteraction", back_populates="content")
    # 添加与学习路径的多对多关系
    learning_paths = relationship(
        "LearningPath",
        secondary="path_content_associations",
        back_populates="contents"
    )
    
    def __repr__(self):
        return f"<LearningContent {self.id}: {self.title}>"
