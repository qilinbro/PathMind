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
        return []
    finally:
        if close_db:
            db.close()
