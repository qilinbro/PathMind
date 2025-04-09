from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback
import uvicorn
import time
import os

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base
from app.db.init_db import init_db
from app.db.session import get_db
from app.routers import analytics
from app.api.v1.endpoints import assessment as assessment_v1
from app.api.v1.endpoints import content as content_v1
from app.routers.learning_path import router as learning_path_router
from app.api.v1.endpoints import learning_path
from app.logging_config import setup_logging

# 配置日志
setup_logging()
logger = logging.getLogger("backend")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="学习路径平台的后端API服务",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

db = next(get_db())

# Initialize database with default data
init_db(db)

# 添加日志中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 生成请求ID
    request_id = str(int(time.time() * 1000))
    # 将请求ID添加到请求对象
    request.state.request_id = request_id
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url}", extra={"requestId": request_id})
    
    try:
        # 处理请求
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(
            f"Response: {response.status_code} (took: {process_time:.3f}s)",
            extra={"requestId": request_id}
        )
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        logger.exception(
            f"Request failed: {str(e)}",
            extra={"requestId": request_id}
        )
        raise

# 添加CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API根路径端点
@app.get("/api/v1")
async def api_root():
    """API根路径端点"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0",
        "description": "学习路径平台API",
        "endpoints": {
            "assessment": "/api/v1/assessment",
            "content": "/api/v1/content",
            "learning_paths": "/api/v1/learning-paths",
            "analytics": "/api/v1/analytics"
        }
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "api_version": "1.0"}

# 测试ZhipuAI API连接端点
@app.get("/api-status")
async def api_status():
    """检查智谱API连接状态"""
    from app.services.ai_service import AIService
    
    try:
        api_service = AIService()
        has_client = bool(api_service.client)
        
        return {
            "api_key_configured": bool(api_service.api_key),
            "client_available": has_client,
            "model": api_service.model,
            "timeout": api_service.timeout,
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"检查API状态时发生错误: {str(e)}")
        return {
            "error": str(e),
            "environment": settings.ENVIRONMENT
        }

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(assessment_v1.router, prefix="/api/v1/assessment", tags=["assessment"])
app.include_router(content_v1.router, prefix="/api/v1/content", tags=["content"])
app.include_router(learning_path.router, prefix="/api/v1/learning-paths", tags=["learning-paths"])
app.include_router(analytics.router)
app.include_router(learning_path_router)

# 添加路由器注册日志
logger.info(f"已注册路由: {[route.path for route in app.routes]}")

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.error(
        f"全局异常: {str(exc)}",
        extra={"requestId": request_id}
    )
    logger.error(
        f"错误堆栈:\n{traceback.format_exc()}",
        extra={"requestId": request_id}
    )
    
    # 对于HTTP异常，保持原始状态码
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    # 其他异常作为500错误返回
    error_msg = str(exc)
    if settings.PRODUCTION:
        error_msg = "服务器内部错误"
    
    return JSONResponse(
        status_code=500,
        content={"error": error_msg}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)