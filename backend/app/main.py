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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend_api.log", encoding="utf-8")
    ]
)
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

# 添加CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应时间
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (took: {process_time:.3f}s)")
    
    return response

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
        has_key = bool(api_service.api_key)
        has_client = api_service.client is not None
        
        return {
            "api_key_configured": has_key,
            "client_available": has_client,
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"检查API状态时发生错误: {str(e)}")
        return {
            "error": str(e),
            "environment": settings.ENVIRONMENT
        }

# 注册API路由，合理安排顺序，避免冲突
# 1. 先注册API版本前缀路径
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. 注册带完整前缀的路由
app.include_router(
    assessment_v1.router, 
    prefix="/api/v1/assessment", 
    tags=["assessment"]
)

app.include_router(
    content_v1.router,
    prefix="/api/v1/content",
    tags=["content"]
)

app.include_router(
    learning_path.router,
    prefix="/api/v1/learning-paths",
    tags=["learning-paths"]
)

# 3. 注册自定义前缀的路由
app.include_router(analytics.router)

# 4. 最后注册learning路由，避免与learning-paths冲突
app.include_router(learning_path_router)

# 添加路由器注册日志以便调试
logger.info(f"已注册路由: {[route.path for route in app.routes]}")

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}")
    logger.error(traceback.format_exc())
    
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