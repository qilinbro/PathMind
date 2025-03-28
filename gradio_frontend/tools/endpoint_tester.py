#!/usr/bin/env python
"""
API 端点测试工具 - 针对学习路径API端点格式问题
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
        logging.FileHandler("endpoint_tester.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("endpoint_tester")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
USER_ID = 1

def test_endpoint(name, method, url, params=None, data=None, expected_status=None):
    """测试API端点"""
    logger.info(f"测试 {name}: {method} {url}")
    if params:
        logger.info(f"参数: {params}")
    if data:
        logger.info(f"数据: {data}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params)
        else:
            logger.error(f"不支持的HTTP方法: {method}")
            return False
        
        status_code = response.status_code
        logger.info(f"状态码: {status_code}")
        
        if expected_status and status_code != expected_status:
            logger.warning(f"状态码不匹配，期望: {expected_status}, 实际: {status_code}")
        
        if status_code < 400:
            try:
                result = response.json()
                logger.info(f"响应: {json.dumps(result, indent=2)[:200]}...")
                return True
            except:
                logger.warning(f"响应不是有效的JSON: {response.text[:100]}")
                return False
        else:
            logger.error(f"错误响应: {response.text}")
            return False
    except Exception as e:
        logger.error(f"请求异常: {e}")
        return False

def test_learning_path_endpoints():
    """测试学习路径相关的所有可能端点格式"""
    endpoints = [
        # 已注册路径 - 正确格式
        ("已注册路径", "GET", f"{BASE_URL}/learning-paths", {"user_id": USER_ID, "enrolled": "true"}),
        
        # 推荐路径 - 正确格式
        ("推荐路径", "GET", f"{BASE_URL}/learning-paths", {"user_id": USER_ID, "recommended": "true"}),
        
        # 路径详情 - 正确格式
        ("路径详情", "GET", f"{BASE_URL}/learning-paths/1", {"user_id": USER_ID}),
        
        # 其他端点
        ("评估问题", "GET", f"{BASE_URL}/assessment/questions", None),
        ("内容列表", "GET", f"{BASE_URL}/content", None),
    ]
    
    success_count = 0
    for args in endpoints:
        success = test_endpoint(*args)
        if success:
            success_count += 1
        logger.info("-" * 50)
    
    logger.info(f"测试结果：{success_count}/{len(endpoints)} 个端点可成功访问")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("开始测试学习路径API端点格式")
    logger.info("=" * 50)
    
    test_learning_path_endpoints()
