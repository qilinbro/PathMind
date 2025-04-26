from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.db.session import get_db
from app.models.content import LearningContent, ContentTag
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Dict[str, Any]])
async def get_content(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """获取学习内容列表"""
    try:
        # 获取内容
        contents = db.query(LearningContent).offset(skip).limit(limit).all()
        
        # 准备响应，确保所有可能为NULL的字段有默认值
        result = []
        for content in contents:
            # 获取标签
            tags = [tag.name for tag in content.tags] if hasattr(content, "tags") else []
            
            # 准备内容数据，确保亲和度字段有默认值
            content_data = {
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type,
                "subject": content.subject,
                "difficulty_level": content.difficulty_level,
                "content_url": content.content_url,
                # 为可能为NULL的字段提供默认值
                "visual_affinity": content.visual_affinity or 0.0,
                "auditory_affinity": content.auditory_affinity or 0.0,
                "kinesthetic_affinity": content.kinesthetic_affinity or 0.0,
                "reading_affinity": content.reading_affinity or 0.0,
                "tags": tags,
                "author": content.author,
                "is_premium": content.is_premium,
                "created_at": content.created_at
            }
            result.append(content_data)
            
        return result
    except Exception as e:
        logger.exception(f"获取内容列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取内容列表失败: {str(e)}"
        )

@router.post("", response_model=Dict[str, Any])
async def create_content(
    content: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """创建学习内容"""
    try:
        # 创建内容实例
        new_content = LearningContent(**content)
        db.add(new_content)
        db.commit()
        db.refresh(new_content)
        return new_content
    except Exception as e:
        logger.exception(f"创建内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建内容失败: {str(e)}"
        )

@router.get("/{content_id}", response_model=Dict[str, Any])
async def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db)
):
    """获取特定学习内容的详情"""
    try:
        content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"内容ID {content_id} 不存在"
            )
        
        # 获取标签
        tags = [tag.name for tag in content.tags] if hasattr(content, "tags") else []
        
        # 返回内容详情，确保亲和度字段有默认值
        return {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type,
            "content_url": content.content_url,
            "content_data": content.content_data,
            "subject": content.subject,
            "difficulty_level": content.difficulty_level,
            "estimated_minutes": content.estimated_minutes,
            "resources": content.resources,
            # 为可能为NULL的字段提供默认值
            "visual_affinity": content.visual_affinity or 0.0,
            "auditory_affinity": content.auditory_affinity or 0.0,
            "kinesthetic_affinity": content.kinesthetic_affinity or 0.0,
            "reading_affinity": content.reading_affinity or 0.0,
            "author": content.author,
            "source_url": content.source_url,
            "is_premium": content.is_premium or False,
            "tags": tags,
            "created_at": content.created_at,
            "updated_at": content.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"获取内容详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取内容详情失败: {str(e)}"
        )

@router.put("/{content_id}", response_model=Dict[str, Any])
async def update_content(
    content_id: int,
    content: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """更新学习内容"""
    try:
        db_content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
        
        if not db_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"内容ID {content_id} 不存在"
            )
        
        # 更新内容
        for key, value in content.items():
            setattr(db_content, key, value)
        
        db.commit()
        db.refresh(db_content)
        return db_content
    except Exception as e:
        logger.exception(f"更新内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新内容失败: {str(e)}"
        )

@router.delete("/{content_id}", response_model=Dict[str, Any])
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """删除学习内容"""
    try:
        content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"内容ID {content_id} 不存在"
            )
        
        db.delete(content)
        db.commit()
        return {"detail": f"内容ID {content_id} 已删除"}
    except Exception as e:
        logger.exception(f"删除内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除内容失败: {str(e)}"
        )