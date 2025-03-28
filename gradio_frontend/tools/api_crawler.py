#!/usr/bin/env python
"""
API 爬虫 - 自动发现和测试 API 端点
"""
import sys
import os
import json
import requests
import logging
import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin

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
        logging.FileHandler("api_crawler.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("api_crawler")

# API基础URL
BASE_URL = "http://localhost:8000"
API_PATH = "/api/v1"
FULL_API_URL = f"{BASE_URL}{API_PATH}"

class ApiCrawler:
    """API爬虫，自动发现和测试端点"""
    
    def __init__(self, base_url=BASE_URL, api_path=API_PATH):
        self.base_url = base_url
        self.api_path = api_path
        self.full_api_url = f"{base_url}{api_path}"
        self.discovered_endpoints = set()
        self.tested_endpoints = {}
        self.known_patterns = [
            r'/api/v1/(\w+)',
            r'/api/v1/(\w+)/(\w+)',
            r'/api/v1/(\w+)/(\d+)',
            r'/api/v1/(\w+)/(\w+)/(\w+)',
            r'/api/v1/(\w+)/(\d+)/(\w+)',
        ]
    
    def discover_endpoints(self):
        """从API根路径开始发现可能的端点"""
        logger.info("开始发现API端点...")
        
        # 首先检查API根路径
        try:
            response = requests.get(self.base_url)
            if response.status_code == 200:
                logger.info(f"API根路径可访问: {self.base_url}")
                self._extract_endpoints(response.text)
            else:
                logger.warning(f"API根路径返回非200状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"访问API根路径失败: {str(e)}")
            return False
            
        # 检查API文档路径
        doc_paths = ["/docs", "/redoc", "/swagger", "/openapi.json"]
        for path in doc_paths:
            try:
                doc_url = urljoin(self.base_url, path)
                logger.info(f"尝试访问API文档: {doc_url}")
                response = requests.get(doc_url)
                if response.status_code == 200:
                    logger.info(f"发现API文档: {doc_url}")
                    self._extract_endpoints(response.text)
                    break
            except Exception as e:
                logger.debug(f"访问API文档失败: {str(e)}")
        
        # 也检查健康状态端点
        try:
            health_url = urljoin(self.base_url, "/health")
            response = requests.get(health_url)
            if response.status_code == 200:
                logger.info(f"健康检查端点可用: {health_url}")
                self.discovered_endpoints.add("/health")
        except Exception:
            pass
            
        # 添加常见端点模式
        common_resources = [
            "users", "learning-paths", "paths", "assessment", "content", 
            "analytics", "recommendations", "user-paths"
        ]
        
        for resource in common_resources:
            self.discovered_endpoints.add(f"{self.api_path}/{resource}")
            self.discovered_endpoints.add(f"{self.api_path}/{resource}s")  # 复数形式
            
            # 添加常见操作
            for operation in ["create", "get", "update", "delete", "list", "search"]:
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/{operation}")
                
            # 添加特定端点
            if resource == "assessment":
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/questions")
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/submit")
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/progress/1")
            elif resource in ["learning-paths", "paths"]:
                # 根据后端路由定义添加正确的API端点
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/enrolled")
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/recommended")
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/1")
                self.discovered_endpoints.add(f"{self.api_path}/{resource}/enroll")
        
        # 添加一些特定于路由参数的端点
        for i in range(1, 4):  # 测试一些ID
            self.discovered_endpoints.add(f"{self.api_path}/users/{i}")
            self.discovered_endpoints.add(f"{self.api_path}/users/{i}/paths")
            self.discovered_endpoints.add(f"{self.api_path}/users/{i}/recommendations")
            
        logger.info(f"共发现 {len(self.discovered_endpoints)} 个可能的API端点")
        return True
    
    def _extract_endpoints(self, text):
        """从响应文本中提取可能的API端点"""
        for pattern in self.known_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        path = f"/api/v1/{'/'.join(match)}"
                    else:
                        path = f"/api/v1/{match}"
                    self.discovered_endpoints.add(path)
    
    def test_endpoints(self):
        """测试所有发现的端点"""
        logger.info("开始测试发现的端点...")
        
        for endpoint in sorted(self.discovered_endpoints):
            full_url = f"{self.base_url}{endpoint}"
            logger.info(f"测试端点: GET {full_url}")
            
            try:
                # 对于需要用户ID的端点，添加查询参数
                params = {}
                if any(x in endpoint for x in ["user", "enroll", "progress"]):
                    params["user_id"] = 1
                
                response = requests.get(full_url, params=params)
                status = response.status_code
                
                logger.info(f"状态码: {status}")
                
                self.tested_endpoints[endpoint] = {
                    "method": "GET",
                    "url": full_url,
                    "status": status,
                    "success": status < 400,
                    "response": response.json() if status < 400 and response.content else None
                }
                
                time.sleep(0.1)  # 避免过于频繁的请求
            except Exception as e:
                logger.error(f"测试端点失败: {str(e)}")
                self.tested_endpoints[endpoint] = {
                    "method": "GET",
                    "url": full_url,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # 测试POST请求，确保符合后端期望的格式
        post_endpoints = [
            {"endpoint": f"{self.api_path}/assessment/submit", "data": {
                "user_id": 1,
                "responses": [
                    {"question_id": 1, "response_value": {"answer": "5"}, "response_time": 3.5},
                    {"question_id": 2, "response_value": {"answer": "3"}, "response_time": 4.2}
                ]
            }},
            {"endpoint": f"{self.api_path}/learning-paths", "data": {
                "title": "测试路径",
                "description": "API爬虫创建的测试路径",
                "subject": "testing",
                "difficulty_level": 2,
                "estimated_hours": 1,
                "goals": ["测试目标1", "测试目标2"],
                "difficulty": "medium",
                "created_by": 1
            }},
            {"endpoint": f"{self.api_path}/learning-paths/enroll", "data": {
                "user_id": 1,
                "path_id": 1,
                "personalization_settings": {}
            }}
        ]
        
        for item in post_endpoints:
            endpoint = item["endpoint"]
            data = item["data"]
            full_url = f"{self.base_url}{endpoint}"
            
            logger.info(f"测试端点: POST {full_url}")
            logger.debug(f"请求数据: {data}")
            
            try:
                response = requests.post(full_url, json=data)
                status = response.status_code
                
                logger.info(f"状态码: {status}")
                
                self.tested_endpoints[f"POST {endpoint}"] = {
                    "method": "POST",
                    "url": full_url,
                    "status": status,
                    "success": status < 400,
                    "response": response.json() if status < 400 and response.content else None
                }
            except Exception as e:
                logger.error(f"测试端点失败: {str(e)}")
                self.tested_endpoints[f"POST {endpoint}"] = {
                    "method": "POST", 
                    "url": full_url,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                }
    
    def generate_report(self):
        """生成API测试报告"""
        report = {
            "base_url": self.base_url,
            "api_path": self.api_path,
            "discovered_endpoints": len(self.discovered_endpoints),
            "successful_endpoints": sum(1 for e in self.tested_endpoints.values() if e["success"]),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints": self.tested_endpoints
        }
        
        # 按状态码分组
        by_status = {}
        for endpoint, data in self.tested_endpoints.items():
            status = data["status"]
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(endpoint)
        
        report["by_status"] = by_status
        
        # 保存报告
        report_file = f"api_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        logger.info(f"报告已保存至: {report_file}")
        
        # 打印摘要
        logger.info("\n" + "=" * 50)
        logger.info("API测试摘要")
        logger.info("=" * 50)
        logger.info(f"发现的端点总数: {report['discovered_endpoints']}")
        logger.info(f"成功的端点数量: {report['successful_endpoints']}")
        
        logger.info("\n状态码分布:")
        for status, endpoints in sorted(by_status.items()):
            status_name = "成功" if status < 400 else "失败"
            logger.info(f"  {status} ({status_name}): {len(endpoints)} 个端点")
            
        logger.info("\n可用的端点:")
        for endpoint, data in self.tested_endpoints.items():
            if data["success"]:
                logger.info(f"  {data['method']} {endpoint}")
                
        return report

def main():
    parser = argparse.ArgumentParser(description="API爬虫 - 自动发现和测试API端点")
    parser.add_argument("--base-url", default=BASE_URL, help="API基础URL")
    parser.add_argument("--api-path", default=API_PATH, help="API路径前缀")
    args = parser.parse_args()
    
    crawler = ApiCrawler(args.base_url, args.api_path)
    
    if crawler.discover_endpoints():
        crawler.test_endpoints()
        crawler.generate_report()
    else:
        logger.error("无法连接到API服务器")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
