from typing import Dict, List, Any, Optional
import json
import asyncio
from zhipuai import ZhipuAI
from app.core.config import settings

class AIService:
    """处理AI相关功能的服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ZHIPU_API_KEY
        self.client = ZhipuAI(api_key=self.api_key) if self.api_key else None
        
    async def analyze_learning_style(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析用户的学习风格偏好"""
        if not self.client:
            # 如果API密钥未配置，使用模拟数据
            return self._mock_learning_style_analysis()
        
        # 在实际应用中，使用智谱AI API进行分析
        try:
            prompt = self._create_learning_style_prompt(responses)
            
            # 使用异步API调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="glm-4-plus", 
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析返回结果
            result_text = response.choices[0].message.content
            return json.loads(result_text)
        except Exception as e:
            print(f"AI学习风格分析错误: {str(e)}")
            # 如有异常，使用模拟数据
            return self._mock_learning_style_analysis()
    
    async def generate_learning_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户学习数据并提供见解"""
        if not self.client:
            return {"error": "API未配置", "status": "使用模拟数据"}
        
        try:
            prompt = f"""
            我有一个学生的学习行为数据，请分析并提供见解:
            
            学习时间: {user_data.get('study_time', '未知')}分钟
            内容完成率: {user_data.get('completion_rate', '未知')}%
            互动次数: {user_data.get('interactions', '未知')}次
            主要内容类型: {user_data.get('content_types', ['未知'])}
            
            请提供以下分析:
            1. 学习模式和习惯
            2. 优势和待改进的方面
            3. 提高学习效率的建议
            4. 适合该学习者的内容类型推荐
            
            以JSON格式返回，包含以下字段:
            - behavior_patterns: 行为模式对象
            - strengths: 优势列表
            - weaknesses: 弱点列表
            - recommendations: 建议列表
            - optimal_content_types: 最适合的内容类型列表
            """
            
            # 使用异步API调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="glm-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析返回结果
            result_text = response.choices[0].message.content
            return json.loads(result_text)
        except Exception as e:
            print(f"学习分析生成错误: {str(e)}")
            return {
                "behavior_patterns": {"study_consistency": "不规律", "focus_level": "中等"},
                "strengths": ["专注于完成任务", "善于互动学习"],
                "weaknesses": ["学习时间不足", "缺乏规律性"],
                "recommendations": ["建立固定学习时间", "增加每次学习的时长"],
                "optimal_content_types": ["视频教程", "互动练习"]
            }
    
    def _create_learning_style_prompt(self, responses: List[Dict[str, Any]]) -> str:
        """创建用于分析学习风格的提示词"""
        return f"""
        基于以下用户的评估回答，分析他们的学习风格偏好。回答应包含视觉、听觉、动觉和阅读方面的得分，
        以及最适合该用户的学习方式。请将回答格式化为JSON。
        
        用户回答:
        {json.dumps(responses, ensure_ascii=False)}
        
        请以JSON格式返回分析结果，包含以下字段:
        - visual_score: 视觉学习得分(0-100)
        - auditory_score: 听觉学习得分(0-100)
        - kinesthetic_score: 动觉学习得分(0-100)
        - reading_score: 阅读学习得分(0-100)
        - dominant_style: 主导学习风格
        """
    
    def _mock_learning_style_analysis(self) -> Dict[str, Any]:
        """提供模拟的学习风格分析结果"""
        return {
            "visual_score": 75,
            "auditory_score": 60,
            "kinesthetic_score": 45,
            "reading_score": 65,
            "dominant_style": "visual"
        }
    
    async def generate_content_recommendations(
        self, user_id: int, subject: str = None, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """生成内容推荐"""
        if not self.client:
            # 返回模拟推荐
            return self._mock_content_recommendations(limit)
            
        try:
            prompt = f"""
            为用户ID {user_id} 生成{limit}条学习内容推荐。
            {f"学科领域: {subject}" if subject else ""}
            
            推荐应该包括:
            - 内容ID
            - 标题
            - 类型
            - 匹配度评分
            - 推荐理由
            - 学习建议
            
            以JSON数组格式返回。
            """
            
            # 使用异步API调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析返回结果
            result_text = response.choices[0].message.content
            recommendations = json.loads(result_text)
            
            # 确保结果格式正确
            formatted_recommendations = []
            for rec in recommendations[:limit]:
                formatted_recommendations.append({
                    "content": {
                        "id": rec.get("id", 100 + len(formatted_recommendations)),
                        "title": rec.get("title", "推荐内容"),
                        "type": rec.get("type", "interactive"),
                        "match_score": rec.get("match_score", 0.8)
                    },
                    "explanation": rec.get("explanation", "此内容适合您的学习风格"),
                    "approach_suggestion": rec.get("approach_suggestion", "建议仔细学习并做笔记")
                })
            
            return formatted_recommendations
        except Exception as e:
            print(f"内容推荐生成错误: {str(e)}")
            return self._mock_content_recommendations(limit)
            
    def _mock_content_recommendations(self, limit: int = 3) -> List[Dict[str, Any]]:
        """提供模拟的内容推荐"""
        recommendations = [
            {
                "content": {
                    "id": 101,
                    "title": "视觉编程入门",
                    "type": "interactive",
                    "match_score": 0.92
                },
                "explanation": "这个互动编程教程使用大量视觉元素，非常适合您的视觉学习偏好。",
                "approach_suggestion": "尝试完成所有视觉练习，并创建自己的流程图来巩固所学知识。"
            },
            {
                "content": {
                    "id": 102,
                    "title": "算法可视化",
                    "type": "video",
                    "match_score": 0.87
                },
                "explanation": "这个视频课程通过动画展示算法工作原理，适合您的视觉学习风格。",
                "approach_suggestion": "观看视频时尝试在纸上跟随绘制算法流程，加深理解。"
            },
            {
                "content": {
                    "id": 103,
                    "title": "数据结构实战",
                    "type": "exercise",
                    "match_score": 0.85
                },
                "explanation": "这套练习题包含丰富的图表和视觉辅助，帮助您更好地理解数据结构。",
                "approach_suggestion": "先理解视觉图表，再尝试独立解决问题，最后核对答案。"
            }
        ]
        
        return recommendations[:limit]
    
    async def identify_weaknesses(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """识别用户的学习弱点和优势，提供改进计划"""
        if not self.client:
            return self._mock_weakness_analysis()
        
        try:
            # 创建用于分析弱点的提示词
            prompt = f"""
            分析以下学生的学习数据，识别他们的弱点和优势，并提供改进计划:
            
            用户ID: {user_data.get('user_id')}
            学习记录: {json.dumps(user_data.get('learning_records', []), ensure_ascii=False)}
            测验成绩: {json.dumps(user_data.get('quiz_scores', {}), ensure_ascii=False)}
            内容互动: {json.dumps(user_data.get('content_interactions', {}), ensure_ascii=False)}
            
            以JSON格式返回分析结果，格式如下:
            {{
                "weak_areas": [
                    {{
                        "topic": "主题名称",
                        "confidence_level": 0.XX,
                        "suggested_resources": [
                            {{"type": "资源类型", "title": "资源标题", "url": "资源链接"}}
                        ]
                    }}
                ],
                "strength_areas": [
                    {{"topic": "主题名称", "confidence_level": 0.XX}}
                ],
                "improvement_plan": {{
                    "short_term_goals": ["短期目标1", "短期目标2"],
                    "long_term_goals": ["长期目标1", "长期目标2"],
                    "recommended_study_path": "推荐学习路径描述"
                }}
            }}
            """
            
            # 使用智谱AI进行分析
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 处理返回结果
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
        except Exception as e:
            print(f"Weakness analysis error: {str(e)}")
            return self._mock_weakness_analysis()
    
    async def analyze_mistakes(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户的常见错误并提供改进建议"""
        if not self.client:
            return self._mock_mistake_analysis()
        
        try:
            # 创建用于分析错误的提示词
            prompt = f"""
            分析以下学生的错误数据，识别常见错误模式，并提供改进建议:
            
            用户ID: {user_data.get('user_id')}
            错误记录: {json.dumps(user_data.get('error_records', []), ensure_ascii=False)}
            测验答案: {json.dumps(user_data.get('quiz_answers', {}), ensure_ascii=False)}
            学习时间分布: {json.dumps(user_data.get('study_time_distribution', {}), ensure_ascii=False)}
            
            请提供:
            1. 常见错误类型和频率
            2. 错误模式的分析（时间相关、主题相关、难度相关）
            3. 改进计划和建议的学习材料
            
            以JSON格式返回分析结果，格式如下:
            {{
                "common_mistakes": [
                    {{
                        "topic": "错误主题",
                        "frequency": "频率描述",
                        "examples": ["示例1", "示例2"],
                        "remediation": "改进建议"
                    }}
                ],
                "mistake_patterns": {{
                    "time_of_day": "时间相关模式",
                    "subject_correlation": "主题相关模式",
                    "difficulty_correlation": "难度相关模式"
                }},
                "remediation_plan": {{
                    "focus_areas": ["重点领域1", "重点领域2"],
                    "suggested_exercises": ["建议练习1", "建议练习2"],
                    "learning_materials": ["学习材料1", "学习材料2"]
                }}
            }}
            """
            
            # 使用智谱AI进行分析
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 处理返回结果
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
        except Exception as e:
            print(f"Mistake analysis error: {str(e)}")
            return self._mock_mistake_analysis()
    
    def _mock_weakness_analysis(self) -> Dict[str, Any]:
        """提供模拟的弱点分析结果"""
        return {
            "weak_areas": [
                {
                    "topic": "数据结构",
                    "confidence_level": 0.35,
                    "suggested_resources": [
                        {"type": "video", "title": "Data Structures Fundamentals", "url": "https://example.com/ds101"},
                        {"type": "exercise", "title": "Data Structures Practice Problems", "url": "https://example.com/ds-practice"}
                    ]
                },
                {
                    "topic": "算法复杂度分析",
                    "confidence_level": 0.42,
                    "suggested_resources": [
                        {"type": "article", "title": "Introduction to Complexity Analysis", "url": "https://example.com/complexity-intro"},
                        {"type": "quiz", "title": "Algorithm Complexity Quiz", "url": "https://example.com/complexity-quiz"}
                    ]
                }
            ],
            "strength_areas": [
                {"topic": "编程基础", "confidence_level": 0.85},
                {"topic": "Web开发", "confidence_level": 0.78}
            ],
            "improvement_plan": {
                "short_term_goals": ["完成数据结构基础课程", "每周解决5道算法题"],
                "long_term_goals": ["掌握高级数据结构", "能够独立分析算法复杂度"],
                "recommended_study_path": "先巩固基础知识，再通过实践加深理解"
            }
        }
    
    def _mock_mistake_analysis(self) -> Dict[str, Any]:
        """提供模拟的错误分析结果"""
        return {
            "common_mistakes": [
                {
                    "topic": "Loop Control",
                    "frequency": "High",
                    "examples": ["Boundary condition errors", "Infinite loops"],
                    "remediation": "Review loop basics, focusing on boundary conditions"
                },
                {
                    "topic": "Variable Scope",
                    "frequency": "Medium",
                    "examples": ["Using undefined variables", "Scope confusion"],
                    "remediation": "Learn variable declaration and scope rules"
                }
            ],
            "mistake_patterns": {
                "time_of_day": "Higher error rates during evening study sessions",
                "subject_correlation": "Higher error rates in data structure problems",
                "difficulty_correlation": "Higher error rates in medium-to-hard difficulty problems"
            },
            "remediation_plan": {
                "focus_areas": ["循环控制", "变量作用域"],
                "suggested_exercises": ["边界条件测试编写", "作用域练习"],
                "learning_materials": ["《变量作用域详解》", "《循环控制进阶》"]
            }
        }
        
    async def generate_adaptive_test(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成自适应测试，根据用户特点调整难度"""
        if not self.client:
            # 如果API密钥未配置，直接返回模拟数据
            return self._mock_adaptive_test(user_data)
            
        try:
            # 记录请求参数以便调试
            print(f"开始为用户生成自适应测试: {json.dumps(user_data, ensure_ascii=False)}")
            
            # 如果明确设置了使用模拟数据，直接返回
            if hasattr(settings, 'USE_MOCK_DATA') and settings.USE_MOCK_DATA:
                return self._mock_adaptive_test(user_data)
                
            # 创建生成自适应测试的提示词
            prompt = f"""
            为以下用户创建一个自适应测试:
            
            用户ID: {user_data.get('user_id')}
            学科: {user_data.get('subject', '计算机科学')}
            主题: {user_data.get('topic', '编程基础')}
            初始难度: {user_data.get('difficulty', 'auto')}
            
            请创建一个包含5-8个问题的测试，包含选择题和简答题。每个问题应包含:
            1. 问题ID
            2. 问题内容
            3. 问题类型(choice或text)
            4. 选项列表(如果是选择题)
            5. 难度级别
            6. 涉及的主题
            
            返回JSON格式结果:
            {{
                "questions": [
                    {{
                        "id": 1,
                        "content": "问题内容",
                        "question_type": "choice",
                        "options": ["选项A", "选项B", "选项C", "选项D"],
                        "difficulty": "beginner",
                        "topic": "具体主题"
                    }}
                ],
                "adaptive_logic": {{
                    "initial_difficulty": "beginner",
                    "adjustment_rules": {{
                        "correct_answer": "增加难度",
                        "incorrect_answer": "降低难度"
                    }}
                }},
                "estimated_difficulty": "beginner",
                "topics_covered": ["主题1", "主题2"]
            }}
            
            务必确保返回的是有效的JSON格式。
            """
            
            # 使用更长的超时时间
            import asyncio
            try:
                # 使用带超时的异步API调用
                print(f"开始调用智谱AI API生成测试...")
                response_task = asyncio.create_task(asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="glm-4-plus",
                    messages=[{"role": "user", "content": prompt}]
                ))
                # 设置10秒超时(原5秒可能太短)
                response = await asyncio.wait_for(response_task, timeout=10.0)
                
                # 处理返回结果
                result_text = response.choices[0].message.content
                print(f"智谱AI返回原始结果: {result_text[:200]}...")
                
                # 确保JSON解析正确
                try:
                    result = json.loads(result_text)
                    # 验证结果结构
                    if not isinstance(result, dict) or "questions" not in result:
                        print("AI返回的JSON格式有效，但缺少questions字段")
                        # 尝试更智能地解析结果
                        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                            # 可能直接返回了问题列表
                            return {
                                "questions": result,
                                "adaptive_logic": {
                                    "initial_difficulty": user_data.get('difficulty', 'auto'),
                                    "adjustment_rules": {"correct_answer": "+0.1", "incorrect_answer": "-0.05"}
                                },
                                "estimated_difficulty": user_data.get('difficulty', 'auto')
                            }
                        return self._mock_adaptive_test(user_data)
                    return result
                except json.JSONDecodeError as e:
                    print(f"解析AI返回的JSON失败: {e}")
                    # 如果JSON解析失败，尝试提取JSON部分
                    import re
                    json_pattern = r'```json(.*?)```|```(.*?)```|\{.*\}'
                    matches = re.findall(json_pattern, result_text, re.DOTALL)
                    if matches:
                        for match in matches:
                            match_text = match[0] if match[0] else match[1]
                            if match_text:
                                try:
                                    extracted_json = json.loads(match_text.strip())
                                    if isinstance(extracted_json, dict) and "questions" in extracted_json:
                                        print("成功从AI回答中提取JSON")
                                        return extracted_json
                                except:
                                    continue
                    # 如果无法提取有效JSON，使用模拟数据
                    print("无法从AI回答中提取有效JSON，使用模拟数据")
                    return self._mock_adaptive_test(user_data)
            except asyncio.TimeoutError:
                print("AI服务超时，使用模拟数据")
                return self._mock_adaptive_test(user_data)
        except Exception as e:
            print(f"自适应测试生成错误: {str(e)}")
            # 出现任何错误都立即使用模拟数据
            return self._mock_adaptive_test(user_data)
    
    def _mock_adaptive_test(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """提供模拟的自适应测试"""
        # 确保使用用户指定的主题
        subject = user_data.get('subject', '计算机科学')
        topic = user_data.get('topic', '编程基础')
        difficulty = user_data.get('difficulty', 'auto')
        
        print(f"生成模拟测试数据: 主题={topic}, 难度={difficulty}")
        
        # 根据不同主题提供不同的问题集
        if "python" in topic.lower() or "编程" in topic:
            questions = [
                {
                    "id": 1,
                    "content": "在Python中，以下哪个函数用于获取列表的长度？",
                    "question_type": "choice",
                    "options": ["len()", "length()", "size()", "count()"],
                    "difficulty": "beginner",
                    "topic": "Python基础"
                },
                {
                    "id": 2,
                    "content": "以下哪个不是Python的基本数据类型？",
                    "question_type": "choice",
                    "options": ["array", "int", "float", "str"],
                    "difficulty": "beginner",
                    "topic": "Python数据类型"
                }
            ]
        elif "数据" in topic or "data" in topic.lower():
            questions = [
                {
                    "id": 1,
                    "content": "什么是数据规范化？",
                    "question_type": "text",
                    "difficulty": "intermediate",
                    "topic": "数据处理"
                },
                {
                    "id": 2,
                    "content": "以下哪个库最适合Python数据分析？",
                    "question_type": "choice",
                    "options": ["pandas", "flask", "django", "pygame"],
                    "difficulty": "beginner",
                    "topic": "数据分析工具"
                }
            ]
        else:
            questions = [
                {
                    "id": 1,
                    "content": f"关于{topic}，以下说法正确的是？",
                    "question_type": "choice",
                    "options": ["选项A - 正确描述", "选项B - 错误描述", "选项C - 不相关描述", "选项D - 部分正确描述"],
                    "difficulty": "auto",
                    "topic": topic
                },
                {
                    "id": 2,
                    "content": f"请简述{topic}的主要应用场景。",
                    "question_type": "text",
                    "difficulty": "auto",
                    "topic": topic
                }
            ]
        
        # 确保至少有3个问题
        while len(questions) < 3:
            new_id = len(questions) + 1
            questions.append({
                "id": new_id,
                "content": f"{topic}的问题{new_id}",
                "question_type": "choice",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "difficulty": difficulty,
                "topic": topic
            })
        
        # 添加一个文本题
        if not any(q["question_type"] == "text" for q in questions):
            questions.append({
                "id": len(questions) + 1,
                "content": f"请简要描述您对{topic}的理解。",
                "question_type": "text",
                "difficulty": difficulty,
                "topic": topic
            })
        
        return {
            "questions": questions,
            "adaptive_logic": {
                "initial_difficulty": difficulty,
                "adjustment_rules": {
                    "correct_answer": "增加难度",
                    "incorrect_answer": "降低难度",
                }
            },
            "estimated_difficulty": difficulty,
            "topics_covered": [topic, f"{topic}基础", f"{topic}应用"]
        }
