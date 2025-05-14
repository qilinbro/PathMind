from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
# 添加导入以解决循环引用问题
import app.models.content_interaction
import app.models.content

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 用户的学习风格和偏好
    learning_style = Column(JSON)
    preferences = Column(JSON)
    
    # 关系
    # 修正assessments关系定义
    assessments = relationship("app.models.learning_assessment.LearningStyleAssessment", back_populates="user")
    # 其他关系保持不变
    content_interactions = relationship("app.models.content.UserContentInteraction", back_populates="user")
    # 修改这里，确保与ContentInteraction中的back_populates值匹配
    interaction_records = relationship("ContentInteraction", back_populates="user")
    created_paths = relationship("LearningPath", foreign_keys="LearningPath.created_by", back_populates="author")
    path_enrollments = relationship("PathEnrollment", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.email}>"