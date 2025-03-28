from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.config import settings
from app.services.ai_service import AIService
from app.db.session import get_db
from app.models.learning_assessment import LearningStyleAssessment, UserResponse, AssessmentQuestion
from app.models.user import User

router = APIRouter(prefix="/api/v1/assessment", tags=["assessment"])

# 模型定义
class AdaptiveTestRequest(BaseModel):
    user_id: int
    subject: str
    topic: str
    difficulty: str

class AssessmentResponse(BaseModel):
    question_id: int
    response_value: Dict[str, Any]
    response_time: float

class AssessmentSubmission(BaseModel):
    user_id: int
    responses: List[AssessmentResponse]

class AdaptiveTestResult(BaseModel):
    questions: List[Dict[str, Any]]
    adaptive_logic: Dict[str, Any]
    estimated_difficulty: float

# 路由实现
@router.post("/submit/", response_model=Dict[str, Any])
async def submit_assessment(submission: AssessmentSubmission, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """处理用户提交的评估并返回学习风格结果和建议"""
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == submission.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {submission.user_id} 不存在")
        
        # 初始化AI服务
        ai_service = AIService(settings.ZHIPU_API_KEY)
        
        # 处理和存储用户回答
        raw_responses = []
        db_responses = []
        
        for response in submission.responses:
            # 检查问题是否存在
            question = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == response.question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"问题ID {response.question_id} 不存在")
                
            # 准备原始回答数据用于AI分析
            raw_responses.append({
                "question_id": response.question_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "category": question.category,
                "response_value": response.response_value,
                "response_time": response.response_time
            })
            
            # 创建数据库回答记录
            db_response = UserResponse(
                user_id=submission.user_id,
                question_id=question.id,
                response_value=response.response_value,
                response_time=response.response_time
            )
            db_responses.append(db_response)
        
        # 使用AI分析学习风格
        learning_style = await ai_service.analyze_learning_style(raw_responses)
        
        # 创建学习风格评估记录
        assessment = LearningStyleAssessment(
            user_id=submission.user_id,
            visual_score=learning_style.get("visual_score"),
            auditory_score=learning_style.get("auditory_score"),
            kinesthetic_score=learning_style.get("kinesthetic_score"),
            reading_score=learning_style.get("reading_score"),
            responses={"raw_responses": raw_responses},
            analysis_results=learning_style
        )
        db.add(assessment)
        db.flush()  # 获取ID但不提交
        
        # 将评估ID添加到响应中
        for db_response in db_responses:
            db_response.assessment_id = assessment.id
            db.add(db_response)
        
        # 基于学习风格生成内容推荐
        recommendations = await ai_service.generate_content_recommendations(
            user_id=submission.user_id,
            subject=None,  # 这里可以从用户偏好中获取
            limit=5
        )
        
        # 保存推荐到评估记录
        assessment.recommendations = {"items": recommendations}
        
        # 更新用户的学习风格信息
        user.learning_style = learning_style
        
        # 提交所有更改
        db.commit()
        
        # 返回结果
        return {
            "learning_style_result": learning_style,
            "recommendations": recommendations
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估提交失败: {str(e)}"
        )

@router.get("/progress/{user_id}", response_model=Dict[str, Any])
async def get_learning_progress(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """获取用户的学习进度和个性化建议"""
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 初始化AI服务
        ai_service = AIService(settings.ZHIPU_API_KEY)
        
        # 获取用户的最新学习风格评估
        latest_assessment = (
            db.query(LearningStyleAssessment)
            .filter(LearningStyleAssessment.user_id == user_id)
            .order_by(LearningStyleAssessment.created_at.desc())
            .first()
        )
        
        # 如果没有评估记录，返回基本信息
        if not latest_assessment:
            return {
                "user_id": user_id,
                "current_learning_style": {
                    "visual": 25,
                    "auditory": 25,
                    "kinesthetic": 25,
                    "reading": 25,
                    "dominant": "unknown"
                },
                "progress_metrics": {
                    "completed_contents": 0,
                    "average_score": 0,
                    "study_time": 0,
                    "content_engagement": 0
                },
                "improvement_suggestions": [
                    "完成学习风格评估以获取个性化建议"
                ]
            }
        
        # 获取用户的内容交互记录
        from app.models.content import UserContentInteraction
        
        interactions = (
            db.query(UserContentInteraction)
            .filter(UserContentInteraction.user_id == user_id)
            .all()
        )
        
        # 计算学习指标
        completed_count = sum(1 for i in interactions if i.progress >= 90)
        avg_rating = sum(i.rating for i in interactions if i.rating) / sum(1 for i in interactions if i.rating) if any(i.rating for i in interactions) else 0
        total_time = sum(i.time_spent for i in interactions if i.time_spent)
        avg_engagement = sum(i.engagement_feedback for i in interactions if i.engagement_feedback) / sum(1 for i in interactions if i.engagement_feedback) if any(i.engagement_feedback for i in interactions) else 0
        
        # 准备学习进度数据
        progress_data = {
            "user_id": user_id,
            "learning_style": {
                "visual": latest_assessment.visual_score,
                "auditory": latest_assessment.auditory_score,
                "kinesthetic": latest_assessment.kinesthetic_score,
                "reading": latest_assessment.reading_score
            },
            "interaction_metrics": {
                "completed_count": completed_count,
                "average_rating": avg_rating,
                "total_time": total_time,
                "average_engagement": avg_engagement
            }
        }
        
        # 使用AI生成学习进度分析和建议
        try:
            ai_analysis = await ai_service.generate_learning_analysis(progress_data)
            
            improvement_suggestions = ai_analysis.get("recommendations", [
                "基于您的学习风格，尝试更多视觉化学习材料" if latest_assessment.visual_score > 60 else 
                "基于您的学习风格，尝试更多听觉化学习材料" if latest_assessment.auditory_score > 60 else
                "基于您的学习风格，尝试更多动手实践学习" if latest_assessment.kinesthetic_score > 60 else
                "基于您的学习风格，尝试更多阅读和笔记学习" if latest_assessment.reading_score > 60 else
                "尝试多种学习方式以找出最适合您的方法"
            ])
            
            # 确定主导学习风格
            scores = {
                "visual": latest_assessment.visual_score,
                "auditory": latest_assessment.auditory_score,
                "kinesthetic": latest_assessment.kinesthetic_score,
                "reading": latest_assessment.reading_score
            }
            dominant_style = max(scores, key=scores.get)
            
            return {
                "user_id": user_id,
                "latest_assessment_id": latest_assessment.id,
                "latest_assessment_date": latest_assessment.created_at,
                "current_learning_style": {
                    "visual": latest_assessment.visual_score,
                    "auditory": latest_assessment.auditory_score,
                    "kinesthetic": latest_assessment.kinesthetic_score,
                    "reading": latest_assessment.reading_score,
                    "dominant": dominant_style
                },
                "progress_metrics": {
                    "completed_contents": completed_count,
                    "average_score": avg_rating,
                    "study_time": total_time,
                    "content_engagement": avg_engagement
                },
                "improvement_suggestions": improvement_suggestions,
                "strengths": ai_analysis.get("strengths", []),
                "weaknesses": ai_analysis.get("weaknesses", [])
            }
        except Exception as e:
            print(f"AI分析失败: {str(e)}")
            # 失败时返回基本分析
            return {
                "current_learning_style": {
                    "visual": latest_assessment.visual_score,
                    "auditory": latest_assessment.auditory_score,
                    "kinesthetic": latest_assessment.kinesthetic_score,
                    "reading": latest_assessment.reading_score,
                    "dominant": latest_assessment.analysis_results.get("dominant_style") if latest_assessment.analysis_results else "unknown"
                },
                "progress_metrics": {
                    "completed_contents": completed_count,
                    "average_score": avg_rating,
                    "study_time": total_time,
                    "content_engagement": avg_engagement
                },
                "improvement_suggestions": [
                    "尝试更多视觉化学习材料",
                    "增加学习时间",
                    "参与更多互动练习"
                ]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习进度失败: {str(e)}"
        )

@router.post("/adaptive-test", response_model=AdaptiveTestResult)
async def create_adaptive_test(request: AdaptiveTestRequest) -> Dict[str, Any]:
    """创建自适应测试，根据用户特点调整难度"""
    # 初始化AI服务
    ai_service = AIService(settings.ZHIPU_API_KEY)
    
    # 准备测试生成数据
    user_data = {
        "user_id": request.user_id,
        "subject": request.subject,
        "topic": request.topic,
        "difficulty": request.difficulty
    }
    
    try:
        # 使用AI服务生成自适应测试
        test_result = await ai_service.generate_adaptive_test(user_data)
        return test_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试失败: {str(e)}"
        )
