"""
API服务接口 - 封装所有与后端API交互的功能
"""
import requests
import json
import logging
import time
from functools import wraps
from typing import Dict, List, Any, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("api_service")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据 - 当API请求失败时使用
TEST_DATA = {
    "enrolled_paths": [
        {
            "id": 1,
            "title": "Python基础入门",
            "description": "学习Python编程的基础知识和核心概念",
            "image_url": "https://via.placeholder.com/150",
            "progress": 35,
            "level": "初级",
            "duration": "4周",
            "tags": ["编程", "Python", "基础"]
        },
        {
            "id": 2,
            "title": "数据分析基础",
            "description": "使用Python进行数据分析的入门课程",
            "image_url": "https://via.placeholder.com/150",
            "progress": 20,
            "level": "中级",
            "duration": "6周",
            "tags": ["数据分析", "Python", "统计"]
        }
    ],
    "recommended_paths": [
        {
            "id": 3,
            "title": "机器学习入门",
            "description": "了解机器学习基础概念和常见算法",
            "image_url": "https://via.placeholder.com/150",
            "level": "中级",
            "duration": "8周",
            "tags": ["机器学习", "人工智能", "数据科学"]
        },
        {
            "id": 4,
            "title": "Web开发基础",
            "description": "学习使用HTML、CSS和JavaScript构建网站",
            "image_url": "https://via.placeholder.com/150",
            "level": "初级",
            "duration": "5周",
            "tags": ["Web开发", "前端", "HTML", "CSS", "JavaScript"]
        }
    ],
    "learning_path_detail": {
        "id": 1,
        "title": "Python基础入门",
        "description": "全面学习Python编程的基础知识和核心概念",
        "image_url": "https://via.placeholder.com/300x150",
        "level": "初级",
        "duration": "4周",
        "tags": ["编程", "Python", "基础"],
        "modules": [
            {
                "id": 1,
                "title": "Python环境配置",
                "description": "安装Python并配置开发环境",
                "duration": "1小时",
                "completed": True
            },
            {
                "id": 2,
                "title": "Python基本语法",
                "description": "学习Python的基本语法规则和数据类型",
                "duration": "3小时",
                "completed": True
            },
            {
                "id": 3,
                "title": "控制流语句",
                "description": "学习条件语句和循环语句",
                "duration": "2小时",
                "completed": False
            }
        ]
    },
    "learning_progress": {
        "user_id": 1,
        "completed_paths": 2,
        "in_progress_paths": 3,
        "completed_modules": 15,
        "total_modules": 35,
        "recent_activity": [
            {
                "path_id": 1,
                "path_title": "Python基础入门",
                "module_id": 2,
                "module_title": "Python基本语法",
                "completed_at": "2023-09-15T10:30:00Z"
            },
            {
                "path_id": 2,
                "path_title": "数据分析基础",
                "module_id": 1,
                "module_title": "数据分析概述",
                "completed_at": "2023-09-14T14:45:00Z"
            }
        ]
    },
    "assessment_questions": [
        {
            "id": 1,
            "question": "您有多少年编程经验？",
            "options": ["无经验", "少于1年", "1-3年", "3-5年", "5年以上"],
            "type": "single_choice"
        },
        {
            "id": 2,
            "question": "您对哪些编程语言感兴趣？（可多选）",
            "options": ["Python", "JavaScript", "Java", "C++", "Go", "其他"],
            "type": "multiple_choice"
        },
        {
            "id": 3,
            "question": "您的学习目标是什么？",
            "options": ["找工作/转行", "提升技能", "个人项目", "学术研究", "兴趣爱好"],
            "type": "single_choice"
        }
    ]
}

def retry(max_retries=3, delay=1):
    """重试装饰器，用于API请求失败时自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"{func.__name__} 失败，已重试 {retries} 次: {e}")
                        raise
                    logger.warning(f"{func.__name__} 失败，正在重试 ({retries}/{max_retries}): {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

def make_api_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None):
    """发送API请求并处理结果"""
    # 确保endpoint不以斜杠结尾
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
        
    url = f"{BASE_URL}{endpoint}"
    logger.info(f"API请求: {method} {url}")
    
    if params:
        logger.info(f"请求参数: {params}")
    
    if json_data:
        logger.info(f"请求数据: {json_data}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, params=params, json=json_data, timeout=10)
        else:
            logger.error(f"不支持的HTTP方法: {method}")
            return None
        
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            if response.status_code >= 500:
                logger.error(f"服务器内部错误: {response.status_code} {response.reason} for url: {url}")
            else:
                logger.error(f"API请求错误: {response.status_code} {response.reason} for url: {url}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return None
    except Exception as e:
        logger.error(f"请求异常: {str(e)}")
        return None

@retry(max_retries=3)
def check_server_health() -> bool:
    """检查服务器健康状态"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True
        logger.error(f"服务器健康检查返回非200状态码: {response.status_code}")
        return False
    except Exception as e:
        logger.error(f"服务器健康检查失败: {str(e)}")
        return False

@retry(max_retries=3)
def get_enrolled_paths(user_id: int) -> List[Dict]:
    """获取用户已注册的学习路径"""
    # 直接使用POST方法，因为GET请求会返回405
    result = make_api_request("POST", "/learning-paths", json_data={"user_id": user_id, "enrolled": True})
    
    if result:
        return result
    
    # 如果API调用失败，尝试第二种格式
    result = make_api_request("GET", "/user-paths", params={"user_id": user_id, "status": "enrolled"})
    
    if result:
        return result
    
    logger.warning("获取已注册路径失败，使用测试数据")
    return TEST_DATA["enrolled_paths"]

@retry(max_retries=3)
def get_recommended_paths(user_id: int) -> List[Dict]:
    """获取推荐的学习路径"""
    # 直接使用POST方法，因为GET请求会返回405
    result = make_api_request("POST", "/learning-paths", json_data={"user_id": user_id, "recommended": True})
    
    if result:
        return result
    
    # 如果API调用失败，尝试第二种格式
    result = make_api_request("GET", "/user-paths", params={"user_id": user_id, "status": "recommended"})
    
    if result:
        return result
    
    logger.warning("获取推荐路径失败，使用测试数据")
    return TEST_DATA["recommended_paths"]

@retry(max_retries=3)
def get_path_details(path_id: int, user_id: int) -> Dict:
    """获取学习路径详情
    
    完全匹配测试文件的URL格式: /learning-paths/{path_id}?user_id={user_id}
    """
    try:
        # 直接构建完整URL，确保查询参数格式正确
        result = make_api_request("GET", f"/learning-paths/{path_id}", params={"user_id": user_id})
        
        if result:
            return result
        
        logger.warning(f"获取路径详情失败 (ID: {path_id})，使用测试数据")
    except Exception as e:
        logger.error(f"获取路径详情时发生异常: {str(e)}")
    
    return TEST_DATA["learning_path_detail"]

@retry(max_retries=3)
def update_learning_progress(path_id: int, user_id: int, content_id: int, progress: float) -> Dict:
    """更新学习进度
    
    完全匹配测试文件格式: /learning-paths/{path_id}/progress?user_id={user_id}
    """
    # 直接将user_id作为查询参数，其他数据放在JSON请求体中
    progress_data = {
        "content_id": content_id,
        "progress": progress  # 不添加百分号，保持为数字
    }
    
    try:
        result = make_api_request("POST", f"/learning-paths/{path_id}/progress", 
                                params={"user_id": user_id}, 
                                json_data=progress_data)
        if result:
            return result
    except Exception as e:
        logger.error(f"更新学习进度时发生异常: {str(e)}")
        
    return {"error": "更新进度失败，请稍后重试"}

@retry(max_retries=3)
def get_learning_progress(user_id: int) -> Dict:
    """获取用户学习进度"""
    # GET方法访问 /assessment/progress/{user_id} 端点 (表格项9)
    result = make_api_request("GET", f"/assessment/progress/{user_id}")
    
    if result:
        return result
    
    logger.warning("获取学习进度失败，使用测试数据")
    return TEST_DATA["learning_progress"]

@retry(max_retries=3)
def enroll_in_path(user_id: int, path_id: int) -> Dict:
    """注册学习路径"""
    # POST方法访问 /learning-paths/enroll 端点 (表格项4)
    enrollment_data = {
        "user_id": user_id,
        "path_id": path_id,
        "personalization_settings": {
            "preferred_content_types": ["video", "interactive"],
            "study_reminder": True
        }
    }
    
    result = make_api_request("POST", "/learning-paths/enroll", json_data=enrollment_data)
    if result:
        return result
    
    return {"error": "注册失败，请稍后重试"}

@retry(max_retries=3)
def submit_assessment(user_id: int, responses: List[Dict]) -> Dict:
    """提交学习风格评估"""
    # POST方法访问 /assessment/submit 端点 (表格项2)
    assessment_data = {
        "user_id": user_id,
        "responses": responses
    }
    
    result = make_api_request("POST", "/assessment/submit", json_data=assessment_data)
    if result:
        return result
    
    return {"error": "提交评估失败，请稍后重试"}

@retry(max_retries=3)
def analyze_learning_behavior(user_id: int, content_interactions: List[Dict]) -> Dict:
    """分析学习行为"""
    # POST方法访问 /analytics/behavior 端点 (表格项7)
    behavior_data = {
        "user_id": user_id,
        "content_interactions": content_interactions
    }
    
    result = make_api_request("POST", "/analytics/behavior", json_data=behavior_data)
    if result:
        return result
    
    return {"error": "分析学习行为失败，请稍后重试"}

@retry(max_retries=3)
def get_learning_weaknesses(user_id: int) -> Dict:
    """获取学习弱点分析"""
    # GET方法访问 /analytics/weaknesses/{user_id} 端点 (表格项8)
    result = make_api_request("GET", f"/analytics/weaknesses/{user_id}")
    
    if result:
        return result
    
    return {"error": "获取学习弱点分析失败，请稍后重试"}

@retry(max_retries=3)
def generate_adaptive_test(user_id: int, subject: str, topic: str, difficulty: str = "auto") -> Dict:
    """生成自适应测试"""
    # POST方法访问 /assessment/adaptive-test 端点 (表格项10)
    test_request = {
        "user_id": user_id,
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty
    }
    
    result = make_api_request("POST", "/assessment/adaptive-test", json_data=test_request)
    if result:
        return result
    
    return {"error": "生成自适应测试失败，请稍后重试"}

@retry(max_retries=3)
def create_content(content_data: Dict) -> Dict:
    """创建学习内容"""
    # POST方法访问 /content 端点 (表格项11)
    result = make_api_request("POST", "/content", json_data=content_data)
    if result:
        return result
    
    return {"error": "创建内容失败，请稍后重试"}

@retry(max_retries=3)
def get_assessment_questions() -> List[Dict]:
    """获取评估问题列表"""
    # 这个端点不在表格中，但是保持现有功能
    result = make_api_request("GET", "/assessment/questions")
    if result:
        return result
    
    logger.warning("获取评估问题失败，使用测试数据")
    return TEST_DATA["assessment_questions"]

@retry(max_retries=3)
def get_content(content_id: Any) -> Dict:
    """获取指定内容的详情"""
    # 验证内容ID是否有效
    if not isinstance(content_id, (int, str)) or isinstance(content_id, list):
        logger.error(f"无效的内容ID类型: {type(content_id)}, 值: {content_id}")
        return {
            "id": -1,
            "title": "无效内容",
            "description": "该内容不存在或ID格式无效",
            "content_type": "text",
            "content_data": {"text": "无法加载内容，请选择其他内容或联系管理员。"}
        }
    
    # 尝试将内容ID转换为整数
    try:
        if isinstance(content_id, str) and content_id.isdigit():
            content_id = int(content_id)
    except ValueError:
        logger.error(f"无法将内容ID转换为整数: {content_id}")
        content_id = -1
    
    # 调用API获取内容
    result = make_api_request("GET", f"/content/{content_id}")
    
    if result:
        return result
    
    logger.warning(f"获取内容失败 (ID: {content_id})，使用测试数据")
    
    # 提供测试数据作为后备
    return {
        "id": content_id if isinstance(content_id, int) else -1,
        "title": "测试内容",
        "description": "这是一个临时的测试内容",
        "content_type": "text",
        "content_data": {"text": "这是测试内容的正文。实际内容将从API获取。"},
        "difficulty_level": 1,
        "estimated_time": 10,
        "tags": ["测试"]
    }
