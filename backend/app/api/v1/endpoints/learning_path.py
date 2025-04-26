from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.learning_path import LearningPath, PathEnrollment
from app.models.content import LearningContent
from app.models.user import User
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

# 创建路由器和AI服务实例
router = APIRouter()
ai_service = AIService()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    path_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """创建新的学习路径"""
    try:
        logger.info(f"创建学习路径: {path_data['title']}")
        
        # 检查创建者是否存在
        user_id = path_data.get("created_by")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404, 
                    detail=f"创建者用户ID {user_id} 不存在"
                )
        
        # 准备路径元数据
        path_metadata = {
            "goals": path_data.get("goals", []),
            "prerequisites": path_data.get("prerequisites", []),
            "difficulty": path_data.get("difficulty", "beginner")
        }
        
        # 创建路径对象
        db_path = LearningPath(
            title=path_data["title"],
            description=path_data.get("description", ""),
            subject=path_data["subject"],
            difficulty_level=path_data.get("difficulty_level", 2),
            estimated_hours=path_data.get("estimated_hours"),
            path_metadata=path_metadata,
            created_by=user_id
        )
        
        db.add(db_path)
        db.commit()
        db.refresh(db_path)
        
        # 返回创建的路径
        return {
            "id": db_path.id,
            "title": db_path.title,
            "description": db_path.description,
            "subject": db_path.subject,
            "difficulty_level": db_path.difficulty_level,
            "estimated_hours": db_path.estimated_hours,
            "created_by": db_path.created_by,
            "created_at": db_path.created_at
        }
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        db.rollback()
        logger.exception(f"创建学习路径失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建学习路径失败: {str(e)}"
        )

@router.post("/enroll")
async def enroll_in_learning_path(
    enrollment_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """注册学习路径"""
    try:
        user_id = enrollment_data["user_id"]
        path_id = enrollment_data["path_id"]
        
        # 检查用户和路径是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
            
        path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
        if not path:
            raise HTTPException(status_code=404, detail=f"学习路径ID {path_id} 不存在")
        
        # 检查是否已注册
        existing_enrollment = (
            db.query(PathEnrollment)
            .filter(
                PathEnrollment.user_id == user_id,
                PathEnrollment.path_id == path_id
            )
            .first()
        )
        
        if existing_enrollment:
            return {
                "id": existing_enrollment.id,
                "user_id": existing_enrollment.user_id,
                "path_id": existing_enrollment.path_id,
                "progress": existing_enrollment.progress,
                "enrolled_at": existing_enrollment.enrolled_at,
                "content_progress": existing_enrollment.content_progress or {}
            }
        
        # 创建新的注册
        personalization_settings = enrollment_data.get("personalization_settings", {})
        
        db_enrollment = PathEnrollment(
            user_id=user_id,
            path_id=path_id,
            progress=0.0,
            content_progress={},
            personalization_settings=personalization_settings
        )
        
        db.add(db_enrollment)
        db.commit()
        db.refresh(db_enrollment)
        
        return {
            "id": db_enrollment.id,
            "user_id": db_enrollment.user_id,
            "path_id": db_enrollment.path_id,
            "progress": db_enrollment.progress,
            "enrolled_at": db_enrollment.enrolled_at,
            "content_progress": db_enrollment.content_progress or {}
        }
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        db.rollback()
        logger.exception(f"注册学习路径失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"注册学习路径失败: {str(e)}"
        )

@router.get("/{path_id}")
async def get_learning_path(
    path_id: int,
    user_id: Optional[int] = None,
    subject_area: Optional[str] = Query(None, description="主题领域"),
    target_level: Optional[str] = Query(None, description="目标级别"),
    db: Session = Depends(get_db)
):
    """获取学习路径详情"""
    try:
        path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
        
        # 如果数据库中找不到路径，使用AI生成路径
        if not path:
            logger.info(f"学习路径ID {path_id} 不存在，使用AI生成")
            try:
                # 准备参数
                subject = subject_area or "编程与开发"  # 默认主题
                path_name = f"Learning Path {path_id}"  # 默认路径名
                level = target_level or "beginner"      # 默认级别

                # 使用AI生成学习路径
                ai_path = await ai_service.generate_learning_analysis({
                    "user_id": str(path_id),
                    "study_time": "0",
                    "completion_rate": "0",
                    "interactions": "0",
                    "content_types": [subject],
                    "learning_goals": [f"Master {subject} at {level} level"],
                    "subject_area": subject,
                    "target_level": level
                })

                # 转换AI生成的路径为响应格式
                path_content = []
                if "recommendations" in ai_path and ai_path["recommendations"]:
                    for i, rec in enumerate(ai_path["recommendations"], 1):
                        content_type = "video" if "watch" in rec.lower() or "video" in rec.lower() else "interactive"
                        path_content.append({
                            "id": i,
                            "title": f"Step {i}",
                            "description": rec,
                            "content_type": content_type,
                            "subject": subject,
                            "difficulty_level": 1 if level == "beginner" else 2 if level == "intermediate" else 3
                        })

                return {
                    "id": path_id,
                    "title": f"{subject} Learning Path",
                    "description": ai_path.get("behavior_patterns", {}).get("study_consistency", "A customized learning path"),
                    "subject": subject,
                    "difficulty_level": 1 if level == "beginner" else 2 if level == "intermediate" else 3,
                    "estimated_hours": 25,
                    "contents": path_content,
                    "metadata": {
                        "goals": ai_path.get("strengths", []),
                        "prerequisites": [],
                        "difficulty": level
                    },
                    "user_progress": {
                        "overall_progress": 0,
                        "content_progress": {},
                        "enrolled_at": None
                    } if user_id else None
                }
            except Exception as e:
                logger.error(f"AI生成学习路径失败: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"生成学习路径失败: {str(e)}"
                )
        
        # 获取路径内容
        contents = []
        for content in path.contents:
            contents.append({
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type,
                "subject": content.subject,
                "difficulty_level": content.difficulty_level
            })
        
        # 如果提供了用户ID，获取用户在此路径上的进度
        user_progress = None
        if user_id:
            enrollment = (
                db.query(PathEnrollment)
                .filter(
                    PathEnrollment.user_id == user_id,
                    PathEnrollment.path_id == path_id
                )
                .first()
            )
            if enrollment:
                user_progress = {
                    "overall_progress": enrollment.progress,
                    "content_progress": enrollment.content_progress or {},
                    "enrolled_at": enrollment.enrolled_at
                }
        
        # 组装响应
        return {
            "id": path.id,
            "title": path.title,
            "description": path.description,
            "subject": path.subject,
            "difficulty_level": path.difficulty_level,
            "estimated_hours": path.estimated_hours,
            "metadata": path.path_metadata,
            "contents": contents,
            "user_progress": user_progress
        }
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        logger.exception(f"获取学习路径失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取学习路径失败: {str(e)}"
        )

@router.post("/{path_id}/progress")
async def update_path_progress(
    path_id: int,
    progress_data: Dict[str, Any],
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """更新学习路径进度"""
    try:
        # 检查注册记录是否存在
        enrollment = (
            db.query(PathEnrollment)
            .filter(
                PathEnrollment.user_id == user_id,
                PathEnrollment.path_id == path_id
            )
            .first()
        )
        
        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail=f"未找到用户ID {user_id} 在路径ID {path_id} 上的注册记录"
            )
        
        # 获取内容ID和进度
        content_id = progress_data.get("content_id")
        progress = progress_data.get("progress", 0)
        
        if content_id:
            # 检查内容是否存在
            content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
            if not content:
                raise HTTPException(status_code=404, detail=f"内容ID {content_id} 不存在")
            
            # 更新特定内容的进度
            content_progress = enrollment.content_progress or {}
            content_progress[str(content_id)] = progress
            enrollment.content_progress = content_progress
            
            # 重新计算总体进度
            if path_id in enrollment.content_progress:
                total_progress = sum(enrollment.content_progress.values()) / len(enrollment.content_progress)
                enrollment.progress = min(100, total_progress)
            
            db.commit()
            db.refresh(enrollment)
        
        return {
            "id": enrollment.id,
            "user_id": enrollment.user_id,
            "path_id": enrollment.path_id,
            "progress": enrollment.progress,
            "content_progress": enrollment.content_progress or {},
            "last_activity_at": enrollment.last_activity_at
        }
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        db.rollback()
        logger.exception(f"更新路径进度失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新路径进度失败: {str(e)}"
        )

# 修改为同时支持GET和POST请求
@router.get("/recommended", response_model=List[Dict[str, Any]])
@router.post("/recommended", response_model=List[Dict[str, Any]])
async def get_recommended_learning_paths(
    request: Request,
    user_id: int = Query(None, description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取推荐给用户的学习路径"""
    try:
        # 从POST请求体或查询参数获取用户ID
        if request.method == "POST":
            try:
                body = await request.json()
                if not user_id:
                    user_id = body.get("user_id")
            except:
                pass
                
        if not user_id:
            raise HTTPException(status_code=400, detail="必须提供用户ID")
            
        # 获取用户信息，包括学习偏好
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")

        # 使用AI服务生成推荐
        try:
            recommendations = await ai_service.generate_content_recommendations(user_id, limit=5)
            paths = []
            
            for rec in recommendations:
                content = rec["content"]
                paths.append({
                    "id": content["id"],
                    "title": content["title"],
                    "description": rec["explanation"],
                    "subject": "programming",  # 可以根据内容类型设置
                    "difficulty_level": 2,  # 可以从match_score推断
                    "estimated_hours": 20,
                    "created_at": None,
                    "content_count": 5,
                    "recommendation_reason": rec["approach_suggestion"]
                })
            
            return paths
            
        except Exception as e:
            logger.error(f"AI推荐生成失败: {str(e)}")
            # 如果AI推荐失败，回退到数据库查询
            
            # 获取用户已注册的路径ID
            enrolled_path_ids = [
                enrollment.path_id for enrollment in 
                db.query(PathEnrollment.path_id)
                .filter(PathEnrollment.user_id == user_id)
                .all()
            ]
            
            # 查询未注册的路径
            query = db.query(LearningPath)
            if enrolled_path_ids:
                query = query.filter(LearningPath.id.notin_(enrolled_path_ids))
            
            # 最多返回5条推荐
            paths = query.limit(5).all()
            
            # 格式化响应
            recommended = []
            for path in paths:
                content_count = len(path.contents) if path.contents else 0
                
                recommended.append({
                    "id": path.id,
                    "title": path.title,
                    "description": path.description,
                    "subject": path.subject,
                    "difficulty_level": path.difficulty_level,
                    "estimated_hours": path.estimated_hours,
                    "created_at": path.created_at,
                    "content_count": content_count
                })
            
            return recommended
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"获取推荐学习路径失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取推荐学习路径失败: {str(e)}"
        )
