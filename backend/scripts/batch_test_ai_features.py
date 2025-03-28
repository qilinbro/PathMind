#!/usr/bin/env python
"""
批量测试脚本 - 测试所有AI功能
此脚本会测试所有依赖智谱AI的功能，并生成测试报告
"""
import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.append(str(ROOT_DIR))

# 创建报告目录
REPORT_DIR = ROOT_DIR / "tests" / "reports"
REPORT_DIR.mkdir(exist_ok=True, parents=True)

# 检查必要的模块是否已安装
try:
    from app.services.ai_service import AIService
    from app.core.config import settings
except ModuleNotFoundError as e:
    print(f"错误: 缺少必要的模块 - {e}")
    print("请运行 'python setup_test_env.py' 安装所需依赖")
    sys.exit(1)

# 测试用例列表
TEST_CASES = [
    {
        "name": "学习风格分析",
        "function": "analyze_learning_style",
        "data": [
            {
                "question_id": 1,
                "question_text": "我喜欢通过图表和图像学习",
                "category": "visual",
                "response_value": {"answer": "4"}
            },
            {
                "question_id": 2,
                "question_text": "我更喜欢听讲座而不是阅读",
                "category": "auditory",
                "response_value": {"answer": "3"}
            },
            {
                "question_id": 3,
                "question_text": "我喜欢动手实践",
                "category": "kinesthetic",
                "response_value": {"answer": "5"}
            },
            {
                "question_id": 4,
                "question_text": "我喜欢通过阅读材料学习",
                "category": "reading",
                "response_value": {"answer": "2"}
            }
        ]
    },
    {
        "name": "学习行为分析",
        "function": "generate_learning_analysis",
        "data": {
            "user_id": 1,
            "study_time": 45,
            "completion_rate": 75,
            "interactions": 10,
            "content_types": ["video", "article", "quiz"]
        }
    },
    {
        "name": "内容推荐",
        "function": "generate_content_recommendations",
        "data": {
            "user_id": 1,
            "subject": "programming",
            "limit": 3
        }
    },
    {
        "name": "弱点分析",
        "function": "identify_weaknesses",
        "data": {
            "user_id": 1,
            "learning_records": [
                {"topic": "数据结构", "score": 65, "time_spent": 120},
                {"topic": "算法", "score": 60, "time_spent": 90},
                {"topic": "编程基础", "score": 90, "time_spent": 150}
            ],
            "quiz_scores": {
                "数据结构": [65, 70, 62],
                "算法": [60, 55, 65],
                "编程基础": [90, 95, 85]
            }
        }
    },
    {
        "name": "错误分析",
        "function": "analyze_mistakes",
        "data": {
            "user_id": 1,
            "error_records": [
                {"topic": "循环", "error_type": "边界条件", "frequency": 5},
                {"topic": "变量", "error_type": "未初始化", "frequency": 3}
            ],
            "quiz_answers": {
                "编程基础": {"correct": 8, "incorrect": 2}
            }
        }
    },
    {
        "name": "自适应测试生成",
        "function": "generate_adaptive_test",
        "data": {
            "user_id": 1,
            "subject": "计算机科学",
            "topic": "算法",
            "difficulty": "medium"
        }
    }
]

async def run_test_case(ai_service, test_case):
    """运行单个测试用例"""
    name = test_case["name"]
    function_name = test_case["function"]
    data = test_case["data"]
    
    print(f"测试 {name}...")
    start_time = time.time()
    
    try:
        # 获取要调用的函数
        function = getattr(ai_service, function_name)
        
        # 调用函数并传递参数
        if function_name == "generate_content_recommendations":
            result = await function(
                user_id=data["user_id"],
                subject=data.get("subject"),
                limit=data.get("limit", 3)
            )
        else:
            result = await function(data)
        
        duration = time.time() - start_time
        
        return {
            "name": name,
            "status": "成功",
            "duration": f"{duration:.2f}秒",
            "result": result
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "name": name,
            "status": "失败",
            "duration": f"{duration:.2f}秒",
            "error": str(e)
        }

async def run_batch_tests():
    """运行所有测试用例"""
    if not settings.ZHIPU_API_KEY:
        print("错误: 未配置ZhipuAI API密钥，无法进行测试")
        return
    
    # 确保zhipuai模块已安装
    try:
        from zhipuai import ZhipuAI
    except ModuleNotFoundError:
        print("错误: 未安装zhipuai模块")
        print("请运行 'python -m pip install zhipuai' 安装")
        return
    
    ai_service = AIService(settings.ZHIPU_API_KEY)
    results = []
    
    # 测试开始时间
    start_time = time.time()
    print(f"开始批量测试，共{len(TEST_CASES)}个测试用例...")
    
    # 依次运行所有测试用例
    for test_case in TEST_CASES:
        result = await run_test_case(ai_service, test_case)
        results.append(result)
    
    # 测试结束时间
    total_duration = time.time() - start_time
    
    # 生成测试报告
    success_count = sum(1 for r in results if r["status"] == "成功")
    report = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "api_key_configured": bool(settings.ZHIPU_API_KEY),
        "total_tests": len(TEST_CASES),
        "successful_tests": success_count,
        "failed_tests": len(TEST_CASES) - success_count,
        "total_duration": f"{total_duration:.2f}秒",
        "results": results
    }
    
    # 将报告保存到文件
    report_file = REPORT_DIR / f"ai_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成! {success_count}/{len(TEST_CASES)} 测试用例成功")
    print(f"测试报告已保存到: {report_file}")
    
    # 输出结果摘要
    print("\n测试结果摘要:")
    print("-" * 50)
    print(f"{'测试名称':<20} {'状态':<10} {'耗时':<10}")
    print("-" * 50)
    for r in results:
        print(f"{r['name']:<20} {r['status']:<10} {r['duration']:<10}")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_batch_tests())
