from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.session import get_db

async def get_user_by_id(user_id: int, db: Session = None) -> Optional[User]:
    """根据ID获取用户"""
    if db is None:
        # 如果没有提供数据库会话，创建一个新的
        db_generator = get_db()
        db = next(db_generator)
        close_db = True
    else:
        close_db = False
    
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        if close_db:
            db.close()

async def update_user_learning_style(user_id: int, learning_style: Dict[str, Any], db: Session = None) -> bool:
    """更新用户的学习风格信息"""
    if db is None:
        db_generator = get_db()
        db = next(db_generator)
        close_db = True
    else:
        close_db = False
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.learning_style = learning_style
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False
    finally:
        if close_db:
            db.close()

async def get_user_learning_history(user_id: int, db: Session = None) -> List[Dict[str, Any]]:
    """获取用户的学习历史"""
    if db is None:
        db_generator = get_db()
        db = next(db_generator)
        close_db = True
    else:
        close_db = False
    
    try:
        # 获取用户内容交互记录
        from app.models.content import UserContentInteraction, LearningContent
        
        interactions = (
            db.query(
                UserContentInteraction, 
                LearningContent.title, 
                LearningContent.content_type
            )
            .join(LearningContent)
            .filter(UserContentInteraction.user_id == user_id)
            .order_by(UserContentInteraction.created_at.desc())
            .all()
        )
        
        history = []
        for interaction, title, content_type in interactions:
            history.append({
                "content_id": interaction.content_id,
                "title": title,
                "content_type": content_type,
                "interaction_type": interaction.interaction_type,
                "progress": interaction.progress,
                "rating": interaction.rating,
                "time_spent": interaction.time_spent,
                "created_at": interaction.created_at
            })
        
        return history
    except Exception as e:
        print(f"获取用户历史记录错误: {str(e)}")
        return []  # 返回空列表而不是None
    finally:
        if close_db:
            db.close()

async def record_user_progress(
    user_id: int, 
    content_id: int, 
    progress_data: Dict[str, Any],
    db: Session = None
) -> bool:
    """记录用户的学习进度"""
    if db is None:
        db_generator = get_db()
        db = next(db_generator)
        close_db = True
    else:
        close_db = False
    
    try:
        from app.models.content import UserContentInteraction, LearningContent
        
        # 检查内容是否存在
        content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
        if not content:
            print(f"内容ID {content_id} 不存在")
            return False
        
        # 获取现有交互记录，如果有的话
        interaction = (
            db.query(UserContentInteraction)
            .filter(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content_id
            )
            .first()
        )
        
        # 解析进度数据
        progress = progress_data.get("progress", 0)
        time_spent = progress_data.get("time_spent", 0)
        rating = progress_data.get("rating")
        completed = progress_data.get("completed", False)
        
        if interaction:
            # 更新现有记录
            interaction.progress = max(interaction.progress, progress)
            interaction.time_spent = (interaction.time_spent or 0) + time_spent
            if rating is not None:
                interaction.rating = rating
            interaction.completed = completed or interaction.completed
            
        else:
            # 创建新记录
            interaction = UserContentInteraction(
                user_id=user_id,
                content_id=content_id,
                interaction_type="view",
                progress=progress,
                time_spent=time_spent,
                rating=rating,
                completed=completed
            )
            db.add(interaction)
        
        db.commit()
        return True
    
    except Exception as e:
        db.rollback()
        print(f"记录用户进度错误: {str(e)}")
        return False
        
    finally:
        if close_db:
            db.close()

async def get_user_activity_summary(user_id: int, db: Session = None) -> Dict[str, Any]:
    """获取用户活动摘要"""
    if db is None:
        db_generator = get_db()
        db = next(db_generator)
        close_db = True
    else:
        close_db = False
    
    try:
        from app.models.content import UserContentInteraction
        from sqlalchemy import func
        
        # 获取总学习时间
        total_time_result = (
            db.query(func.sum(UserContentInteraction.time_spent))
            .filter(UserContentInteraction.user_id == user_id)
            .first()
        )
        total_time = total_time_result[0] if total_time_result[0] else 0
        
        # 获取完成的内容数量
        completed_count = (
            db.query(func.count())
            .filter(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.completed == True
            )
            .scalar()
        )
        
        # 获取平均进度
        avg_progress_result = (
            db.query(func.avg(UserContentInteraction.progress))
            .filter(UserContentInteraction.user_id == user_id)
            .first()
        )
        avg_progress = avg_progress_result[0] if avg_progress_result[0] else 0
        
        # 获取最近的活动
        recent_activities = await get_user_learning_history(user_id, db=db)
        recent_activities = recent_activities[:5]  # 只返回最近5条
        
        return {
            "total_study_time": total_time,
            "completed_contents": completed_count,
            "average_progress": avg_progress,
            "recent_activities": recent_activities
        }
        
    except Exception as e:
        print(f"获取用户活动摘要错误: {str(e)}")
        return {
            "total_study_time": 0,
            "completed_contents": 0,
            "average_progress": 0,
            "recent_activities": []
        }
        
    finally:
        if close_db:
            db.close()
