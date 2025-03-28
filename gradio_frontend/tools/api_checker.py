#!/usr/bin/env python
"""
API 诊断工具 - 检查后端API是否正确工作
"""
import sys
import os
import json
import requests
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
        logging.FileHandler("api_checker.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("api_checker")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def check_endpoint(method, endpoint, params=None, data=None, expected_status=200):
    """检查API端点是否正常工作"""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    logger.info(f"检查端点: {method} {url}")
    
    if params:
        logger.info(f"查询参数: {params}")
    if data:
        logger.info(f"请求数据: {data}")
    
    try:
        headers = {"Content-Type": "application/json"} if data else {}
        
        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params, headers=headers)
        else:
            logger.error(f"不支持的HTTP方法: {method}")
            return False, None
        
        status_ok = response.status_code == expected_status
        status_text = "成功" if status_ok else "失败"
        logger.info(f"状态码: {response.status_code} ({status_text})")
        
        if response.status_code >= 400:
            logger.error(f"错误响应: {response.text}")
            return False, None
        
        # 尝试解析JSON
        try:
            result = response.json()
            logger.info(f"响应摘要: {str(result)[:200]}...")
            return status_ok, result
        except json.JSONDecodeError:
            logger.warning(f"响应不是有效JSON: {response.text[:200]}...")
            return status_ok, response.text
            
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {str(e)}")
        return False, None

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始API诊断")
    logger.info("=" * 50)
    
    # 1. 健康检查
    base_url = BASE_URL.rsplit('/api/v1', 1)[0]
    logger.info(f"检查服务器健康状态: {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            logger.info(f"服务器状态: 健康 ({response.json()})")
        else:
            logger.error(f"服务器状态: 不健康 ({response.status_code})")
            logger.error("请确保后端服务器已启动")
            return
    except requests.exceptions.RequestException:
        logger.error("无法连接到服务器")
        logger.error("请确保后端服务器已启动")
        return
    
    # 2. 获取API版本
    logger.info(f"获取API版本信息: {base_url}")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"API版本: {data.get('version')}")
            logger.info(f"API信息: {data.get('message')}")
        else:
            logger.warning(f"无法获取API版本 ({response.status_code})")
    except:
        logger.warning("获取API版本失败")
    
    # 端点清单
    endpoints = [
        # 基本端点
        ("GET", "/assessment/questions", None, None),
        ("GET", "/content", None, None),
        
        # 用户相关端点
        ("GET", "/assessment/progress/1", None, None, 404), # 预期404
        ("GET", "/learning-paths/enrolled", {"user_id": 1}, None),
        ("GET", "/learning-paths/recommended", {"user_id": 1}, None),
        
        # 学习路径详情
        ("GET", "/learning-paths/1", {"user_id": 1}, None, 404), # 预期404，未创建路径
    ]
    
    results = {}
    for args in endpoints:
        endpoint = args[1]
        status, data = check_endpoint(*args)
        results[endpoint] = {
            "status": "正常" if status else "异常",
            "data": data if data else None
        }
    
    # 输出结果摘要
    logger.info("\n" + "=" * 50)
    logger.info("诊断结果摘要")
    logger.info("=" * 50)
    
    for endpoint, result in results.items():
        logger.info(f"{endpoint}: {result['status']}")
    
    # 尝试提交一个测试评估
    logger.info("\n尝试提交一个测试评估...")
    test_assessment = {
        "user_id": 1,
        "responses": [
            {"question_id": 1, "response_value": {"answer": "5"}, "response_time": 3.5},
            {"question_id": 2, "response_value": {"answer": "4"}, "response_time": 2.8},
            {"question_id": 3, "response_value": {"answer": "3"}, "response_time": 4.0},
            {"question_id": 4, "response_value": {"answer": "2"}, "response_time": 3.2}
        ]
    }
    
    success, result = check_endpoint("POST", "/assessment/submit", None, test_assessment)
    if success:
        logger.info("测试评估提交成功！")
        logger.info("现在应该可以查询学习风格和推荐路径了")
        
        # 尝试获取学习进度（应该可以了）
        logger.info("\n重新检查学习进度...")
        check_endpoint("GET", "/assessment/progress/1", None, None)
    else:
        logger.error("测试评估提交失败")
    
    logger.info("\n" + "=" * 50)
    logger.info("诊断完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("诊断被用户中断")
    except Exception as e:
        logger.error(f"诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
