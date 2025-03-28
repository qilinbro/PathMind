#!/usr/bin/env python
"""
手动测试脚本 - 测试智谱AI API集成
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.append(str(ROOT_DIR))

# 创建日志目录
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "zhipuai_test.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("zhipuai_test")

# 检查必要的模块是否已安装
try:
    from app.services.ai_service import AIService
    from app.core.config import settings
except ModuleNotFoundError as e:
    logger.error(f"导入错误: {e}")
    print(f"错误: 缺少必要的模块 - {e}")
    print("请运行 'python setup_test_env.py' 安装所需依赖")
    sys.exit(1)

async def test_direct_zhipuai_call():
    """直接测试智谱AI API调用"""
    logger.info("测试直接API调用...")
    ai_service = AIService(settings.ZHIPU_API_KEY)
    
    if not ai_service.client:
        logger.error("错误: 未配置ZhipuAI API密钥")
        return False
    
    try:
        # 直接使用客户端进行调用
        response = await asyncio.to_thread(
            ai_service.client.chat.completions.create,
            model="glm-4-plus",
            messages=[
                {"role": "user", "content": "请用一句话解释什么是个性化学习"}
            ]
        )
        
        logger.info("\n=== 直接API调用结果 ===")
        logger.info(f"响应状态: 成功")
        logger.info(f"模型: {response.model}")
        logger.info(f"回复内容:\n{response.choices[0].message.content}")
        logger.info("======================\n")
        return True
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")
        return False

async def test_learning_style_analysis():
    """测试学习风格分析"""
    logger.info("测试学习风格分析...")
    ai_service = AIService(settings.ZHIPU_API_KEY)
    
    # 测试数据
    responses = [
        {
            "question_id": 1,
            "question_text": "我喜欢通过图片和视频学习",
            "question_type": "scale",
            "category": "visual",
            "response_value": {"answer": "5"},
            "response_time": 2.5
        },
        {
            "question_id": 2,
            "question_text": "我更喜欢听讲座和录音",
            "question_type": "scale",
            "category": "auditory",
            "response_value": {"answer": "3"},
            "response_time": 3.1
        }
    ]
    
    try:
        result = await ai_service.analyze_learning_style(responses)
        logger.info("\n=== 学习风格分析结果 ===")
        logger.info(json.dumps(result, indent=2, ensure_ascii=False))
        logger.info("======================\n")
        return True
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        return False

async def test_mistake_analysis():
    """测试错误分析"""
    logger.info("测试错误分析...")
    ai_service = AIService(settings.ZHIPU_API_KEY)
    
    # 测试数据
    user_data = {
        "user_id": 1,
        "error_records": [
            {
                "topic": "循环控制",
                "error_type": "边界条件",
                "frequency": 5,
                "examples": ["数组索引越界", "循环终止条件错误"]
            },
            {
                "topic": "函数调用",
                "error_type": "参数错误",
                "frequency": 3,
                "examples": ["参数数量不匹配", "参数类型错误"]
            }
        ],
        "quiz_answers": {
            "基础编程": {"correct": 8, "incorrect": 2}
        }
    }
    
    try:
        result = await ai_service.analyze_mistakes(user_data)
        logger.info("\n=== 错误分析结果 ===")
        logger.info(json.dumps(result, indent=2, ensure_ascii=False))
        logger.info("======================\n")
        return True
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        return False

async def test_adaptive_test_generation():
    """测试自适应测试生成"""
    logger.info("测试自适应测试生成...")
    ai_service = AIService(settings.ZHIPU_API_KEY)
    
    # 测试数据
    test_request = {
        "user_id": 1,
        "subject": "编程",
        "topic": "Python基础",
        "difficulty": "medium"
    }
    
    try:
        result = await ai_service.generate_adaptive_test(test_request)
        logger.info("\n=== 自适应测试生成结果 ===")
        logger.info(json.dumps(result, indent=2, ensure_ascii=False))
        logger.info("======================\n")
        return True
    except Exception as e:
        logger.error(f"生成失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("=" * 50)
    print("智谱AI测试脚本")
    print("=" * 50)
    print(f"API密钥状态: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
    
    if not settings.ZHIPU_API_KEY:
        print("错误: 未配置ZhipuAI API密钥，无法进行测试")
        return
    
    tests = [
        (test_direct_zhipuai_call, "直接API调用"),
        (test_learning_style_analysis, "学习风格分析"),
        (test_mistake_analysis, "错误分析"),
        (test_adaptive_test_generation, "自适应测试生成")
    ]
    
    results = []
    for test_func, name in tests:
        print(f"\n运行测试: {name}")
        success = await test_func()
        results.append((name, success))
        if success:
            print(f"✅ {name}测试成功")
        else:
            print(f"❌ {name}测试失败")
    
    print("\n" + "=" * 50)
    print("测试结果摘要:")
    print("=" * 50)
    for name, success in results:
        status = "成功" if success else "失败"
        print(f"{name:<15}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n总计: {success_count}/{len(results)} 成功")
    print("=" * 50)
    
    # 保存日志路径
    log_path = LOG_DIR / "zhipuai_test.log"
    print(f"\n详细日志已保存至: {log_path}")

if __name__ == "__main__":
    asyncio.run(main())
