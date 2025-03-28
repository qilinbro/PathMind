from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
# 添加导入以解决循环引用问题
import app.models.user

class AssessmentQuestion(Base):
    """学习风格评估问题模型"""
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)  # scale, choice, etc.
    options = Column(JSON)  # For choice questions
    category = Column(String, nullable=False)  # visual, auditory, kinesthetic, reading
    weight = Column(Float, default=1.0)
    question_metadata = Column(JSON)
    
    # 关系
    responses = relationship("UserResponse", back_populates="question")
    
    def __repr__(self):
        return f"<AssessmentQuestion {self.id}: {self.category}>"

class LearningStyleAssessment(Base):
    """用户学习风格评估记录"""
    __tablename__ = "learning_style_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 评估结果（不同维度的得分）
    visual_score = Column(Float)
    auditory_score = Column(Float)
    kinesthetic_score = Column(Float)
    reading_score = Column(Float)
    
    # 优势学习风格
    dominant_style = Column(String)
    
    # 详细评估数据
    assessment_data = Column(JSON)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 使用app.models.user.User作为完整引用以避免循环导入问题
    user = relationship("app.models.user.User", back_populates="assessments")
    responses = relationship("UserResponse", back_populates="assessment")
    
    def __repr__(self):
        return f"<LearningStyleAssessment {self.id}: User {self.user_id}>"

class UserResponse(Base):
    """用户对评估问题的回答"""
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("learning_style_assessments.id"))
    question_id = Column(Integer, ForeignKey("assessment_questions.id"))
    
    # 修改字段类型为JSON以匹配测试脚本中的数据格式
    response_value = Column(JSON, nullable=False)
    
    # 添加响应时间字段
    response_time = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    assessment = relationship("LearningStyleAssessment", back_populates="responses")
    question = relationship("AssessmentQuestion", back_populates="responses")
    
    def __repr__(self):
        return f"<UserResponse {self.id}: Assessment {self.assessment_id} - Question {self.question_id}>"