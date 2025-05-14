from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
# 添加导入以解决循环引用问题
import app.models.content_interaction
import app.models.learning_path
from app.models.learning_path import path_content_association

# Association table for many-to-many relationship between content and tags
content_tag_association = Table(
    "content_tag_associations",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("learning_contents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("learning_tags.id"), primary_key=True)
)

class LearningContent(Base):
    """学习内容模型"""
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    content_type = Column(String, nullable=False)  # video, reading, interactive, etc.
    content_url = Column(String)
    content_data = Column(JSON)  # 存储额外的内容数据
    
    subject = Column(String)  # 学科/主题分类
    difficulty_level = Column(Integer, default=2)  # 1-5级难度
    estimated_minutes = Column(Integer)  # 预计完成时间（分钟）
    
    resources = Column(JSON)  # 相关学习资源
    
    # 添加这些字段以匹配API中的使用，并提供默认值
    visual_affinity = Column(Float, default=0.0)  # 添加默认值0.0
    auditory_affinity = Column(Float, default=0.0)  # 添加默认值0.0
    kinesthetic_affinity = Column(Float, default=0.0)  # 添加默认值0.0
    reading_affinity = Column(Float, default=0.0)  # 添加默认值0.0
    author = Column(String)
    source_url = Column(String)
    is_premium = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    learning_paths = relationship(
        "LearningPath", 
        secondary=path_content_association,
        back_populates="contents"
    )
    interactions = relationship("UserContentInteraction", back_populates="content")
    # 添加这个新的关系，匹配 ContentInteraction.content 的 back_populates
    content_interactions = relationship("app.models.content_interaction.ContentInteraction", back_populates="content")
    # 添加标签关系
    tags = relationship("ContentTag", secondary=content_tag_association, back_populates="contents")
    
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
    """用户与学习内容交互记录"""
    __tablename__ = "user_content_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("learning_contents.id"))
    
    # 交互类型：view, complete, quiz_attempt, etc.
    interaction_type = Column(String, nullable=False)
    
    # 进度百分比 (0-100)
    progress = Column(Float, default=0.0)
    
    # 是否已完成
    completed = Column(Boolean, default=False)
    
    # 用户评分 (1-5)
    rating = Column(Integer)
    
    # 学习时长（分钟）
    time_spent = Column(Float, default=0.0)
    
    # 参与反馈评分 (1-5)
    engagement_feedback = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="content_interactions")
    content = relationship("LearningContent", back_populates="interactions")
    
    def __repr__(self):
        return f"<UserContentInteraction {self.id}: User {self.user_id} - Content {self.content_id}>"