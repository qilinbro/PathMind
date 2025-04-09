from typing import Dict, List, Any, Optional
import json
import asyncio
from zhipuai import ZhipuAI
from app.core.config import settings
import logging
import traceback
import time
import functools
import re

# 设置日志
logger = logging.getLogger(__name__)

class AIService:
    """处理AI相关功能的服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ZHIPUAI_API_KEY
        self.model = settings.ZHIPUAI_MODEL
        self.timeout = settings.ZHIPUAI_TIMEOUT
        
        logger.info("初始化智谱AI服务...")
        logger.info(f"使用模型: {self.model}")
        logger.info(f"超时设置: {self.timeout}秒")
        logger.debug(f"API密钥: {self.api_key[:8]}..." if self.api_key else "API密钥未配置")
        
        if not self.api_key:
            logger.error("ZHIPUAI_API_KEY未配置")
            raise ValueError("ZHIPUAI_API_KEY未配置")
            
        try:
            self.client = ZhipuAI(api_key=self.api_key)
            logger.info("智谱AI客户端初始化成功")
        except Exception as e:
            logger.error(f"智谱AI客户端初始化失败: {str(e)}")
            raise
            
    def _extract_json(self, text: str, request_id: str) -> Optional[str]:
        """从文本中提取JSON"""
        # 首先尝试整个文本是否为JSON
        text = text.strip()
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            logger.debug(f"[{request_id}] 完整文本不是有效JSON，尝试提取...")
        
        # 尝试使用正则表达式提取JSON部分
        patterns = [
            r'```json\s*(.*?)\s*```',  # Markdown JSON代码块
            r'```\s*(.*?)\s*```',      # 任何代码块
            r'\{.*\}',                 # 花括号包围的内容
            r'\[.*\]'                  # 方括号包围的内容
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    content = match.strip()
                    json.loads(content)  # 验证是否为有效JSON
                    logger.info(f"[{request_id}] 成功提取JSON")
                    return content
                except json.JSONDecodeError:
                    continue
        
        return None
        
    async def _call_ai_api(self, prompt: str, model: Optional[str] = None) -> str:
        """调用智谱AI API的通用方法"""
        start_time = time.time()
        request_id = int(time.time() * 1000)
        
        try:
            logger.info(f"[{request_id}] 开始调用智谱AI API...")
            logger.info(f"[{request_id}] 模型: {model or self.model}")
            logger.debug(f"[{request_id}] 提示词: {prompt[:200]}...")
            
            try:
                # 异步调用API
                fn = functools.partial(
                    self.client.chat.completions.create,
                    model=model or self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Please respond in JSON format only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(fn),
                    timeout=self.timeout
                )
                
                # 计算耗时
                elapsed_time = time.time() - start_time
                raw_text = response.choices[0].message.content.strip()
                logger.info(f"[{request_id}] 智谱AI调用成功")
                logger.info(f"[{request_id}] 耗时: {elapsed_time:.2f}秒")
                logger.info(f"[{request_id}] 响应长度: {len(raw_text)}")
                logger.debug(f"[{request_id}] 原始响应:\n{raw_text[:500]}...")
                
                # 尝试从响应中提取JSON
                result_text = self._extract_json(raw_text, request_id)
                if result_text:
                    return result_text
                    
                # 如果无法提取JSON，返回原始响应
                logger.warning(f"[{request_id}] 无法提取JSON，返回原始响应")
                return raw_text
                
            except asyncio.TimeoutError as e:
                elapsed_time = time.time() - start_time
                logger.error(f"[{request_id}] 智谱AI API调用超时 ({self.timeout}秒)")
                logger.error(f"[{request_id}] 耗时: {elapsed_time:.2f}秒")
                logger.error(f"[{request_id}] 提示词长度: {len(prompt)}")
                raise
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"[{request_id}] 智谱AI API调用失败: {str(e)}")
            logger.error(f"[{request_id}] 错误类型: {type(e).__name__}")
            logger.error(f"[{request_id}] 耗时: {elapsed_time:.2f}秒")
            logger.error(f"[{request_id}] 提示词长度: {len(prompt)}")
            logger.error(f"[{request_id}] 完整错误追踪:\n{traceback.format_exc()}")
            raise
            
    async def analyze_learning_style(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析用户的学习风格偏好"""
        logger.info(f"开始分析学习风格，输入数据量: {len(responses)}")
        
        prompt = f"""
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
            
        result_text = await self._call_ai_api(prompt)
        result = json.loads(result_text)
        logger.info(f"学习风格分析完成，主导风格: {result.get('dominant_style', 'unknown')}")
        return result
    
    async def generate_learning_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户学习数据并提供见解"""
        logger.info(f"开始生成学习分析，用户数据: {json.dumps(user_data, ensure_ascii=False)}")
        
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
        
        result_text = await self._call_ai_api(prompt, model="glm-4")
        result = json.loads(result_text)
        logger.info("学习分析生成完成")
        return result
    
    async def generate_content_recommendations(
        self, user_id: int, subject: str = None, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """生成内容推荐"""
        logger.info(f"开始生成内容推荐: user_id={user_id}, subject={subject}, limit={limit}")
        
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
        
        result_text = await self._call_ai_api(prompt)
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
        
        logger.info(f"内容推荐生成完成: {len(formatted_recommendations)}条推荐")
        return formatted_recommendations
    
    async def generate_adaptive_test(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成自适应测试，根据用户特点调整难度"""
        logger.info(f"开始生成自适应测试: {json.dumps(user_data, ensure_ascii=False)}")
        
        # 如果明确设置了使用模拟数据，直接返回
        if hasattr(settings, 'USE_MOCK_DATA') and settings.USE_MOCK_DATA:
            raise ValueError("系统配置为使用模拟数据，但AIService已不再支持mock")
        
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
        
        result_text = await self._call_ai_api(prompt)
        
        try:
            result = json.loads(result_text)
            # 验证结果结构
            if not isinstance(result, dict) or "questions" not in result:
                logger.error("AI返回的JSON格式有效，但缺少questions字段")
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
                raise ValueError("AI返回的数据结构不正确")
                
            logger.info(f"自适应测试生成完成: {len(result.get('questions', []))}个问题")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"解析AI返回的JSON失败: {e}")
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
                                logger.info("成功从AI回答中提取JSON")
                                return extracted_json
                        except:
                            continue
            raise ValueError("无法从AI回答中提取有效的JSON")
