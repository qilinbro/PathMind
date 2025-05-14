from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import app.models.user
import app.models.content

class ContentInteraction(Base):
    """用户与学习内容交互记录"""
    __tablename__ = "content_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("learning_contents.id"))
    
    # 交互类型：view, complete, quiz_attempt, etc.
    interaction_type = Column(String, nullable=False)
    
    # 交互数据：例如测验分数、观看时长等
    interaction_data = Column(JSON, nullable=True)
    
    # 学习时长（分钟）
    learning_duration = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 修改这里：将 back_populates 从 "interactions" 改为 "content_interactions"
    user = relationship("User", back_populates="interaction_records")
    content = relationship("LearningContent", back_populates="content_interactions") 
    
    def __repr__(self):
        return f"<ContentInteraction {self.id}: User {self.user_id} - Content {self.content_id}>"
