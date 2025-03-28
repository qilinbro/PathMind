#!/usr/bin/env python
"""
API 路由测试工具 - 确保前端使用正确的API路由格式
"""
import sys
import requests
import json
import logging
from pathlib import Path

# 添加项目根目录到Python路径
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.append(str(ROOT_DIR))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_routes.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("api_routes")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def verify_and_document_routes():
    """验证API路由并生成文档"""
    logger.info("开始验证API路由...")
    
    # 更新端点测试，严格按照测试文件的格式
    endpoints = [
        # 健康检查 - 简单GET请求
        {"name": "服务器健康检查", "method": "GET", "url": "http://localhost:8000/health", 
         "params": {}, "expected_error": False},
        
        # POST请求 - JSON数据在请求体中
        {"name": "提交评估", "method": "POST", "url": f"{BASE_URL}/assessment/submit", 
         "json_data": {
             "user_id": 1,
             "responses": [
                 {"question_id": 1, "response_value": {"answer": "5"}, "response_time": 3.5}
             ]
         },
         "expected_error": False},
        
        # GET请求 - 查询参数直接附加到URL
        {"name": "学习路径详情", "method": "GET", "url": f"{BASE_URL}/learning-paths/1", 
         "params": {"user_id": 1}, "expected_error": False},
         
        # user_id作为查询参数，其他数据在请求体
        {"name": "更新学习进度", "method": "POST", "url": f"{BASE_URL}/learning-paths/1/progress", 
         "params": {"user_id": 1},
         "json_data": {
             "content_id": 1,
             "progress": 75.0
         },
         "expected_error": False},
        
        # 其他端点
        {"name": "创建学习路径", "method": "POST", "url": f"{BASE_URL}/learning-paths", 
         "json_data": {
             "title": "Python编程基础路径",
             "description": "从零开始学习Python编程的个性化路径",
             "subject": "programming",
             "difficulty_level": 2,
             "estimated_hours": 25,
             "goals": ["掌握Python基础语法"],
             "difficulty": "beginner",
             "created_by": 1
         }, 
         "expected_error": False},
        
        {"name": "获取已注册路径", "method": "POST", "url": f"{BASE_URL}/learning-paths", 
         "json_data": {"user_id": 1, "enrolled": True}, "expected_error": False},
        
        {"name": "获取推荐路径", "method": "POST", "url": f"{BASE_URL}/learning-paths", 
         "json_data": {"user_id": 1, "recommended": True}, "expected_error": False},
        
        {"name": "注册学习路径", "method": "POST", "url": f"{BASE_URL}/learning-paths/enroll", 
         "json_data": {
             "user_id": 1,
             "path_id": 1,
             "personalization_settings": {
                 "preferred_content_types": ["video", "interactive"],
                 "study_reminder": True
             }
         }, 
         "expected_error": False},
        
        {"name": "分析学习行为", "method": "POST", "url": f"{BASE_URL}/analytics/behavior", 
         "json_data": {
             "user_id": 1,
             "content_interactions": [
                 {
                     "content_id": 1,
                     "time_spent": 1200,
                     "interaction_type": "video",
                     "progress": 0.8
                 }
             ]
         },
         "expected_error": False},
        
        {"name": "获取学习弱点", "method": "GET", "url": f"{BASE_URL}/analytics/weaknesses/1", 
         "params": {}, "expected_error": False},
        
        {"name": "获取学习进度", "method": "GET", "url": f"{BASE_URL}/assessment/progress/1", 
         "params": {}, "expected_error": False},
        
        {"name": "生成自适应测试", "method": "POST", "url": f"{BASE_URL}/assessment/adaptive-test", 
         "json_data": {
             "user_id": 1,
             "subject": "programming",
             "topic": "Python基础",
             "difficulty": "auto"
         },
         "expected_error": False},
        
        {"name": "创建内容", "method": "POST", "url": f"{BASE_URL}/content", 
         "json_data": {
             "title": "Python基础语法",
             "description": "学习Python编程的基础语法和概念",
             "content_type": "video",
             "subject": "programming",
             "difficulty_level": 1,
             "content_data": {
                 "url": "https://example.com/python-basics",
                 "duration": 3600
             }
         }, 
         "expected_error": False},
        
        # 额外端点（不在表格中，但仍保留测试）
        {"name": "评估问题列表", "method": "GET", "url": f"{BASE_URL}/assessment/questions", 
         "params": {}, "expected_error": False},
    ]
    
    # 测试端点并收集结果
    results = []
    for endpoint in endpoints:
        try:
            logger.info(f"测试: {endpoint['name']}")
            logger.info(f"方法: {endpoint['method']}")
            logger.info(f"URL: {endpoint['url']}")
            
            if endpoint.get('params'):
                logger.info(f"参数: {endpoint.get('params')}")
            if endpoint.get('json_data'):
                logger.info(f"JSON数据: {endpoint.get('json_data')}")
            
            # 添加超时设置
            timeout = 10
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], params=endpoint.get('params'), timeout=timeout)
            elif endpoint['method'] == 'POST':
                response = requests.post(endpoint['url'], json=endpoint.get('json_data'), timeout=timeout)
            else:
                logger.error(f"不支持的HTTP方法: {endpoint['method']}")
                continue
                
            status_code = response.status_code
            
            # 尝试解析响应JSON
            try:
                response_json = response.json()
                logger.info(f"响应数据: {json.dumps(response_json, ensure_ascii=False)[:100]}...")
            except:
                logger.info(f"响应内容: {response.text[:100]}...")
            
            is_error = status_code >= 400
            expected_result = is_error == endpoint.get('expected_error', False)
            
            result = {
                "name": endpoint['name'],
                "method": endpoint['method'],
                "url": endpoint['url'],
                "params": endpoint.get('params'),
                "json_data": endpoint.get('json_data'),
                "status": status_code,
                "is_error": is_error,
                "matches_expectation": expected_result,
                "response": response.text[:200] + "..." if len(response.text) > 200 else response.text
            }
            
            results.append(result)
            logger.info(f"状态码: {status_code}")
            logger.info(f"符合预期: {'是' if expected_result else '否'}")
            logger.info("-" * 50)
            
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {endpoint['url']}")
            results.append({
                "name": endpoint['name'],
                "method": endpoint['method'],
                "url": endpoint['url'],
                "params": endpoint.get('params'),
                "json_data": endpoint.get('json_data'),
                "error": "请求超时",
                "is_error": True,
                "matches_expectation": endpoint.get('expected_error', True)
            })
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            results.append({
                "name": endpoint['name'],
                "method": endpoint['method'],
                "url": endpoint['url'],
                "params": endpoint.get('params'),
                "json_data": endpoint.get('json_data'),
                "error": str(e),
                "is_error": True,
                "matches_expectation": endpoint.get('expected_error', False)
            })
    
    # 生成文档更新
    logger.info("\n=== API路由参考文档 ===")
    logger.info("以下是正确的API路由格式:")
    
    md_content = "# API路由参考\n\n"
    md_content += "## 学习路径API\n\n"
    
    # 添加已验证的正确端点
    working_endpoints = {}
    
    for result in results:
        if not result.get("is_error") and result.get("status") == 200:
            category = result["name"].split("-")[0] if "-" in result["name"] else result["name"]
            
            # 保存每个类别的第一个工作端点
            if category not in working_endpoints:
                working_endpoints[category] = result
    
    # 将工作端点添加到文档
    for category, result in working_endpoints.items():
        name = category
        url = result["url"].replace(BASE_URL, "")
        method = result["method"]
        
        md_content += f"### {name}\n"
        md_content += f"- 方法: `{method}`\n"
        md_content += f"- 端点: `{url}`\n"
        
        if result.get("params"):
            if method == "GET":
                params = "&".join([f"{k}={v}" for k, v in result.get("params", {}).items()])
                md_content += f"- 参数: `?{params}`\n"
            else:
                md_content += f"- 请求体: `{json.dumps(result.get('json_data'), ensure_ascii=False)}`\n"
                
        md_content += f"- 状态码: {result.get('status')}\n\n"
    
    # 保存到文件
    with open(ROOT_DIR / "api_routes_reference.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    logger.info(f"参考文档已保存至: {ROOT_DIR / 'api_routes_reference.md'}")
    return results

if __name__ == "__main__":
    verify_and_document_routes()
