from typing import Dict, List, Any, Optional
from app.models.learning_assessment import LearningStyleAssessment

class AssessmentService:
    """处理学习评估相关功能的服务类"""
    
    @staticmethod
    def analyze_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析用户评估回答，计算学习风格得分"""
        # 初始化各学习风格分数
        scores = {
            "visual": 0,
            "auditory": 0,
            "kinesthetic": 0,
            "reading": 0
        }
        
        # 各类别问题计数
        counts = {
            "visual": 0,
            "auditory": 0,
            "kinesthetic": 0,
            "reading": 0
        }
        
        # 计算每种学习风格的总分
        for response in responses:
            category = response.get("category", "unknown")
            if category in scores:
                # 假设每个问题的回答是1-5的数值
                response_value = response.get("response_value", {}).get("answer", 0)
                try:
                    value = int(response_value)
                    scores[category] += value
                    counts[category] += 1
                except (ValueError, TypeError):
                    pass
        
        # 计算每种学习风格的平均分数并转换为0-100的范围
        for category in scores:
            if counts[category] > 0:
                # 将1-5的范围转换为0-100
                scores[category] = (scores[category] / counts[category]) * 20
            else:
                scores[category] = 0
        
        # 确定主导学习风格
        dominant_style = max(scores, key=scores.get)
        
        # 找出次要学习风格
        scores_without_dominant = {k: v for k, v in scores.items() if k != dominant_style}
        secondary_style = max(scores_without_dominant, key=scores_without_dominant.get) if scores_without_dominant else None
        
        return {
            "visual_score": scores["visual"],
            "auditory_score": scores["auditory"],
            "kinesthetic_score": scores["kinesthetic"],
            "reading_score": scores["reading"],
            "dominant_style": dominant_style,
            "secondary_style": secondary_style,
            "style_scores": scores
        }
    
    @staticmethod
    def generate_recommendations(learning_style: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于学习风格生成内容推荐"""
        dominant_style = learning_style.get("dominant_style")
        
        recommendations = []
        
        if dominant_style == "visual":
            recommendations = [
                {
                    "content_type": "video",
                    "title": "图解编程基础",
                    "description": "通过可视化图表和动画学习编程基础",
                    "match_score": 0.92
                },
                {
                    "content_type": "interactive",
                    "title": "可视化算法演示",
                    "description": "交互式算法可视化工具",
                    "match_score": 0.88
                }
            ]
        elif dominant_style == "auditory":
            recommendations = [
                {
                    "content_type": "audio",
                    "title": "编程概念播客",
                    "description": "通过讨论和对话学习编程概念",
                    "match_score": 0.90
                },
                {
                    "content_type": "video",
                    "title": "编程讲座系列",
                    "description": "详细讲解编程概念的视频讲座",
                    "match_score": 0.85
                }
            ]
        elif dominant_style == "kinesthetic":
            recommendations = [
                {
                    "content_type": "interactive",
                    "title": "动手编程实验室",
                    "description": "通过实际操作学习编程",
                    "match_score": 0.94
                },
                {
                    "content_type": "exercise",
                    "title": "编程挑战集",
                    "description": "解决实际编程问题的练习",
                    "match_score": 0.89
                }
            ]
        else:  # reading
            recommendations = [
                {
                    "content_type": "article",
                    "title": "编程概念详解",
                    "description": "深入解释编程概念的文章集",
                    "match_score": 0.91
                },
                {
                    "content_type": "tutorial",
                    "title": "深入理解数据结构",
                    "description": "文本教程和示例代码",
                    "match_score": 0.87
                }
            ]
        
        return recommendations
    
    @staticmethod
    def calculate_progress_metrics(
        latest_assessment: LearningStyleAssessment,
        previous_assessments: List[LearningStyleAssessment]
    ) -> Dict[str, Any]:
        """计算学习进度指标"""
        
        # 如果没有历史评估，只返回当前状态
        if not previous_assessments:
            return {
                "current_stats": {
                    "visual": latest_assessment.visual_score,
                    "auditory": latest_assessment.auditory_score,
                    "kinesthetic": latest_assessment.kinesthetic_score, 
                    "reading": latest_assessment.reading_score
                },
                "trend": "初次评估",
                "improvement_areas": []
            }
        
        # 计算各维度变化
        last_assessment = previous_assessments[0]
        
        changes = {
            "visual": latest_assessment.visual_score - last_assessment.visual_score,
            "auditory": latest_assessment.auditory_score - last_assessment.auditory_score,
            "kinesthetic": latest_assessment.kinesthetic_score - last_assessment.kinesthetic_score,
            "reading": latest_assessment.reading_score - last_assessment.reading_score
        }
        
        # 确定进步和需要改进的领域
        improvements = []
        decline_areas = []
        
        for style, change in changes.items():
            if change >= 5:
                improvements.append(style)
            elif change <= -5:
                decline_areas.append(style)
        
        # 确定整体趋势
        overall_change = sum(changes.values())
        if overall_change > 10:
            trend = "显著进步"
        elif overall_change > 0:
            trend = "稳步提升"
        elif overall_change == 0:
            trend = "保持稳定"
        elif overall_change > -10:
            trend = "轻微下降"
        else:
            trend = "需要关注"
        
        return {
            "current_stats": {
                "visual": latest_assessment.visual_score,
                "auditory": latest_assessment.auditory_score,
                "kinesthetic": latest_assessment.kinesthetic_score,
                "reading": latest_assessment.reading_score
            },
            "changes": changes,
            "trend": trend,
            "improved_areas": improvements,
            "declined_areas": decline_areas
        }
    
    @staticmethod
    def generate_improvement_suggestions(assessment_results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        # 添加安全检查，确保assessment_results不为None
        if not assessment_results:
            return ["完成更多练习以获取个性化建议", "尝试不同类型的学习资料"]
            
        # 从字典中安全获取dominant_style，如果不存在则使用默认值
        dominant_style = assessment_results.get("dominant_style", "")
        suggestions = []
        
        if dominant_style == "visual":
            suggestions = [
                "使用图表、图像和视频来增强学习",
                "为复杂概念创建思维导图",
                "使用颜色标记重要信息",
                "寻找包含丰富视觉元素的学习材料"
            ]
        elif dominant_style == "auditory":
            suggestions = [
                "录制自己朗读笔记并回放",
                "参加讨论组和研讨会",
                "使用有声书和播客学习",
                "向他人解释所学内容以加深理解"
            ]
        elif dominant_style == "kinesthetic":
            suggestions = [
                "通过实际操作学习新概念",
                "使用动手项目来应用理论知识",
                "学习时适当活动以保持注意力",
                "建立与现实世界的联系以理解抽象概念"
            ]
        elif dominant_style == "reading":
            suggestions = [
                "创建详细的书面笔记",
                "阅读丰富的文本资料",
                "使用列表和大纲组织信息",
                "定期回顾并重写笔记以加深理解"
            ]
        else:
            # 如果没有明确的学习风格，提供通用建议
            suggestions = [
                "尝试不同的学习方法，找出最适合你的方式",
                "组合使用视觉、听觉和动手材料",
                "定期回顾学习内容加深理解",
                "在实际项目中应用所学知识"
            ]
        
        # 添加通用建议
        general_suggestions = [
            "定期评估学习风格，确认其随时间的变化",
            "尝试结合不同学习方法，增强学习效果",
            "为学习设定具体目标和时间表"
        ]
        
        return suggestions + general_suggestions