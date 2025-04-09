"""
Logging configuration for the application
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging configuration"""
    # 创建logs目录（如果不存在）
    logs_dir = os.path.join("backend", "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 配置格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(requestId)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置文件处理器
    file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir, "backend_api.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 配置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 配置特定模块的日志级别
    logging.getLogger('app.services.ai_service').setLevel(logging.DEBUG)
    logging.getLogger('app.api').setLevel(logging.INFO)
    
    # 配置请求ID过滤器
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'requestId'):
                record.requestId = '-'
            return True
    
    # 添加请求ID过滤器到所有处理器
    request_id_filter = RequestIdFilter()
    file_handler.addFilter(request_id_filter)
    console_handler.addFilter(request_id_filter)
    
    # 配置其他日志设置
    logging.getLogger('uvicorn.access').handlers = []
    logging.getLogger('uvicorn.error').handlers = []