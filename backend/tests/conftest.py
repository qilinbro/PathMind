import pytest
import asyncio
import sys
from pathlib import Path

# 将项目根目录添加到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from app.core.config import settings
from app.services.ai_service import AIService

# 跳过条件 - 如果没有配置API密钥
skip_if_no_api_key = pytest.mark.skipif(
    not settings.ZHIPU_API_KEY,
    reason="ZhipuAI API key not configured"
)

@pytest.fixture
def ai_service():
    """提供AI服务实例"""
    return AIService(settings.ZHIPU_API_KEY)

@pytest.fixture
def event_loop():
    """创建一个事件循环实例"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
