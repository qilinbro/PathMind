from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.content import UserContentInteraction
import logging

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

logger = logging.getLogger(__name__)

@router.post("/behavior", response_model=Dict[str, Any])
async def analyze_learning_behavior(
    behavior_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """分析用户的学习行为数据"""
    try:
        logger.info(f"处理学习行为分析: 用户ID {behavior_data.get('user_id')}")
        
        user_id = behavior_data.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="必须提供用户ID")
        
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 获取交互数据
        interactions = behavior_data.get("content_interactions", [])
        if not interactions:
            raise HTTPException(status_code=400, detail="必须提供内容交互数据")
        
        # 计算参与度
        engagement_level = calculate_engagement_level(interactions)
        
        # 识别行为模式
        behavior_patterns = identify_behavior_patterns(interactions, user)
        
        # 生成改进建议
        improvement_areas = generate_improvement_suggestions(behavior_patterns, user)
        
        # 保存分析结果
        try:
            # 将内容交互记录保存到数据库
            for interaction in interactions:
                db_interaction = UserContentInteraction(
                    user_id=user_id,
                    content_id=interaction.get("content_id"),
                    interaction_type=interaction.get("interaction_type", "view"),
                    progress=interaction.get("progress", 0) * 100,  # 转换为百分比
                    time_spent=interaction.get("time_spent"),
                    engagement_feedback=calculate_engagement_score(interaction)
                )
                db.add(db_interaction)
            db.commit()
        except Exception as save_error:
            logger.error(f"保存交互数据失败: {str(save_error)}")
            db.rollback()
            # 但继续返回分析结果
        
        return {
            "user_id": user_id,
            "engagement_level": engagement_level,
            "behavior_patterns": behavior_patterns,
            "improvement_areas": improvement_areas
        }
    except Exception as e:
        logger.exception(f"分析学习行为失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析学习行为失败: {str(e)}")

@router.get("/weaknesses/{user_id}", response_model=Dict[str, Any])
async def get_user_weaknesses(user_id: int, db: Session = Depends(get_db)):
    """识别用户的学习弱点和强项"""
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
        
        # 获取用户的内容交互记录
        interactions = (
            db.query(UserContentInteraction)
            .filter(UserContentInteraction.user_id == user_id)
            .all()
        )
        
        # 模拟弱点分析 - 实际应用中可能会有更复杂的算法
        weak_areas = [
            {
                "topic": "数据结构",
                "confidence_level": 0.35,
                "suggested_resources": [
                    {"type": "video", "title": "数据结构基础", "url": "https://example.com/ds101"}
                ]
            },
            {
                "topic": "算法复杂度",
                "confidence_level": 0.42,
                "suggested_resources": [
                    {"type": "article", "title": "复杂度分析简介", "url": "https://example.com/complexity"}
                ]
            }
        ]
        
        # 模拟强项分析
        strength_areas = [
            {"topic": "编程基础", "confidence_level": 0.85},
            {"topic": "Web开发", "confidence_level": 0.78}
        ]
        
        # 模拟改进计划
        improvement_plan = {
            "short_term_goals": ["完成数据结构基础课程", "每周解决5道算法题"],
            "long_term_goals": ["掌握高级数据结构", "能够独立分析算法复杂度"],
            "recommended_study_path": "先巩固基础知识，再通过实践加深理解"
        }
        
        return {
            "user_id": user_id,
            "weak_areas": weak_areas,
            "strength_areas": strength_areas,
            "improvement_plan": improvement_plan
        }
    except Exception as e:
        logger.exception(f"识别弱点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"识别弱点失败: {str(e)}")

# 辅助函数
def calculate_engagement_level(interactions: List[Dict[str, Any]]) -> str:
    """计算用户的参与度级别"""
    if not interactions:
        return "未知"
    
    # 简单版本 - 基于时间和互动计算平均参与度
    total_time = sum(interaction.get("time_spent", 0) for interaction in interactions)
    avg_progress = sum(interaction.get("progress", 0) for interaction in interactions) / len(interactions)
    
    if total_time > 3600 and avg_progress > 0.8:
        return "非常高"
    elif total_time > 1800 and avg_progress > 0.6:
        return "高"
    elif total_time > 900 and avg_progress > 0.4:
        return "中等"
    else:
        return "低"

def identify_behavior_patterns(interactions: List[Dict[str, Any]], user: Any) -> Dict[str, Any]:
    """识别用户的学习行为模式"""
    # 实际应用中会有更详细的分析
    return {
        "学习偏好": "互动式内容" if any(i.get("interaction_type") == "interactive" for i in interactions) else "被动式内容",
        "注意力持续时间": "长" if sum(i.get("time_spent", 0) for i in interactions) / len(interactions) > 1200 else "短",
        "学习频率": "高" if len(interactions) > 5 else "低",
        "学习风格匹配度": "高" if user and user.learning_style else "未确定"
    }

def generate_improvement_suggestions(behavior_patterns: Dict[str, Any], user: Any) -> List[str]:
    """基于行为模式和学习风格生成改进建议"""
    suggestions = []
    
    # 根据学习偏好添加建议
    if behavior_patterns.get("学习偏好") == "互动式内容":
        suggestions.append("尝试更多的实践项目和动手练习，这符合你的互动学习偏好。")
    else:
        suggestions.append("增加一些互动学习内容可能会提高你的学习效果。")
    
    # 根据注意力持续时间添加建议
    if behavior_patterns.get("注意力持续时间") == "短":
        suggestions.append("尝试番茄工作法，设置25分钟专注学习，然后短暂休息。")
    
    # 根据学习频率添加建议
    if behavior_patterns.get("学习频率") == "低":
        suggestions.append("建立固定的学习时间表，增加学习的频率和规律性。")
    
    # 添加一些通用建议
    suggestions.append("多样化学习内容类型，结合视频、阅读和实践。")
    suggestions.append("每完成一个知识点，尝试向别人解释，或写下笔记总结。")
    
    return suggestions

def calculate_engagement_score(interaction: Dict[str, Any]) -> int:
    """根据交互数据计算参与度分数（1-5）"""
    score = 3  # 默认中等参与度
    
    # 交互时间
    time_spent = interaction.get("time_spent", 0)
    if time_spent > 3000:  # 50分钟以上
        score += 2
    elif time_spent > 1800:  # 30分钟以上
        score += 1
    
    # 完成进度
    progress = interaction.get("progress", 0)
    if progress > 0.9:
        score += 1
    
    # 互动指标
    engagement_metrics = interaction.get("engagement_metrics", {})
    if engagement_metrics.get("notes_taken"):
        score += 1
    
    # 确保分数在1-5范围内
    return max(1, min(5, score))
