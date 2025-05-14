from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
# 修正导入路径，直接导入需要的模型类
from app.models.user import User
from app.models.learning_assessment import LearningStyleAssessment
from app.models.learning_path import PathEnrollment, LearningPath

router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["user-progress"],
)

logger = logging.getLogger("backend")

@router.get("/progress/{user_id}")
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """获取用户的学习进度和最近活动"""
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    # 获取用户最近的评估结果
    user_assessment = db.query(LearningStyleAssessment).filter(
        LearningStyleAssessment.user_id == user_id
    ).order_by(LearningStyleAssessment.completed_at.desc()).first()
    
    # 计算用户的学习路径进度
    completed_paths = db.query(PathEnrollment).filter(
        PathEnrollment.user_id == user_id,
        PathEnrollment.progress >= 100
    ).count()
    
    active_paths = db.query(PathEnrollment).filter(
        PathEnrollment.user_id == user_id,
        PathEnrollment.progress < 100,
        PathEnrollment.progress > 0
    ).count()
    
    # 获取最近活动（这里简化处理，实际应该包括评估、测试和学习路径活动）
    recent_activities = []
    
    # 如果有评估记录，添加到活动中
    if user_assessment:
        learning_style = user_assessment.dominant_style
        recent_activities.append({
            "id": 1,
            "type": "assessment",
            "title": "学习风格评估",
            "date": user_assessment.completed_at.strftime("%Y-%m-%d"),
            "result": f"{learning_style.capitalize() if learning_style else '未知'} 学习者"
        })
    else:
        learning_style = "未知"
    
    # 获取用户注册的学习路径活动
    path_enrollments = db.query(PathEnrollment, LearningPath).join(
        LearningPath, PathEnrollment.path_id == LearningPath.id
    ).filter(
        PathEnrollment.user_id == user_id
    ).order_by(
        PathEnrollment.last_activity_at.desc()
    ).limit(5).all()
    
    # 添加学习路径活动
    for i, (enrollment, path) in enumerate(path_enrollments):
        activity_id = len(recent_activities) + 1
        recent_activities.append({
            "id": activity_id,
            "type": "path",
            "title": path.title,
            "date": enrollment.last_activity_at.strftime("%Y-%m-%d") if enrollment.last_activity_at else 
                  enrollment.enrolled_at.strftime("%Y-%m-%d"),
            "progress": int(enrollment.progress) if enrollment.progress else 0
        })
    
    # 如果没有活动，添加一个默认活动
    if not recent_activities:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        recent_activities = [
            {
                "id": 2,
                "type": "path",
                "title": "Python基础入门",
                "date": yesterday.strftime("%Y-%m-%d"),
                "progress": 15
            }
        ]
    
    # 计算总体进度（简化版，实际应该基于更复杂的计算）
    overall_progress = 0
    if completed_paths > 0 or active_paths > 0:
        overall_progress = int((completed_paths / (completed_paths + active_paths)) * 100) if (completed_paths + active_paths) > 0 else 0
    
    # 返回用户进度数据
    return {
        "name": user.name if hasattr(user, "name") and user.name else 
               (user.full_name if hasattr(user, "full_name") and user.full_name else
               (user.username if hasattr(user, "username") else "用户")),
        "email": user.email,
        "learning_style": learning_style,
        "overall_progress": overall_progress,
        "completed_paths": completed_paths,
        "active_paths": active_paths,
        "completed_tests": 0,  # 应从测试结果表中查询
        "recent_activities": recent_activities
    }
