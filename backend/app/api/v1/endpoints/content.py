from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.content import LearningContent, ContentTag
from app.schemas.content import ContentCreate, ContentResponse, ContentBase
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=List[ContentResponse])
def get_learning_contents(
    skip: int = 0,
    limit: int = 10,
    subject: str = None,
    content_type: str = None,
    difficulty_min: int = None,
    difficulty_max: int = None,
    db: Session = Depends(get_db)
):
    """获取学习内容列表，支持过滤和分页"""
    query = db.query(LearningContent)
    
    # 应用过滤条件
    if subject:
        query = query.filter(LearningContent.subject == subject)
    if content_type:
        query = query.filter(LearningContent.content_type == content_type)
    if difficulty_min is not None:
        query = query.filter(LearningContent.difficulty_level >= difficulty_min)
    if difficulty_max is not None:
        query = query.filter(LearningContent.difficulty_level <= difficulty_max)
    
    # 应用分页
    contents = query.offset(skip).limit(limit).all()
    
    # 手动将内容转换为响应模型，正确处理标签
    result = []
    for content in contents:
        # 将标签对象转换为字典
        tags_as_dict = []
        for tag in content.tags:
            tags_as_dict.append({"id": tag.id, "name": tag.name, "description": tag.description})
        
        # 创建响应对象
        content_dict = {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type,
            "subject": content.subject,
            "difficulty_level": content.difficulty_level,
            "content_data": content.content_data,
            "visual_affinity": content.visual_affinity,
            "auditory_affinity": content.auditory_affinity,
            "kinesthetic_affinity": content.kinesthetic_affinity,
            "reading_affinity": content.reading_affinity,
            "author": content.author,
            "source_url": content.source_url,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "is_premium": content.is_premium,
            "tags": tags_as_dict
        }
        result.append(content_dict)
    
    return result

@router.post("", response_model=ContentResponse)
def create_learning_content(
    content: ContentCreate,
    db: Session = Depends(get_db)
):
    """创建新的学习内容"""
    try:
        logger.info(f"创建新内容: {content.title}")
        
        # 创建内容对象
        db_content = LearningContent(
            title=content.title,
            description=content.description,
            content_type=content.content_type,
            subject=content.subject,
            difficulty_level=content.difficulty_level,
            content_data=content.content_data,
            visual_affinity=content.visual_affinity,
            auditory_affinity=content.auditory_affinity,
            kinesthetic_affinity=content.kinesthetic_affinity,
            reading_affinity=content.reading_affinity,
            author=content.author,
            source_url=content.source_url,
            is_premium=content.is_premium
        )
        
        # 处理标签
        if content.tags:
            for tag_name in content.tags:
                # 查找或创建标签
                tag = db.query(ContentTag).filter(ContentTag.name == tag_name).first()
                if not tag:
                    tag = ContentTag(name=tag_name)
                    db.add(tag)
                    db.flush()
                
                # 添加到内容的标签中
                db_content.tags.append(tag)
        
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        
        return db_content
    except Exception as e:
        db.rollback()
        logger.error(f"创建内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建内容失败: {str(e)}")

@router.get("/{content_id}", response_model=ContentResponse)
def get_content_by_id(
    content_id: int = Path(..., description="内容ID"),
    db: Session = Depends(get_db)
):
    """根据ID获取学习内容详情"""
    content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail=f"内容ID {content_id} 不存在")
    return content

@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_update: ContentBase,
    db: Session = Depends(get_db)
):
    """更新学习内容"""
    db_content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail=f"内容ID {content_id} 不存在")
    
    # 更新字段
    for key, value in content_update.dict().items():
        if hasattr(db_content, key) and value is not None:
            setattr(db_content, key, value)
    
    db.commit()
    db.refresh(db_content)
    return db_content

@router.delete("/{content_id}", response_model=Dict[str, Any])
def delete_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """删除学习内容"""
    db_content = db.query(LearningContent).filter(LearningContent.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail=f"内容ID {content_id} 不存在")
    
    db.delete(db_content)
    db.commit()
    return {"status": "success", "message": f"内容ID {content_id} 已删除"}