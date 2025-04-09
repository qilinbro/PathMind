import os
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import validator, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Learning Path Platform"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # 兼容旧配置
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
    JWT_ALGORITHM: str = "HS256"
    
    # CORS设置
    CORS_ORIGINS: List[str] = ["*"]
    BACKEND_CORS_ORIGINS: Optional[Union[List[str], str]] = None  # 兼容旧配置
    
    # ZhipuAI API配置
    ZHIPUAI_API_KEY: str = os.getenv("ZHIPUAI_API_KEY", "")
    ZHIPUAI_MODEL: str = os.getenv("ZHIPUAI_MODEL", "glm-4-plus")
    ZHIPUAI_TIMEOUT: int = int(os.getenv("ZHIPUAI_TIMEOUT", 30))
    
    # 环境设置
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, testing, production
    PRODUCTION: bool = ENVIRONMENT == "production"
    
    # 测试相关配置
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "False").lower() in ("true", "1", "t")
    
    # API设置
    API_TIMEOUT: float = float(os.getenv("API_TIMEOUT", "10.0"))  # API调用的默认超时时间(秒)
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外的配置项

settings = Settings()

# 向后兼容：如果存在旧配置，更新新配置
if settings.SQLALCHEMY_DATABASE_URI and not settings.DATABASE_URL:
    settings.DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

if settings.BACKEND_CORS_ORIGINS and not settings.CORS_ORIGINS:
    settings.CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS