import json
import traceback
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class ErrorTracker:
    """错误跟踪工具类，用于记录API请求错误并提供详细诊断"""
    
    @staticmethod
    def log_request_error(endpoint: str, request_data: Any, error: Exception) -> Dict[str, Any]:
        """记录API请求错误并返回诊断信息"""
        error_id = id(error)  # 生成唯一错误ID用于引用
        
        # 记录错误详情
        logger.error(f"[ERROR-{error_id}] 请求 '{endpoint}' 失败")
        
        try:
            # 尝试序列化请求数据
            request_str = json.dumps(request_data, ensure_ascii=False)
            logger.error(f"[ERROR-{error_id}] 请求数据: {request_str[:500]}")
        except:
            logger.error(f"[ERROR-{error_id}] 请求数据无法序列化")
        
        # 记录异常栈
        logger.error(f"[ERROR-{error_id}] 异常类型: {type(error).__name__}")
        logger.error(f"[ERROR-{error_id}] 异常信息: {str(error)}")
        logger.error(f"[ERROR-{error_id}] 异常栈:\n{traceback.format_exc()}")
        
        # 返回诊断信息
        return {
            "error_id": f"ERR-{error_id}",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "endpoint": endpoint,
            "diagnostic_info": "请查看服务器日志获取完整错误堆栈"
        }
    
    @staticmethod
    def get_fallback_response(endpoint: str, error: Exception, fallback_data: Any = None) -> Dict[str, Any]:
        """获取错误回退响应"""
        error_info = ErrorTracker.log_request_error(endpoint, None, error)
        
        # 如果提供了回退数据，使用它
        if fallback_data:
            result = fallback_data
            # 添加错误信息
            if isinstance(fallback_data, dict):
                result["error_info"] = error_info
            return result
        
        # 默认回退响应
        return {
            "error": f"处理请求时发生错误: {str(error)}",
            "error_info": error_info,
            "status": "error"
        }
