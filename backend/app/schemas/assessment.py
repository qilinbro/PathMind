from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    options: Dict[str, str]
    category: str
    weight: float

class AssessmentQuestion(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    category: str
    weight: float = 1.0
    
    class Config:
        from_attributes = True

class ResponseInput(BaseModel):
    question_id: int
    response_value: Dict[str, Any]
    response_time: float

class AssessmentResponseItem(BaseModel):
    question_id: int
    response_value: Dict[str, Any]
    response_time: float

class AssessmentSubmission(BaseModel):
    user_id: int
    responses: List[AssessmentResponseItem]

class LearningStyleResult(BaseModel):
    visual_score: float
    auditory_score: float
    kinesthetic_score: float
    reading_score: float
    dominant_style: str
    secondary_style: Optional[str] = None

class Recommendation(BaseModel):
    type: str
    title: str
    description: str
    methods: List[str]
    specific_tools: Optional[List[str]] = None

class AssessmentResponse(BaseModel):
    learning_style_result: LearningStyleResult
    recommendations: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class AssessmentHistoryItem(BaseModel):
    id: int
    created_at: datetime
    visual_score: float
    auditory_score: float
    kinesthetic_score: float
    reading_score: float
    dominant_style: str

class AdaptiveTestRequest(BaseModel):
    user_id: int
    subject: str
    topic: str
    difficulty: str = "auto"  # "auto", "beginner", "easy", "medium", "hard", "expert"

class AdaptiveTestQuestion(BaseModel):
    """自适应测试问题模型"""
    id: int
    content: str
    question_type: str
    options: Optional[List[str]] = None  # 改为可选字段
    difficulty: Optional[str] = None  # 允许使用字符串难度级别
    topic: str

class AdaptiveTestLogic(BaseModel):
    """自适应测试逻辑模型"""
    initial_difficulty: Optional[str] = None  # 允许字符串难度值
    adjustment_rules: Dict[str, Any]  # 使用Any类型更灵活
    topic_focus: Optional[str] = None
    personalization_factors: Optional[List[str]] = None

class AdaptiveTestResult(BaseModel):
    """自适应测试结果模型，适配智谱AI输出"""
    questions: List[AdaptiveTestQuestion]
    adaptive_logic: AdaptiveTestLogic
    estimated_difficulty: Optional[str] = None  # 允许字符串难度值
    topics_covered: Optional[List[str]] = None  # 添加涵盖的主题字段
    
    class Config:
        from_attributes = True
        # 添加额外属性以允许灵活的返回格式
        extra = "allow"

class SuggestedResource(BaseModel):
    """学习资源推荐模型"""
    type: str
    title: str
    url: Optional[str] = None

class WeaknessArea(BaseModel):
    """学习弱点领域模型"""
    topic: str
    confidence_level: float
    suggested_resources: List[SuggestedResource]

class StrengthArea(BaseModel):
    """学习优势领域模型"""
    topic: str
    confidence_level: float

class ImprovementPlan(BaseModel):
    """改进计划模型"""
    short_term_goals: List[str]
    long_term_goals: List[str]
    recommended_study_path: str

class WeaknessAnalysisResult(BaseModel):
    """弱点分析结果模型，适配智谱AI输出"""
    weak_areas: List[WeaknessArea]
    strength_areas: List[StrengthArea]
    improvement_plan: ImprovementPlan
    
    class Config:
        from_attributes = True

class CommonMistake(BaseModel):
    """常见错误模型"""
    topic: str
    frequency: str
    examples: List[str]
    remediation: str

class MistakePatterns(BaseModel):
    """错误模式模型"""
    time_of_day: Optional[str] = None
    subject_correlation: Optional[str] = None
    difficulty_correlation: Optional[str] = None

class RemediationPlan(BaseModel):
    """改进计划模型"""
    focus_areas: List[str]
    suggested_exercises: List[str]
    learning_materials: List[str]

class MistakeAnalysisResult(BaseModel):
    """错误分析结果模型，适配智谱AI输出"""
    common_mistakes: List[CommonMistake]
    mistake_patterns: MistakePatterns
    remediation_plan: RemediationPlan
    
    class Config:
        from_attributes = True

class BehaviorPatterns(BaseModel):
    """行为模式模型"""
    study_consistency: Optional[str] = None
    focus_level: Optional[str] = None
    preferred_time: Optional[str] = None
    learning_pace: Optional[str] = None

class LearningAnalysis(BaseModel):
    """学习分析结果模型，适配智谱AI输出"""
    behavior_patterns: BehaviorPatterns
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    optimal_content_types: List[str]
    
    class Config:
        from_attributes = True

class ContentRecommendationItem(BaseModel):
    """内容推荐项模型"""
    content: Dict[str, Any]
    explanation: str
    approach_suggestion: str
    
    class Config:
        from_attributes = True

class AssessmentResult(BaseModel):
    """评估结果模型"""
    assessment_id: int
    learning_style_result: LearningStyleResult
    recommendations: List[ContentRecommendationItem]
    
    class Config:
        from_attributes = True

class ProgressMetrics(BaseModel):
    """学习进度指标模型"""
    completed_contents: int
    average_score: float
    study_time: float
    content_engagement: float

class LearningProgress(BaseModel):
    """学习进度模型"""
    user_id: int
    latest_assessment_id: Optional[int] = None
    latest_assessment_date: Optional[datetime] = None
    current_learning_style: Dict[str, Any]
    progress_metrics: ProgressMetrics
    improvement_suggestions: List[str]
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class ZhipuAIRequest(BaseModel):
    """智谱AI请求模型"""
    model: str = "glm-4-plus"
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.8
    
    class Config:
        from_attributes = True

class ZhipuAIResponse(BaseModel):
    """智谱AI响应模型"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    
    class Config:
        from_attributes = True