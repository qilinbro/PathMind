"""
调试工具函数，用于分析API响应和故障排查
"""
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def analyze_api_response(response_data, endpoint_name="未知端点"):
    """
    分析API响应，记录结构信息
    
    Args:
        response_data: API响应数据
        endpoint_name: 端点名称，用于日志记录
    
    Returns:
        dict: 分析结果
    """
    result = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint_name,
        "is_error": False,
        "structure_info": {}
    }
    
    try:
        if isinstance(response_data, dict):
            if "error" in response_data:
                result["is_error"] = True
                result["error_message"] = response_data["error"]
                logger.error(f"{endpoint_name} 返回错误: {response_data['error']}")
                return result
            
            result["structure_info"]["type"] = "dict"
            result["structure_info"]["keys"] = list(response_data.keys())
            result["structure_info"]["key_types"] = {
                k: type(v).__name__ for k, v in response_data.items()
            }
            
            # 检查是否有嵌套结构
            for key, value in response_data.items():
                if isinstance(value, dict):
                    result["structure_info"][f"nested_{key}_keys"] = list(value.keys())
                elif isinstance(value, list) and len(value) > 0:
                    result["structure_info"][f"list_{key}_length"] = len(value)
                    if isinstance(value[0], dict):
                        result["structure_info"][f"list_{key}_item_keys"] = list(value[0].keys())
            
            logger.info(f"{endpoint_name} 响应结构: {json.dumps(result['structure_info'], ensure_ascii=False)}")
        
        elif isinstance(response_data, list):
            result["structure_info"]["type"] = "list"
            result["structure_info"]["length"] = len(response_data)
            
            if len(response_data) > 0:
                first_item = response_data[0]
                result["structure_info"]["first_item_type"] = type(first_item).__name__
                
                if isinstance(first_item, dict):
                    result["structure_info"]["first_item_keys"] = list(first_item.keys())
            
            logger.info(f"{endpoint_name} 响应是列表，长度: {len(response_data)}")
        
        else:
            result["structure_info"]["type"] = type(response_data).__name__
            logger.info(f"{endpoint_name} 响应是 {type(response_data).__name__} 类型")
        
        return result
    
    except Exception as e:
        logger.error(f"分析 {endpoint_name} 响应时出错: {str(e)}")
        result["is_error"] = True
        result["error_message"] = f"分析错误: {str(e)}"
        return result

def create_debug_entry_point(api_service):
    """创建一个可以在任何界面中调用的调试函数"""
    
    async def debug_api_endpoint(endpoint, method="GET", data=None):
        """调试特定API端点"""
        try:
            logger.info(f"调试端点 {method} {endpoint}")
            
            # 准备请求数据
            request_data = None
            if data:
                try:
                    if isinstance(data, str):
                        request_data = json.loads(data)
                    else:
                        request_data = data
                except:
                    logger.error("无法解析请求数据为JSON")
                    return {"error": "请求数据格式无效"}
            
            # 发送API请求
            response = await api_service.request(method, endpoint, data=request_data)
            
            # 分析响应
            analysis = analyze_api_response(response, endpoint)
            
            # 添加原始响应
            analysis["raw_response"] = response
            
            return analysis
        except Exception as e:
            logger.error(f"调试端点时出错: {str(e)}")
            return {"error": f"调试错误: {str(e)}"}
    
    return debug_api_endpoint
