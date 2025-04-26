from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.content import UserContentInteraction
from app.services.user_service import (
    get_user_by_id, 
    update_user_learning_style,
    get_user_learning_history,
    record_user_progress,
    get_user_activity_summary
)
import logging

router = APIRouter(prefix="/api/v1/users", tags=["users"])

logger = logging.getLogger(__name__)

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    try:
        user = await get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
            
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "learning_style": user.learning_style or {},
            "preferences": user.preferences or {}
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"获取用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.get("/{user_id}/history", response_model=List[Dict[str, Any]])
async def get_history(
    user_id: int = Path(..., description="用户ID"),
    limit: int = Query(20, description="返回记录的最大数量"),
    db: Session = Depends(get_db)
):
    """获取用户学习历史记录"""
    try:
        # 验证用户是否存在
        user = await get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 获取学习历史
        history = await get_user_learning_history(user_id, db)
        return history[:limit]
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"获取用户学习历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户学习历史失败: {str(e)}")

@router.post("/{user_id}/progress", response_model=Dict[str, Any])
async def record_progress(
    user_id: int,
    progress_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """记录用户学习进度"""
    try:
        # 验证用户是否存在
        user = await get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 验证必要参数
        if "content_id" not in progress_data:
            raise HTTPException(status_code=400, detail="缺少必要参数: content_id")
        
        content_id = progress_data["content_id"]
        
        # 记录进度
        success = await record_user_progress(user_id, content_id, progress_data, db)
        
        if not success:
            raise HTTPException(status_code=500, detail="记录进度失败，请检查日志")
            
        return {
            "success": True,
            "user_id": user_id,
            "content_id": content_id,
            "message": "进度已更新"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"记录学习进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"记录学习进度失败: {str(e)}")

@router.get("/{user_id}/summary", response_model=Dict[str, Any])
async def get_summary(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户学习活动摘要"""
    try:
        # 验证用户是否存在
        user = await get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 获取活动摘要
        summary = await get_user_activity_summary(user_id, db)
        return summary
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"获取用户活动摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户活动摘要失败: {str(e)}")
