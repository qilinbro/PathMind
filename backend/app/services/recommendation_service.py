import json
import logging
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy.orm import Session
from app.models.content import LearningContent, UserContentInteraction
from app.models.learning_assessment import LearningStyleAssessment
from app.models.user import User
from app.core.config import settings
from app.schemas.content import Content, RecommendationItem
from app.services.ai_service import AIService

# Configure logging
logger = logging.getLogger(__name__)

class RecommendationService:
    """处理内容推荐相关功能的服务类"""
    
    def __init__(self):
        self.ai_service = AIService(settings.ZHIPU_API_KEY)
    
    async def get_personalized_recommendations(
        self,
        db: Session,
        user_id: int,
        subject: Optional[str] = None,
        content_type: Optional[str] = None,
        difficulty_range: Optional[List[int]] = None,
        limit: int = 10,
        exclude_viewed: bool = True,
        exclude_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """获取针对特定用户的个性化内容推荐"""
        
        # 获取用户的学习风格偏好
        # 在实际应用中，应该从数据库获取用户最近的学习风格评估结果
        user_learning_style = {
            "visual_score": 75,
            "auditory_score": 60,
            "kinesthetic_score": 45,
            "reading_score": 65,
            "dominant_style": "visual"
        }
        
        # 获取用户已查看的内容ID列表
        viewed_content_ids = []
        if exclude_viewed:
            viewed_interactions = (
                db.query(UserContentInteraction.content_id)
                .filter(UserContentInteraction.user_id == user_id)
                .all()
            )
            viewed_content_ids = [interaction[0] for interaction in viewed_interactions]
        
        # 合并排除ID列表
        exclude_content_ids = list(set(viewed_content_ids + (exclude_ids or [])))
        
        # 查询可能的推荐内容
        query = db.query(LearningContent)
        
        # 应用过滤条件
        if subject:
            query = query.filter(LearningContent.subject == subject)
        if content_type:
            query = query.filter(LearningContent.content_type == content_type)
        if difficulty_range:
            query = query.filter(
                LearningContent.difficulty_level >= difficulty_range[0],
                LearningContent.difficulty_level <= difficulty_range[1]
            )
        if exclude_content_ids:
            query = query.filter(LearningContent.id.notin_(exclude_content_ids))
        
        # 获取可能的推荐内容
        potential_contents = query.limit(50).all()  # 获取多一些内容供AI选择
        
        if not potential_contents:
            # 如果没有找到可能的内容，返回空结果
            return {
                "recommendations": [],
                "recommendation_factors": {
                    "learning_style": user_learning_style,
                    "filters_applied": {
                        "subject": subject,
                        "content_type": content_type,
                        "exclude_viewed": exclude_viewed
                    }
                }
            }
        
        # 准备AI分析的内容数据
        content_data = []
        for content in potential_contents:
            content_tags = [tag.name for tag in content.tags]
            content_data.append({
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type,
                "subject": content.subject,
                "difficulty_level": content.difficulty_level,
                "visual_affinity": content.visual_affinity,
                "auditory_affinity": content.auditory_affinity,
                "kinesthetic_affinity": content.kinesthetic_affinity,
                "reading_affinity": content.reading_affinity,
                "tags": content_tags
            })
        
        # 使用AI服务生成推荐
        ai_recommendations = await self._generate_ai_recommendations(
            user_id=user_id,
            user_learning_style=user_learning_style,
            content_data=content_data,
            limit=limit
        )
        
        # 处理推荐结果
        recommendations = []
        for rec in ai_recommendations:
            # 查找对应的完整内容对象
            content_id = rec.get("content_id")
            content = next((c for c in potential_contents if c.id == content_id), None)
            
            if content:
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
                    "tags": [{"id": tag.id, "name": tag.name, "description": tag.description} for tag in content.tags]
                }
                
                recommendations.append({
                    "content": content_dict,
                    "explanation": rec.get("explanation", "This content aligns with your learning preferences"),
                    "approach_suggestion": rec.get("approach_suggestion", "Review thoroughly and practice with examples")
                })
        
        return {
            "recommendations": recommendations[:limit],
            "recommendation_factors": {
                "learning_style": user_learning_style,
                "filters_applied": {
                    "subject": subject,
                    "content_type": content_type,
                    "exclude_viewed": exclude_viewed
                },
                "ai_reasoning": ai_recommendations[0].get("reasoning_factors", {}) if ai_recommendations else {}
            }
        }
    
    async def _generate_ai_recommendations(
        self,
        user_id: int,
        user_learning_style: Dict[str, Any],
        content_data: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """使用AI服务生成内容推荐"""
        try:
            # 准备一个良好的提示
            dominant_style = user_learning_style.get("dominant_style", "visual")
            
            prompt = f"""
            You are an AI learning recommendation system. Please recommend {limit} learning contents for a user with the following learning style:
            
            Learning Style Profile:
            - Visual: {user_learning_style.get('visual_score', 0)}/100
            - Auditory: {user_learning_style.get('auditory_score', 0)}/100
            - Kinesthetic: {user_learning_style.get('kinesthetic_score', 0)}/100
            - Reading: {user_learning_style.get('reading_score', 0)}/100
            - Dominant style: {dominant_style}
            
            Available content items:
            {json.dumps(content_data, indent=2, ensure_ascii=False)}
            
            For each recommendation, provide:
            1. The content ID
            2. A personalized explanation of why this content matches their learning style
            3. A suggestion on how they should approach this content based on their learning style
            4. Key reasoning factors that influenced this recommendation
            
            Return your recommendations as a JSON array of objects with the following structure:
            [
              {{
                "content_id": 123,
                "explanation": "This content is recommended because...",
                "approach_suggestion": "Given your learning style, you should...",
                "reasoning_factors": {{ "key factors that influenced this recommendation": "explanation" }}
              }}
            ]
            
            Select the most appropriate content based on learning style match and provide insightful, personalized explanations.
            """
            
            # 使用AI服务生成推荐
            response = await asyncio.to_thread(
                self.ai_service.client.chat.completions.create,
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析返回结果
            result_text = response.choices[0].message.content
            return json.loads(result_text)
        except Exception as e:
            print(f"AI recommendation generation error: {str(e)}")
            
            # 回退到基于规则的推荐
            return self._fallback_recommendations(user_id, user_learning_style, content_data, limit)
    
    def _fallback_recommendations(
        self,
        user_id: int,
        user_learning_style: Dict[str, Any],
        content_data: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """提供基于规则的推荐，作为AI推荐的备选"""
        recommendations = []
        
        # 获取主要学习风格
        dominant_style = user_learning_style.get("dominant_style", "visual")
        
        # 基于学习风格对内容进行排序
        if dominant_style == "visual":
            sorted_content = sorted(content_data, key=lambda x: x.get("visual_affinity", 0), reverse=True)
        elif dominant_style == "auditory":
            sorted_content = sorted(content_data, key=lambda x: x.get("auditory_affinity", 0), reverse=True)
        elif dominant_style == "kinesthetic":
            sorted_content = sorted(content_data, key=lambda x: x.get("kinesthetic_affinity", 0), reverse=True)
        else:  # reading
            sorted_content = sorted(content_data, key=lambda x: x.get("reading_affinity", 0), reverse=True)
        
        # 生成推荐
        for content in sorted_content[:limit]:
            explanation = f"This content has high {dominant_style} learning affinity ({content.get(f'{dominant_style}_affinity', 0)}%)"
            
            if dominant_style == "visual":
                approach = "Focus on the diagrams and visual elements while studying this content"
            elif dominant_style == "auditory":
                approach = "Consider reading this content aloud or discussing it with others"
            elif dominant_style == "kinesthetic":
                approach = "Try to apply these concepts through hands-on exercises as you learn"
            else:  # reading
                approach = "Take detailed notes while reading through this material"
            
            recommendations.append({
                "content_id": content["id"],
                "explanation": explanation,
                "approach_suggestion": approach,
                "reasoning_factors": {
                    "learning_style_match": f"High {dominant_style} affinity",
                    "difficulty_level": f"Level {content['difficulty_level']} - appropriate for your progress"
                }
            })
        
        return recommendations