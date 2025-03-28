import pytest
import json
from typing import Dict, List, Any
import asyncio
import logging

from app.services.ai_service import AIService
from app.core.config import settings
from conftest import skip_if_no_api_key

# 设置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试数据
test_user_responses = [
    {
        "question_id": 1,
        "question_text": "我更喜欢通过图表和视觉辅助工具来学习",
        "question_type": "scale",
        "category": "visual",
        "response_value": {"answer": "5"},
        "response_time": 3.5
    },
    {
        "question_id": 2,
        "question_text": "听讲座和讨论是我最有效的学习方式",
        "question_type": "scale",
        "category": "auditory",
        "response_value": {"answer": "3"},
        "response_time": 4.2
    },
    {
        "question_id": 3,
        "question_text": "我喜欢通过实际操作来学习新事物",
        "question_type": "scale",
        "category": "kinesthetic",
        "response_value": {"answer": "4"},
        "response_time": 2.8
    }
]

test_user_learning_data = {
    "user_id": 1,
    "study_time": 45.5,
    "completion_rate": 72.5,
    "interactions": 12,
    "content_types": ["video", "interactive", "article"]
}

test_user_weakness_data = {
    "user_id": 1,
    "learning_records": [
        {"topic": "数据结构", "score": 65, "time_spent": 120},
        {"topic": "算法", "score": 58, "time_spent": 90},
        {"topic": "编程基础", "score": 92, "time_spent": 150}
    ],
    "quiz_scores": {
        "数据结构": [65, 70, 62],
        "算法": [60, 55, 65],
        "编程基础": [90, 95, 85]
    }
}

test_adaptive_test_request = {
    "user_id": 1,
    "subject": "计算机科学",
    "topic": "数据结构",
    "difficulty": "medium"
}

@skip_if_no_api_key
@pytest.mark.asyncio
async def test_analyze_learning_style(ai_service):
    """测试学习风格分析功能"""
    logger.info("测试学习风格分析...")
    
    try:
        # 调用学习风格分析功能
        result = await ai_service.analyze_learning_style(test_user_responses)
        
        # 验证结果
        assert "visual_score" in result
        assert "auditory_score" in result
        assert "kinesthetic_score" in result
        assert "reading_score" in result
        assert "dominant_style" in result
        
        # 打印结果
        logger.info(f"学习风格分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"学习风格分析失败: {str(e)}")
        pytest.fail(f"测试失败: {str(e)}")
        return False

@skip_if_no_api_key
@pytest.mark.asyncio
async def test_generate_learning_analysis(ai_service):
    """测试学习行为分析功能"""
    logger.info("测试学习行为分析...")
    
    try:
        # 调用学习行为分析功能
        result = await ai_service.generate_learning_analysis(test_user_learning_data)
        
        # 验证结果
        assert "behavior_patterns" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "recommendations" in result
        
        # 打印结果
        logger.info(f"学习行为分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"学习行为分析失败: {str(e)}")
        pytest.fail(f"测试失败: {str(e)}")
        return False

@skip_if_no_api_key
@pytest.mark.asyncio
async def test_generate_content_recommendations(ai_service):
    """测试内容推荐功能"""
    logger.info("测试内容推荐...")
    
    try:
        # 调用内容推荐功能
        result = await ai_service.generate_content_recommendations(
            user_id=1,
            subject="计算机科学",
            limit=2
        )
        
        # 验证结果
        assert len(result) > 0
        for rec in result:
            assert "content" in rec
            assert "explanation" in rec
            assert "approach_suggestion" in rec
        
        # 打印结果
        logger.info(f"内容推荐结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"内容推荐失败: {str(e)}")
        pytest.fail(f"测试失败: {str(e)}")
        return False

@skip_if_no_api_key
@pytest.mark.asyncio
async def test_identify_weaknesses(ai_service):
    """测试学习弱点识别功能"""
    logger.info("测试学习弱点识别...")
    
    try:
        # 调用弱点识别功能
        result = await ai_service.identify_weaknesses(test_user_weakness_data)
        
        # 验证结果
        assert "weak_areas" in result
        assert "strength_areas" in result
        assert "improvement_plan" in result
        
        # 打印结果
        logger.info(f"学习弱点分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"学习弱点识别失败: {str(e)}")
        pytest.fail(f"测试失败: {str(e)}")
        return False

@skip_if_no_api_key
@pytest.mark.asyncio
async def test_generate_adaptive_test(ai_service):
    """测试自适应测试生成功能"""
    logger.info("测试自适应测试生成...")
    
    try:
        # 调用自适应测试生成功能
        result = await ai_service.generate_adaptive_test(test_adaptive_test_request)
        
        # 验证结果
        assert "questions" in result
        assert "adaptive_logic" in result
        assert "estimated_difficulty" in result
        
        # 打印结果
        logger.info(f"自适应测试生成结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"自适应测试生成失败: {str(e)}")
        pytest.fail(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("直接运行测试文件...")
    print(f"API密钥状态: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
    
    if not settings.ZHIPU_API_KEY:
        print("警告: ZhipuAI API密钥未配置，测试将使用模拟数据")
    
    async def run_all_tests():
        service = AIService(settings.ZHIPU_API_KEY)
        tests = [
            (test_analyze_learning_style, "学习风格分析"),
            (test_generate_learning_analysis, "学习行为分析"),
            (test_generate_content_recommendations, "内容推荐"),
            (test_identify_weaknesses, "弱点识别"),
            (test_generate_adaptive_test, "自适应测试生成")
        ]
        
        results = []
        for test_func, name in tests:
            print(f"\n运行测试: {name}")
            try:
                await test_func(service)
                print(f"✅ {name}测试成功")
                results.append(True)
            except Exception as e:
                print(f"❌ {name}测试失败: {str(e)}")
                results.append(False)
        
        success = sum(results)
        total = len(results)
        print(f"\n测试完成: {success}/{total} 成功, {total-success}/{total} 失败")
    
    asyncio.run(run_all_tests())
