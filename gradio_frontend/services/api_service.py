import requests
import json
import logging
from typing import Dict, List, Any, Optional, Union

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_service")

class ApiService:
    """与后端API通信的服务类"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        
    def _request(self, method: str, endpoint: str, data=None, params=None, endpoint_prefix=""):
        """通用请求方法"""
        # 添加endpoint_prefix参数，允许指定前缀（如空字符串用于基础URL）
        base = self.base_url if not endpoint_prefix else endpoint_prefix.rstrip("/")
        url = f"{base}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        
        # 记录请求信息
        logger.info(f"API请求: {method} {url}")
        if params:
            logger.info(f"请求参数: {params}")
        if data:
            logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False)[:100]}...")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # 记录响应信息
            logger.info(f"API响应状态码: {response.status_code}")
            
            # 检查错误并提供更详细的日志
            if response.status_code >= 400:
                error_msg = f"{response.status_code} {response.reason} for url: {url}"
                if response.status_code == 422:
                    error_detail = response.json() if response.content else "No detail"
                    logger.error(f"参数验证错误: {error_msg}\n详情: {error_detail}")
                    return {"error": f"参数验证错误: {error_msg}", "detail": error_detail}
                elif response.status_code == 500:
                    logger.error(f"服务器内部错误: {error_msg}")
                    return {"error": f"服务器内部错误: {error_msg}"}
                else:
                    logger.error(f"API请求错误: {error_msg}")
                    return {"error": f"API请求错误: {error_msg}"}
            
            # 尝试解析JSON响应
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"无法解析JSON响应: {response.text[:100]}...")
                return {"error": "无法解析API响应"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
            return {"error": f"API请求异常: {str(e)}"}
        except Exception as e:
            logger.error(f"未预期的错误: {str(e)}")
            return {"error": f"未预期的错误: {str(e)}"}
    
    # 学习风格评估相关方法
    def get_assessment_questions(self):
        """获取学习风格评估问题"""
        result = self._request("GET", "/assessment/questions")
        if "error" in result:
            # 发生错误时返回一些测试问题
            logger.warning("获取评估问题失败，使用测试数据")
            return self._get_test_assessment_questions()
        return result
    
    def submit_assessment(self, user_id: int, responses: List[Dict[str, Any]]):
        """提交学习风格评估回答"""
        data = {
            "user_id": user_id,
            "responses": responses
        }
        result = self._request("POST", "/assessment/submit", data=data)
        if "error" in result:
            # 发生错误时返回测试结果
            logger.warning("提交评估回答失败，使用测试数据")
            return self._get_test_assessment_result()
        return result
    
    def get_learning_progress(self, user_id: int):
        """获取用户学习进度"""
        result = self._request("GET", f"/assessment/progress/{user_id}")
        # 特殊处理404错误，这是预期的情况 - 用户还没有评估记录
        if "error" in result and "404" in result["error"]:
            logger.info("用户没有评估记录，使用空数据")
            return self._get_empty_learning_progress()
        elif "error" in result:
            logger.warning("获取学习进度失败，使用测试数据")
            return self._get_test_learning_progress()
        return result
    
    # 学习路径相关方法
    def get_enrolled_paths(self, user_id: int):
        """获取用户已注册的学习路径"""
        # 根据test_full_flow.py的调用方式，实际应该使用过滤后的学习路径端点
        result = self._request("GET", "/learning-paths", params={"user_id": user_id, "enrolled": "true"})
        if "error" in result:
            logger.warning("获取已注册路径失败，使用测试数据")
            return self._get_test_enrolled_paths()
        return result
    
    def get_recommended_paths(self, user_id: int):
        """获取推荐给用户的学习路径"""
        # 根据test_full_flow.py的调用方式，实际应该使用过滤后的学习路径端点
        result = self._request("GET", "/learning-paths", params={"user_id": user_id, "recommended": "true"})
        if "error" in result:
            logger.warning("获取推荐路径失败，使用测试数据")
            return self._get_test_recommended_paths()
        return result
    
    def get_path_details(self, path_id: int, user_id: Optional[int] = None):
        """获取学习路径详情"""
        # 根据test_full_flow.py的调用方式
        params = {"user_id": user_id} if user_id else {}
        result = self._request("GET", f"/learning-paths/{path_id}", params=params)
        if "error" in result:
            logger.warning(f"获取路径详情失败 (ID: {path_id})，使用测试数据")
            return self._get_test_path_details(path_id)
        return result
    
    def enroll_in_path(self, user_id: int, path_id: int):
        """注册学习路径"""
        # 根据test_full_flow.py的调用方式
        data = {
            "user_id": user_id,
            "path_id": path_id,
            "personalization_settings": {
                "preferred_content_types": ["video", "interactive"],
                "study_reminder": True
            }
        }
        return self._request("POST", "/learning-paths/enroll", data=data)
    
    def update_path_progress(self, path_id: int, user_id: int, content_id: int, progress: float):
        """更新学习路径进度"""
        # 根据test_full_flow.py的调用方式
        data = {
            "content_id": content_id,
            "progress": progress
        }
        return self._request("POST", f"/learning-paths/{path_id}/progress", data=data, params={"user_id": user_id})
    
    def update_learning_progress(self, path_id: int, user_id: int, content_id: int, progress: float) -> Dict:
        """更新学习进度
        
        这个方法是为了与content_viewer.py中的调用保持一致
        """
        return self.update_path_progress(path_id, user_id, content_id, progress)
    
    # 内容相关方法
    def get_content(self, content_id: int):
        """获取学习内容"""
        result = self._request("GET", f"/content/{content_id}")
        if "error" in result:
            logger.warning(f"获取内容失败 (ID: {content_id})，使用测试数据")
            return self._get_test_content(content_id)
        return result
    
    # 分析相关方法
    def analyze_learning_behavior(self, user_id: int, content_interactions: List[Dict[str, Any]]):
        """分析学习行为"""
        data = {
            "user_id": user_id,
            "content_interactions": content_interactions
        }
        return self._request("POST", "/analytics/behavior", data=data)
    
    def get_weaknesses(self, user_id: int):
        """获取用户学习弱点分析"""
        return self._request("GET", f"/analytics/weaknesses/{user_id}")
    
    # 测试和诊断方法
    def diagnose_api(self):
        """诊断API可用性"""
        endpoints = [
            ("GET", "/health", None, None, "健康检查"),
            ("GET", "/", None, None, "API根"),
            ("GET", "/api/v1/assessment/questions", None, None, "评估问题"),
            ("GET", "/api/v1/content", None, None, "内容列表"),
            # 更新为正确的端点格式，匹配test_full_flow.py
            ("GET", "/api/v1/learning-paths", {"user_id": 1, "enrolled": "true"}, None, "已注册路径"),
            ("GET", "/api/v1/learning-paths", {"user_id": 1, "recommended": "true"}, None, "推荐路径"),
            ("GET", "/api/v1/learning-paths/1", {"user_id": 1}, None, "路径详情")
        ]
        
        results = {}
        base_url = self.base_url.rsplit('/api/v1', 1)[0]
        
        for method, endpoint, params, data, name in endpoints:
            full_url = f"{base_url}{endpoint}" if not endpoint.startswith('/api') else f"{base_url.rsplit('/api', 1)[0]}{endpoint}"
            
            try:
                if method == "GET":
                    response = requests.get(full_url, params=params)
                else:
                    response = requests.post(full_url, json=data, params=params)
                
                status_ok = response.status_code < 400
                results[name] = {
                    "url": full_url,
                    "status": response.status_code,
                    "ok": status_ok,
                    "response": response.json() if status_ok and response.content else None,
                }
            except Exception as e:
                results[name] = {
                    "url": full_url,
                    "status": 0,
                    "ok": False,
                    "error": str(e)
                }
                
        return results
    
    # 测试数据方法 - 当API不可用时使用
    def _get_test_assessment_questions(self):
        """返回测试评估问题"""
        return [
            {
                "id": 1,
                "question_text": "我喜欢通过观看视频或图像来学习新知识",
                "category": "visual",
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 2,
                "question_text": "我喜欢听讲座或讨论来学习新概念",
                "category": "auditory",
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 3,
                "question_text": "我通过实践和动手操作学得最好",
                "category": "kinesthetic",
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 4,
                "question_text": "我喜欢阅读文章和书籍来获取信息",
                "category": "reading",
                "options": ["1", "2", "3", "4", "5"]
            }
        ]
    
    def _get_test_assessment_result(self):
        """返回测试评估结果"""
        return {
            "learning_style_result": {
                "visual_score": 75.0,
                "auditory_score": 60.0,
                "kinesthetic_score": 50.0,
                "reading_score": 65.0,
                "dominant_style": "visual",
                "secondary_style": "reading"
            },
            "recommendations": [
                {
                    "title": "Python基础编程",
                    "description": "通过可视化示例学习Python编程基础",
                    "match_score": 0.85
                },
                {
                    "title": "数据结构与算法",
                    "description": "包含丰富视觉图表的数据结构课程",
                    "match_score": 0.78
                }
            ]
        }
    
    def _get_test_learning_progress(self):
        """返回测试学习进度数据"""
        return {
            "current_learning_style": {
                "visual": 75,
                "auditory": 60,
                "kinesthetic": 50,
                "reading": 65
            },
            "progress_metrics": {
                "completed_paths": 2,
                "in_progress_paths": 1,
                "total_learning_time": 18.5,
                "average_completion_rate": 85.0
            },
            "improvement_suggestions": [
                "尝试更多交互式学习内容以提高动觉学习能力",
                "参与小组讨论以加强听觉学习效果"
            ]
        }
    
    def _get_empty_learning_progress(self):
        """返回空的学习进度数据（用于新用户）"""
        return {
            "current_learning_style": {
                "visual": 0,
                "auditory": 0,
                "kinesthetic": 0,
                "reading": 0
            },
            "progress_metrics": {
                "completed_paths": 0,
                "in_progress_paths": 0,
                "total_learning_time": 0,
                "average_completion_rate": 0
            },
            "improvement_suggestions": [
                "完成学习风格评估以获取个性化建议",
                "浏览推荐的学习路径"
            ]
        }
    
    def _get_test_enrolled_paths(self):
        """返回测试已注册路径"""
        return [
            {
                "id": 1,
                "title": "Python编程基础",
                "description": "从零开始学习Python编程语言",
                "subject": "programming",
                "difficulty_level": 2,
                "estimated_hours": 25,
                "progress": 75.0
            },
            {
                "id": 2,
                "title": "Web开发入门",
                "description": "HTML, CSS和JavaScript基础",
                "subject": "web_development",
                "difficulty_level": 3,
                "estimated_hours": 30,
                "progress": 45.0
            }
        ]
    
    def _get_test_recommended_paths(self):
        """返回测试推荐路径"""
        return [
            {
                "id": 3,
                "title": "数据科学基础",
                "description": "学习数据分析和可视化基础知识",
                "subject": "data_science",
                "difficulty_level": 3,
                "estimated_hours": 40,
                "match_score": 0.89
            },
            {
                "id": 4,
                "title": "机器学习入门",
                "description": "了解机器学习的基本原理和应用",
                "subject": "machine_learning",
                "difficulty_level": 4,
                "estimated_hours": 50,
                "match_score": 0.82
            }
        ]
    
    def _get_test_path_details(self, path_id: int):
        """返回测试路径详情"""
        title = "测试学习路径"
        subject = "test_subject"
        description = "这是一个测试学习路径"
        
        if path_id == 1:
            title = "Python编程基础"
            subject = "programming"
            description = "从零开始学习Python编程语言"
        elif path_id == 2:
            title = "Web开发入门"
            subject = "web_development"
            description = "HTML, CSS和JavaScript基础"
        
        return {
            "id": path_id,
            "title": title,
            "description": description,
            "subject": subject,
            "difficulty_level": 3,
            "estimated_hours": 30,
            "contents": [
                {
                    "id": path_id * 10 + 1,
                    "title": f"内容 1: {title}简介",
                    "description": "入门基础知识介绍",
                    "content_type": "video",
                    "difficulty_level": 1
                },
                {
                    "id": path_id * 10 + 2,
                    "title": f"内容 2: {subject}核心概念",
                    "description": "深入理解核心概念和原理",
                    "content_type": "article",
                    "difficulty_level": 2
                },
                {
                    "id": path_id * 10 + 3,
                    "title": f"内容 3: {title}实践练习",
                    "description": "动手操作巩固所学知识",
                    "content_type": "interactive",
                    "difficulty_level": 3
                }
            ],
            "user_progress": {
                "overall_progress": 50.0,
                "content_progress": {
                    str(path_id * 10 + 1): 100.0,
                    str(path_id * 10 + 2): 50.0,
                    str(path_id * 10 + 3): 0.0
                }
            }
        }
    
    def _get_test_content(self, content_id: int):
        """返回测试内容数据"""
        content_type = "video"
        if content_id % 3 == 0:
            content_type = "interactive"
        elif content_id % 3 == 1:
            content_type = "article"
        
        content_data = {}
        if content_type == "video":
            content_data = {
                "url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "duration": 3600
            }
        elif content_type == "article":
            content_data = {
                "content": "<h2>学习内容示例</h2><p>这是一篇测试文章的内容。这里会包含学习相关的文本。</p><p>实际内容将由后端API提供。</p>"
            }
        elif content_type == "interactive":
            content_data = {
                "exercises": 5
            }
        
        return {
            "id": content_id,
            "title": f"测试内容 {content_id}",
            "description": f"这是内容 ID {content_id} 的描述",
            "content_type": content_type,
            "subject": "test_subject",
            "difficulty_level": content_id % 5 + 1,
            "content_data": content_data
        }
