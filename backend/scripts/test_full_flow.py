#!/usr/bin/env python
"""
全流程测试脚本 - 测试学习路径平台的完整用户流程
从学习风格评估到路径生成、注册和进度追踪
"""
import os
import sys
import json
import time
import asyncio
import httpx
import logging
import traceback
from pathlib import Path
from datetime import datetime

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
        logging.FileHandler(LOG_DIR / "full_flow_test.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("full_flow_test")

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用户数据
TEST_USER = {
    "id": 1,  # 假设这是我们的测试用户ID
    "full_name": "测试用户"
}

# 测试用的评估回答
TEST_ASSESSMENT = {
    "user_id": TEST_USER["id"],
    "responses": [
        {
            "question_id": 1,
            "response_value": {"answer": "5"},  # 强烈视觉偏好
            "response_time": 3.5
        },
        {
            "question_id": 2,
            "response_value": {"answer": "3"},  # 中等听觉偏好
            "response_time": 4.2
        },
        {
            "question_id": 3,
            "response_value": {"answer": "4"},  # 较高动觉偏好
            "response_time": 2.8
        },
        {
            "question_id": 4,
            "response_value": {"answer": "2"},  # 较低阅读偏好
            "response_time": 5.0
        }
    ]
}

# 学习路径创建请求
LEARNING_PATH_REQUEST = {
    "title": "Python编程基础路径",
    "description": "从零开始学习Python编程的个性化路径",
    "subject": "programming",
    "difficulty_level": 2,
    "estimated_hours": 25,
    "goals": ["掌握Python基础语法", "能够编写简单的Python程序", "理解面向对象编程概念"],
    "difficulty": "beginner",
    "created_by": TEST_USER["id"]
}

# 学习行为数据
LEARNING_BEHAVIOR_DATA = {
    "user_id": TEST_USER["id"],
    "content_interactions": [
        {
            "content_id": 1,
            "time_spent": 1200,  # 20分钟
            "interaction_type": "video",
            "progress": 0.8,  # 80%完成率
            "engagement_metrics": {
                "pauses": 3,
                "rewinds": 2,
                "notes_taken": True
            }
        },
        {
            "content_id": 2,
            "time_spent": 1800,  # 30分钟
            "interaction_type": "interactive",
            "progress": 0.9,  # 90%完成率
            "engagement_metrics": {
                "pauses": 1,
                "rewinds": 0,
                "notes_taken": True
            }
        }
    ]
}

async def step_1_check_server_health():
    """步骤1: 检查服务器健康状态"""
    logger.info("开始步骤1: 检查服务器健康状态")
    try:
        # 增加超时参数
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info("正在连接服务器...")
            response = await client.get("http://localhost:8000/health")
            response.raise_for_status()
            logger.info(f"服务器状态: {response.json()}")
            return True
    except httpx.ConnectError:
        logger.error("无法连接到服务器，请确保服务器已启动")
        logger.error("启动命令: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except httpx.HTTPStatusError as e:
        logger.error(f"服务器返回错误状态码: {e.response.status_code}")
        logger.error(f"错误详情: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"服务器健康检查失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def step_2_learning_style_assessment():
    """步骤2: 完成学习风格评估"""
    logger.info("开始步骤2: 完成学习风格评估")
    try:
        async with httpx.AsyncClient() as client:
            # 移除URL尾部斜杠
            response = await client.post(
                f"{BASE_URL}/assessment/submit", 
                json=TEST_ASSESSMENT
            )
            response.raise_for_status()
            result = response.json()
            logger.info("学习风格评估完成")
            logger.info(f"评估结果: {json.dumps(result['learning_style_result'], indent=2, ensure_ascii=False)}")
            logger.info(f"收到 {len(result['recommendations'])} 条推荐内容")
            return result
    except Exception as e:
        logger.error(f"学习风格评估失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_3_generate_learning_path():
    """步骤3: 生成个性化学习路径"""
    logger.info("开始步骤3: 生成个性化学习路径")
    try:
        async with httpx.AsyncClient() as client:
            # 移除URL尾部斜杠 
            response = await client.post(
                f"{BASE_URL}/learning-paths", # 修改这里: 删除尾部斜杠
                json=LEARNING_PATH_REQUEST
            )
            response.raise_for_status()
            path = response.json()
            logger.info(f"成功创建学习路径: {path['title']}")
            logger.info(f"路径ID: {path['id']}")
            logger.info(f"难度级别: {path['difficulty_level']}")
            logger.info(f"估计学习时间: {path['estimated_hours']} 小时")
            return path
    except Exception as e:
        logger.error(f"生成学习路径失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_4_enroll_in_path(path_id):
    """步骤4: 注册学习路径"""
    logger.info(f"开始步骤4: 注册学习路径 (ID: {path_id})")
    try:
        enrollment_data = {
            "user_id": TEST_USER["id"],
            "path_id": path_id,
            "personalization_settings": {
                "preferred_content_types": ["video", "interactive"],
                "study_reminder": True
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/learning-paths/enroll", 
                json=enrollment_data
            )
            response.raise_for_status()
            enrollment = response.json()
            logger.info(f"成功注册学习路径")
            logger.info(f"注册ID: {enrollment['id']}")
            logger.info(f"当前进度: {enrollment['progress']}%")
            return enrollment
    except Exception as e:
        logger.error(f"注册学习路径失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_5_view_path_details(path_id):
    """步骤5: 查看学习路径详细信息"""
    logger.info(f"开始步骤5: 查看学习路径详情 (ID: {path_id})")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/learning-paths/{path_id}?user_id={TEST_USER['id']}"
            )
            response.raise_for_status()
            path_details = response.json()
            logger.info(f"获取到学习路径详情: {path_details['title']}")
            logger.info(f"包含 {len(path_details['contents'])} 个学习内容")
            # 打印内容列表
            for i, content in enumerate(path_details['contents']):
                logger.info(f"  内容 {i+1}: {content['title']} (ID: {content['id']})")
            return path_details
    except Exception as e:
        logger.error(f"获取学习路径详情失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_6_update_learning_progress(path_id):
    """步骤6: 更新学习进度"""
    logger.info(f"开始步骤6: 更新学习进度 (路径ID: {path_id})")
    try:
        # 假设我们更新了第一个内容的进度
        progress_data = {
            "content_id": 1,  # 这里需要使用实际的内容ID
            "progress": 75.0   # 75%
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/learning-paths/{path_id}/progress?user_id={TEST_USER['id']}", 
                json=progress_data
            )
            response.raise_for_status()
            updated_enrollment = response.json()
            logger.info(f"成功更新学习进度")
            logger.info(f"当前总进度: {updated_enrollment['progress']}%")
            logger.info(f"内容进度详情: {json.dumps(updated_enrollment['content_progress'], indent=2)}")
            return updated_enrollment
    except Exception as e:
        logger.error(f"更新学习进度失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_7_analyze_learning_behavior():
    """步骤7: 分析学习行为"""
    logger.info("开始步骤7: 分析学习行为")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/analytics/behavior", 
                json=LEARNING_BEHAVIOR_DATA
            )
            response.raise_for_status()
            analysis = response.json()
            logger.info("成功获取学习行为分析")
            logger.info(f"参与度: {analysis['engagement_level']}")
            logger.info(f"行为模式: {json.dumps(analysis['behavior_patterns'], indent=2, ensure_ascii=False)}")
            logger.info(f"改进建议: {json.dumps(analysis['improvement_areas'], indent=2, ensure_ascii=False)}")
            return analysis
    except Exception as e:
        logger.error(f"分析学习行为失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_8_identify_weaknesses():
    """步骤8: 识别学习弱点"""
    logger.info("开始步骤8: 识别学习弱点")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/analytics/weaknesses/{TEST_USER['id']}"
            )
            response.raise_for_status()
            weaknesses = response.json()
            logger.info("成功获取学习弱点分析")
            logger.info(f"弱点领域: {len(weaknesses['weak_areas'])} 个")
            for area in weaknesses['weak_areas']:
                logger.info(f"  - {area['topic']} (信心水平: {area['confidence_level']})")
                logger.info(f"    推荐资源: {len(area['suggested_resources'])} 个")
            logger.info(f"优势领域: {len(weaknesses['strength_areas'])} 个")
            logger.info(f"改进计划: {json.dumps(weaknesses['improvement_plan'], indent=2, ensure_ascii=False)}")
            return weaknesses
    except Exception as e:
        logger.error(f"识别学习弱点失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_9_get_learning_progress():
    """步骤9: 获取学习进度"""
    logger.info("开始步骤9: 获取学习进度")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/assessment/progress/{TEST_USER['id']}"
            )
            response.raise_for_status()
            progress = response.json()
            logger.info("成功获取学习进度")
            logger.info(f"当前学习风格: {json.dumps(progress['current_learning_style'], indent=2, ensure_ascii=False)}")
            logger.info(f"进度指标: {json.dumps(progress['progress_metrics'], indent=2, ensure_ascii=False)}")
            logger.info(f"改进建议: {json.dumps(progress['improvement_suggestions'], indent=2, ensure_ascii=False)}")
            return progress
    except Exception as e:
        logger.error(f"获取学习进度失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def step_10_generate_adaptive_test():
    """步骤10: 生成自适应测试"""
    logger.info("开始步骤10: 生成自适应测试")
    try:
        test_request = {
            "user_id": TEST_USER["id"],
            "subject": "programming",
            "topic": "Python基础",
            "difficulty": "auto"
        }
        # 增加较长的超时时间 - 30秒
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/assessment/adaptive-test", 
                json=test_request
            )
            response.raise_for_status()
            test = response.json()
            logger.info("成功生成自适应测试")
            logger.info(f"问题数量: {len(test['questions'])}")
            logger.info(f"估计难度: {test['estimated_difficulty']}")
            # 显示部分问题
            for i, q in enumerate(test['questions']):
                if i < 3:  # 只显示前3个问题
                    logger.info(f"  问题 {i+1}: {q['content']}")
                    logger.info(f"    难度: {q['difficulty']}, 主题: {q['topic']}")
            return test
    except Exception as e:
        logger.error(f"生成自适应测试失败: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def setup_test_content():
    """设置测试学习内容"""
    logger.info("设置测试学习内容...")
    
    content_items = [
        {
            "title": "Python基础语法",
            "description": "学习Python编程的基础语法和概念",
            "content_type": "video",
            "subject": "programming",
            "difficulty_level": 1,
            "content_data": {
                "url": "https://example.com/python-basics",
                "duration": 3600
            },
            "visual_affinity": 70,
            "auditory_affinity": 50,
            "kinesthetic_affinity": 30,
            "reading_affinity": 60,
            "tags": ["python", "beginner"]
        },
        {
            "title": "Python函数编程",
            "description": "学习如何在Python中定义和使用函数",
            "content_type": "interactive",
            "subject": "programming",
            "difficulty_level": 2,
            "content_data": {
                "url": "https://example.com/python-functions",
                "exercises": 5
            },
            "visual_affinity": 50,
            "auditory_affinity": 30,
            "kinesthetic_affinity": 80,
            "reading_affinity": 50,
            "tags": ["python", "functions", "intermediate"]
        }
    ]
    
    content_ids = []
    async with httpx.AsyncClient() as client:
        for content in content_items:
            try:
                # 移除URL尾部斜杠
                response = await client.post(f"{BASE_URL}/content", json=content)
                if response.status_code == 200:
                    content_id = response.json()["id"]
                    content_ids.append(content_id)
                    logger.info(f"创建内容成功，ID: {content_id}")
                else:
                    logger.warning(f"创建内容失败: {response.text}")
            except Exception as e:
                logger.error(f"创建内容出错: {str(e)}")
                logger.error(traceback.format_exc())
    return content_ids

async def run_complete_flow():
    """运行完整流程测试"""
    logger.info("=" * 50)
    logger.info("开始学习路径平台全流程测试")
    logger.info("=" * 50)
    
    all_results = {}
    
    # 步骤1: 检查服务器健康状态
    if not await step_1_check_server_health():
        logger.error("服务器健康检查失败，结束测试")
        return
    
    all_results["server_check"] = "成功"
    logger.info("\n")
    
    # 步骤2: 完成学习风格评估
    assessment_result = await step_2_learning_style_assessment()
    if not assessment_result:
        logger.error("学习风格评估失败，结束测试")
        return
    
    all_results["assessment"] = "成功"
    logger.info("\n")
    
    # 步骤3: 生成个性化学习路径
    path = await step_3_generate_learning_path()
    if not path:
        logger.error("生成学习路径失败，结束测试")
        return
    
    path_id = path["id"]
    all_results["learning_path"] = "成功"
    logger.info("\n")
    
    # 步骤4: 注册学习路径
    enrollment = await step_4_enroll_in_path(path_id)
    if not enrollment:
        logger.error("注册学习路径失败，结束测试")
        return
    
    all_results["enrollment"] = "成功"
    logger.info("\n")
    
    # 步骤5: 查看学习路径详细信息
    path_details = await step_5_view_path_details(path_id)
    if not path_details:
        logger.error("查看学习路径详情失败，结束测试")
        return
    
    all_results["path_details"] = "成功"
    logger.info("\n")
    
    # 获取第一个内容的ID用于更新进度
    first_content_id = path_details["contents"][0]["id"] if path_details.get("contents") else 1
    
    # 更新测试内容ID
    LEARNING_BEHAVIOR_DATA["content_interactions"][0]["content_id"] = first_content_id
    
    # 步骤6: 更新学习进度
    progress_data = {
        "content_id": first_content_id,
        "progress": 75.0
    }
    updated_enrollment = await step_6_update_learning_progress(path_id)
    if not updated_enrollment:
        logger.error("更新学习进度失败，结束测试")
        return
    
    all_results["progress_update"] = "成功"
    logger.info("\n")
    
    # 步骤7: 分析学习行为
    behavior_analysis = await step_7_analyze_learning_behavior()
    if not behavior_analysis:
        logger.error("分析学习行为失败，结束测试")
        return
    
    all_results["behavior_analysis"] = "成功"
    logger.info("\n")
    
    # 步骤8: 识别学习弱点
    weaknesses = await step_8_identify_weaknesses()
    if not weaknesses:
        logger.error("识别学习弱点失败，结束测试")
        return
    
    all_results["weaknesses"] = "成功"
    logger.info("\n")
    
    # 步骤9: 获取学习进度
    progress = await step_9_get_learning_progress()
    if not progress:
        logger.error("获取学习进度失败，结束测试")
        return
    
    all_results["learning_progress"] = "成功"
    logger.info("\n")
    
    # 步骤10: 生成自适应测试
    test = await step_10_generate_adaptive_test()
    if not test:
        logger.error("生成自适应测试失败，结束测试")
        return
    
    all_results["adaptive_test"] = "成功"
    logger.info("\n")
    
    # 最终保存测试结果
    results = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": all_results,
        "user_id": TEST_USER["id"]
        # ... [其他结果数据]
    }
    
    result_file = ROOT_DIR / "logs" / f"full_flow_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"测试结果已保存到: {result_file}")

# 添加简单的诊断函数
async def diagnose_server():
    """诊断服务器状态"""
    logger.info("执行服务器诊断...")
    
    endpoints = [
        "/health",
        "/api/v1/assessment/questions",  # 删除尾部斜杠，与API定义保持一致
        "/api/v1/content"                # 删除尾部斜杠，与API定义保持一致
    ]
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"http://localhost:8000{endpoint}"
                logger.info(f"测试端点: {url}")
                response = await client.get(url)
                status = "成功" if response.status_code < 400 else "失败"
                logger.info(f"状态码: {response.status_code} ({status})")
                if status == "成功":
                    logger.info(f"响应: {response.text[:100]}...")
                else:
                    logger.error(f"错误响应: {response.text}")
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")

if __name__ == "__main__":
    print("正在执行全流程测试...")
    
    try:
        # 首先执行诊断
        asyncio.run(diagnose_server())
        
        # 然后运行完整测试
        asyncio.run(run_complete_flow())
        print("测试完成! 查看日志获取详细信息。")
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试执行出错: {e}")
        traceback.print_exc()