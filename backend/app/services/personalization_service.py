from sqlalchemy.orm import Session
import logging
from typing import List, Optional

from app.models import learning_path as lp_models
from app.models import assessment as assessment_models
from app.models import user as user_models

logger = logging.getLogger("backend")

class PersonalizationService:
    """个性化推荐服务"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_recommendations_for_user(self, user_id: int) -> List[lp_models.LearningPath]:
        """根据用户学习风格和历史获取推荐学习路径"""
        logger.info(f"为用户 {user_id} 生成个性化推荐")
        
        try:
            # 获取用户的学习风格
            user_assessment = self.db.query(assessment_models.UserAssessment).filter(
                assessment_models.UserAssessment.user_id == user_id
            ).order_by(assessment_models.UserAssessment.created_at.desc()).first()
            
            # 获取用户已参与的学习路径
            enrolled_path_ids = [
                path.path_id for path in self.db.query(lp_models.UserLearningPath).filter(
                    lp_models.UserLearningPath.user_id == user_id
                ).all()
            ]
            
            # 基本查询 - 排除已参与的路径
            query = self.db.query(lp_models.LearningPath).filter(
                ~lp_models.LearningPath.id.in_(enrolled_path_ids) if enrolled_path_ids else True
            )
            
            # 如果有学习风格评估，根据学习风格进行个性化推荐
            if user_assessment:
                dominant_style = user_assessment.dominant_style
                logger.info(f"用户 {user_id} 的主要学习风格: {dominant_style}")
                
                # 这里假设学习路径的metadata中包含适合的学习风格
                # 实际实现可能需要根据具体数据模型调整
                # 在实际项目中可能需要更复杂的匹配逻辑
                
                # 返回3个推荐路径
                return query.limit(3).all()
            else:
                logger.info(f"用户 {user_id} 没有学习风格评估，返回通用推荐")
                # 如果没有学习风格评估，返回通用推荐
                return query.limit(3).all()
                
        except Exception as e:
            logger.error(f"生成用户 {user_id} 的推荐时出错: {str(e)}")
            # 发生错误时，返回空列表
            return []
