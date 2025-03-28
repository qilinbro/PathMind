import logging
import httpx
import json
from datetime import datetime

# 设置日志
logger = logging.getLogger("api_service")

class ApiService:
    """API服务类，处理所有与后端API的交互"""
    def __init__(self, base_url):
        self.base_url = base_url
        
    async def request(self, method, endpoint, data=None, params=None, timeout=10.0):
        """执行API请求，与test_full_flow.py保持一致的格式"""
        # 确保endpoint没有前导斜杠
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        # 特殊处理health端点 - 不添加API前缀
        if endpoint == "health":
            url = "http://localhost:8000/health"
        else:
            # 构建完整URL
            base_url = self.base_url.rstrip('/')
            url = f"{base_url}/{endpoint}"
        
        # 确保URL使用正确的协议格式
        if not url.startswith(('http://', 'https://')):
            if url.startswith('http:/'):
                url = url.replace('http:/', 'http://')
            elif url.startswith('https:/'):
                url = url.replace('https:/', 'https://')
        
        # 移除URL中的双斜杠(除了协议部分)
        url = url.replace('://', ':@@')  # 临时替换协议的双斜杠
        while '//' in url:
            url = url.replace('//', '/')
        url = url.replace(':@@', '://')  # 恢复协议的双斜杠
        
        # 日志输出请求信息
        logger.info(f"请求 {method} {url}")
        if data:
            logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False)[:200]}")
        if params:
            logger.info(f"请求参数: {params}")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # 添加更详细的日志记录，特别是对adaptive-test端点
                if endpoint == "assessment/adaptive-test":
                    logger.info(f"发送自适应测试请求: URL={url}, 数据={json.dumps(data, ensure_ascii=False)}")
                    logger.info(f"自适应测试请求开始时间: {datetime.now().isoformat()}")
                
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, params=params)
                else:
                    return {"error": f"不支持的HTTP方法: {method}"}
                
                # 特别记录自适应测试的响应结果
                if endpoint == "assessment/adaptive-test":
                    logger.info(f"收到自适应测试响应: 状态码={response.status_code}, 时间={datetime.now().isoformat()}")
                    if response.status_code < 400:
                        try:
                            resp_data = response.json()
                            logger.info(f"自适应测试题目数量: {len(resp_data.get('questions', []))}")
                            logger.info(f"自适应测试响应类型: {type(resp_data)}")
                            logger.info(f"自适应测试响应内容前100字符: {str(resp_data)[:100]}...")
                        except Exception as e:
                            logger.warning(f"无法解析自适应测试响应为JSON: {str(e)}")
                            logger.warning(f"响应内容前100字符: {response.text[:100]}...")
                
                logger.info(f"响应状态: {response.status_code}")
                
                if response.status_code >= 400:
                    error_msg = f"HTTP错误 {response.status_code}"
                    try:
                        error_detail = response.text[:500]
                        logger.error(f"{error_msg}: {error_detail}")
                    except:
                        logger.error(error_msg)
                    return {"error": error_msg}
                
                # 尝试解析JSON响应
                try:
                    json_data = response.json()
                    # 对adaptive-test端点记录完整响应
                    if endpoint == "assessment/adaptive-test":
                        logger.info(f"自适应测试完整响应: {json.dumps(json_data, ensure_ascii=False)}")
                    else:
                        logger.info(f"响应JSON: {json.dumps(json_data, ensure_ascii=False)[:200]}...")
                    return json_data
                except ValueError:
                    logger.warning(f"响应不是JSON格式: {response.text[:200]}...")
                    return {"error": "响应不是有效的JSON格式", "text": response.text[:500]}
        except Exception as e:
            logger.error(f"API请求异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": f"API请求异常: {str(e)}"}

    def diagnose_api(self):
        """诊断API状态 - 减少不必要的404日志"""
        results = {}
        try:
            # 同步调用以简化代码
            with httpx.Client(timeout=5.0) as client:
                # 1. 首先只检查健康端点 - 直接使用正确的URL
                health_url = "http://localhost:8000/health"
                logger.info(f"检查健康端点: {health_url}")
                try:
                    health_resp = client.get(health_url)
                    health_ok = health_resp.status_code < 400
                    results["健康检查"] = {
                        "ok": health_ok,
                        "status": f"HTTP {health_resp.status_code}",
                        "response": health_resp.json() if health_ok else {}
                    }
                    
                    # 如果健康检查失败，不继续尝试其他API
                    if not health_ok:
                        logger.warning("健康检查失败，跳过后续API检查")
                        return results
                        
                except Exception as e:
                    results["健康检查"] = {
                        "ok": False,
                        "status": f"错误: {str(e)}"
                    }
                    logger.warning(f"健康检查异常: {str(e)}，跳过后续API检查")
                    return results
                
                # 2. 检查API根端点 - 直接使用预期的工作URL而不是尝试多个
                api_url = "http://localhost:8000/api/v1"
                logger.debug(f"检查API根端点: {api_url}") # 降低日志级别到DEBUG
                try:
                    api_resp = client.get(api_url)
                    api_ok = api_resp.status_code < 400
                    results["API根"] = {
                        "ok": api_ok,
                        "status": f"HTTP {api_resp.status_code}",
                        "response": api_resp.json() if api_ok else {},
                        "url": api_url
                    }
                    
                    if api_ok:
                        # 更新base_url为成功的API根路径
                        self.base_url = api_url
                    else:
                        logger.warning(f"API根端点返回状态码: {api_resp.status_code}")
                except Exception as e:
                    logger.debug(f"API根端点检查失败: {str(e)}")
                    results["API根"] = {
                        "ok": False,
                        "status": "无法连接",
                        "info": str(e)
                    }
                
                # 3. 检查自适应测试端点 - 我们希望确认这个端点是否存在可用
                adaptive_test_endpoint = "assessment/adaptive-test"
                try:
                    url = f"{self.base_url.rstrip('/')}/{adaptive_test_endpoint}"
                    logger.info(f"检查自适应测试端点: {url}")
                    
                    # 为了测试端点，我们发送一个简单的POST请求
                    test_data = {
                        "user_id": 1,
                        "subject": "programming", 
                        "topic": "Python基础",
                        "difficulty": "auto"
                    }
                    
                    resp = client.post(url, json=test_data)
                    results["自适应测试"] = {
                        "ok": resp.status_code < 400,
                        "status": f"HTTP {resp.status_code}"
                    }
                    
                    if resp.status_code < 400:
                        logger.info("自适应测试端点可用")
                        try:
                            response_data = resp.json()
                            question_count = len(response_data.get("questions", []))
                            logger.info(f"自适应测试返回了 {question_count} 个问题")
                        except Exception as parse_error:
                            logger.warning(f"无法解析自适应测试响应: {str(parse_error)}")
                    else:
                        logger.warning(f"自适应测试端点返回错误状态: {resp.status_code}")
                except Exception as e:
                    logger.warning(f"检查自适应测试端点失败: {str(e)}")
                    results["自适应测试"] = {
                        "ok": False,
                        "status": f"错误: {str(e)}"
                    }
        except Exception as e:
            logger.error(f"API诊断异常: {str(e)}")
            results["诊断异常"] = {
                "ok": False,
                "status": f"错误: {str(e)}"
            }
        
        return results

    # 测试数据方法
    def _get_test_assessment_questions(self):
        """获取测试评估问题"""
        return [
            {
                "id": 1,
                "question_text": "我更喜欢通过图表和图像学习新概念。",
                "question_type": "scale",
                "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
            },
            {
                "id": 2,
                "question_text": "我喜欢听讲座和音频材料来学习。",
                "question_type": "scale",
                "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
            },
            {
                "id": 3,
                "question_text": "我通过动手实践学习效果最好。",
                "question_type": "scale",
                "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
            }
        ]
    
    def _get_test_enrolled_paths(self):
        """获取测试已注册学习路径"""
        return [
            {
                "id": 1,
                "title": "Python编程基础",
                "description": "从零开始学习Python编程",
                "progress": 35,
                "last_activity": "2023-08-15T14:30:00Z"
            },
            {
                "id": 2,
                "title": "数据科学入门",
                "description": "数据分析和可视化基础",
                "progress": 20,
                "last_activity": "2023-08-10T09:15:00Z"
            }
        ]
    
    def _get_test_recommended_paths(self):
        """获取测试推荐学习路径"""
        return [
            {
                "id": 3,
                "title": "机器学习基础",
                "description": "机器学习算法和应用",
                "match_score": 85,
                "estimated_hours": 40
            },
            {
                "id": 4,
                "title": "Web开发入门",
                "description": "HTML, CSS和JavaScript基础",
                "match_score": 75,
                "estimated_hours": 30
            }
        ]
    
    def _get_test_path_details(self, path_id):
        """获取测试学习路径详情"""
        return {
            "id": path_id,
            "title": "Python编程基础",
            "description": "从零开始学习Python编程的综合路径",
            "difficulty_level": 2,
            "estimated_hours": 25,
            "progress": 35,
            "contents": [
                {
                    "id": 1,
                    "title": "Python安装和环境设置",
                    "type": "video",
                    "progress": 100,
                    "duration": 15
                },
                {
                    "id": 2,
                    "title": "变量和数据类型",
                    "type": "interactive",
                    "progress": 80,
                    "duration": 25
                },
                {
                    "id": 3,
                    "title": "控制流语句",
                    "type": "reading",
                    "progress": 0,
                    "duration": 20
                }
            ]
        }
    
    def _get_test_content(self, content_id):
        """获取测试内容详情"""
        return {
            "id": content_id,
            "title": "变量和数据类型",
            "description": "学习Python中的变量声明和基本数据类型",
            "content_type": "interactive",
            "content_data": {
                "url": "https://example.com/python-variables",
                "exercises": [
                    {
                        "question": "在Python中，如何声明一个整数变量x并赋值为10？",
                        "options": ["x = 10", "int x = 10", "x := 10", "x <- 10"],
                        "correct": 0
                    },
                    {
                        "question": "以下哪个是Python中的列表类型？",
                        "options": ["(1, 2, 3)", "[1, 2, 3]", "{1, 2, 3}", "{'a': 1, 'b': 2}"],
                        "correct": 1
                    }
                ]
            }
        }

def check_api_status(api_service):
    """检查API服务状态"""
    try:
        # 使用诊断API功能
        api_info = api_service.diagnose_api()
        
        # 分析诊断结果
        available_endpoints = [name for name, info in api_info.items() if info["ok"]]
        unavailable_endpoints = [name for name, info in api_info.items() if not info["ok"]]
        
        # 获取API版本信息
        api_version = "未知"
        api_name = "学习路径API"
        if "API根" in api_info and api_info["API根"]["ok"]:
            api_data = api_info["API根"]["response"]
            api_version = api_data.get("version", "未知")
            api_name = api_data.get("message", "学习路径API").replace("Welcome to ", "").replace(" API", "")
            
        # 确定状态
        if len(unavailable_endpoints) == 0:
            status = "正常"
            message = "所有API服务正常运行"
        elif "健康检查" in unavailable_endpoints:
            status = "不可用"
            message = "API服务不可用，请确保后端服务已启动"
        elif len(available_endpoints) >= 2:  # 至少健康检查和另一个端点可用
            status = "部分可用"
            message = f"部分API端点可用，不可用端点: {', '.join(unavailable_endpoints)}"
        else:
            status = "功能受限"
            message = f"大部分API端点不可用，仅有: {', '.join(available_endpoints)}"
            
        return {
            "status": status,
            "message": message,
            "api_info": f"{api_name} {api_version}",
            "details": api_info
        }
    except Exception as e:
        logger.error(f"API状态检查异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "错误",
            "message": f"API状态检查失败: {str(e)}"
        }
