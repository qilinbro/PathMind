import gradio as gr
import logging
import os
import asyncio
import json
from pathlib import Path

# 导入自定义模块
from api_service import ApiService, check_api_status
from pages import (
    create_dashboard_tab, 
    create_assessment_tab, 
    create_learning_paths_tab,
    create_content_viewer_tab,
    create_adaptive_test_tab,
    create_analytics_tab
)
# 添加学习路径页面的导入
from pages.learning_path import create_learning_path_tab
from utils import format_api_status_html

# 添加调试工具导入
from utils.debug_tools import create_debug_entry_point
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gradio_front2.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("app")

# 全局设置
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
DEFAULT_USER_ID = int(os.environ.get("DEFAULT_USER_ID", 1))

# 创建API服务实例
api_service = ApiService(API_BASE_URL)

def create_app():
    """创建Gradio应用程序"""
    
    # 创建调试函数
    debug_api_endpoint = create_debug_entry_point(api_service)
    
    with gr.Blocks(title="学习路径平台", theme=gr.themes.Soft(), css="""
        .warning-box {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .backend-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-normal { background-color: #198754; }
        .status-partial { background-color: #ffc107; }
        .status-error { background-color: #dc3545; }
        .detail-view {
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
        }
    """) as app:
        gr.Markdown("# 学习路径平台")
        
        # 开发模式警告
        gr.HTML("""
        <div class="warning-box">
            <strong>⚠️ 开发模式</strong> - 这是简化版WebUI，部分功能使用测试数据
        </div>
        """)
        
        # API状态指示器
        with gr.Row():
            api_status = gr.HTML(
                value="<div>正在检查API状态...</div>",
                label="API状态"
            )
            check_api_btn = gr.Button("检查API状态", variant="secondary", size="sm")
            debug_btn = gr.Button("显示测试数据", variant="secondary", size="sm")
            execute_test_btn = gr.Button("运行测试流程", variant="secondary", size="sm")
        
        # 调试面板 (默认隐藏)
        debug_panel = gr.JSON(
            value={},
            label="调试信息",
            visible=False
        )
        
        # 增强调试面板功能
        debug_container = gr.Group(visible=False)
        with debug_container:
            gr.Markdown("### 高级调试工具")
            with gr.Row():
                with gr.Column():
                    debug_endpoint = gr.Textbox(label="API端点", value="assessment/adaptive-test")
                    debug_method = gr.Radio(
                        label="请求方法", 
                        choices=["GET", "POST"], 
                        value="POST"
                    )
                    debug_data = gr.Textbox(
                        label="请求数据 (JSON)", 
                        value="""{"user_id": 1, "subject": "programming", "topic": "Python基础", "difficulty": "auto"}""",
                        lines=5
                    )
                with gr.Column():
                    debug_btn = gr.Button("发送调试请求", variant="primary")
                    debug_result = gr.JSON(label="调试结果")
                    debug_timestamp = gr.Textbox(label="调试时间戳", value="")
        
        # 添加一个特定的端点测试区域
        endpoint_test_container = gr.Group(visible=False)
        with endpoint_test_container:
            gr.Markdown("### API端点测试")
            endpoint_url = gr.Textbox(label="API端点", value="assessment/adaptive-test")
            endpoint_method = gr.Radio(
                label="请求方法", 
                choices=["GET", "POST"], 
                value="POST"
            )
            endpoint_data = gr.Textbox(
                label="请求数据 (JSON)", 
                value="""{"user_id": 1, "subject": "programming", "topic": "Python基础", "difficulty": "auto"}""",
                lines=5
            )
            test_endpoint_btn = gr.Button("测试端点", variant="primary")
            endpoint_result = gr.JSON(label="响应结果")
        
        # 创建标签页
        with gr.Tabs() as tabs:
            with gr.TabItem("仪表盘"):
                dashboard_components = create_dashboard_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习风格评估"):
                # 接收新的返回组件
                assessment_result, style_chart, learning_style_result, recommendations = create_assessment_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习路径"):
                paths_components = create_learning_paths_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习内容"):
                content_components = create_content_viewer_tab(api_service, DEFAULT_USER_ID)
            
            # 添加新标签页
            with gr.TabItem("自适应测试"):
                test_result, test_container = create_adaptive_test_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习分析"):
                behavior_result, weaknesses_result, progress_result = create_analytics_tab(api_service, DEFAULT_USER_ID)
            
            # 添加可视化学习路径标签页
            with gr.TabItem("学习路径可视化"):
                learning_path_container = create_learning_path_tab(api_service, DEFAULT_USER_ID)
        
        # 检查API状态事件处理
        def update_api_status():
            """更新API状态显示"""
            try:
                status_info = check_api_status(api_service)
                html_status = format_api_status_html(status_info)
                
                # 如果API根检测到有效URL，更新API基础URL
                if "details" in status_info and "API根" in status_info["details"]:
                    api_root = status_info["details"]["API根"]
                    if api_root.get("ok") and "url" in api_root:
                        logger.info(f"API根有效，使用URL: {api_root['url']}")
                
                return html_status
            except Exception as e:
                logger.error(f"更新API状态出错: {str(e)}")
                return f"<div>API状态更新失败: {str(e)}</div>"
        
        # 绑定API状态按钮事件
        check_api_btn.click(
            fn=update_api_status,
            outputs=[api_status]
        )
        
        # 增强调试面板逻辑
        def toggle_debug_panel():
            # 收集测试数据
            test_data = {
                "assessment_questions": api_service._get_test_assessment_questions(),
                "enrolled_paths": api_service._get_test_enrolled_paths(),
                "recommended_paths": api_service._get_test_recommended_paths(),
                "path_details": api_service._get_test_path_details(1),
                "content": api_service._get_test_content(1)
            }
            # 显示调试面板和调试容器
            return gr.update(value=test_data, visible=True), gr.update(visible=True)
        
        debug_btn.click(
            fn=toggle_debug_panel,
            outputs=[debug_panel, debug_container]
        )
        
        # 添加API端点测试功能
        def test_endpoint(url, method, data_str):
            try:
                # 解析JSON数据
                data = json.loads(data_str) if data_str.strip() else None
                
                # 调用API
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(
                    api_service.request(method, url, data=data)
                )
                loop.close()
                
                return result
            except Exception as e:
                return {"error": f"测试端点失败: {str(e)}"}
        
        test_endpoint_btn.click(
            fn=test_endpoint,
            inputs=[endpoint_url, endpoint_method, endpoint_data],
            outputs=[endpoint_result]
        )
        
        # 添加高级调试功能
        async def run_debug_request(endpoint, method, data_str):
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = await debug_api_endpoint(endpoint, method, data_str)
                return result, timestamp
            except Exception as e:
                return {"error": f"调试请求异常: {str(e)}"}, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 绑定高级调试按钮
        debug_btn.click(
            fn=run_debug_request,
            inputs=[debug_endpoint, debug_method, debug_data],
            outputs=[debug_result, debug_timestamp]
        )
        
        # 运行测试流程 - 使用test_full_flow.py中的格式
        def execute_test_flow():
            try:
                import asyncio
                
                # 创建和设置事件循环
                loop = asyncio.new_event_loop()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 步骤1: 检查API健康状态 - 修正URL
                logger.info("测试步骤1: 检查API健康状态")
                health_result = loop.run_until_complete(
                    api_service.request("GET", "health", timeout=5.0)  # 不需要修改，因为我们已修改了request方法
                )
                if "error" in health_result:
                    loop.close()
                    return f"API健康检查失败: {health_result['error']}"
                logger.info("API健康状态正常")
                
                # 步骤2: 获取评估问题
                logger.info("测试步骤2: 获取评估问题")
                questions_result = loop.run_until_complete(
                    api_service.request("GET", "assessment/questions")
                )
                if "error" in questions_result:
                    logger.warning(f"获取评估问题失败: {questions_result['error']}")
                else:
                    logger.info(f"获取到 {len(questions_result) if isinstance(questions_result, list) else '未知数量'} 个评估问题")
                
                # 步骤3: 提交学习风格评估
                logger.info("测试步骤3: 提交学习风格评估")
                assessment_result = loop.run_until_complete(
                    api_service.request("POST", "assessment/submit", data={
                        "user_id": DEFAULT_USER_ID,
                        "responses": [
                            {"question_id": 1, "response_value": {"answer": "5"}, "response_time": 3.5},
                            {"question_id": 2, "response_value": {"answer": "3"}, "response_time": 4.2},
                            {"question_id": 3, "response_value": {"answer": "4"}, "response_time": 2.8},
                            {"question_id": 4, "response_value": {"answer": "2"}, "response_time": 5.0}
                        ]
                    })
                )
                
                if "error" in assessment_result:
                    logger.error(f"评估提交失败: {assessment_result['error']}")
                    # 继续测试，评估失败不中断整个流程
                else:
                    logger.info("评估提交成功")
                    # 记录评估结果
                    if "learning_style_result" in assessment_result:
                        ls = assessment_result["learning_style_result"]
                        logger.info(f"学习风格: 视觉={ls.get('visual')}%, 听觉={ls.get('auditory')}%, 动觉={ls.get('kinesthetic')}%, 阅读={ls.get('reading')}%")
                
                # 步骤4: 创建学习路径
                logger.info("测试步骤4: 创建学习路径")
                path_result = loop.run_until_complete(
                    api_service.request("POST", "learning-paths", data={
                        "title": "Python编程基础路径",
                        "description": "从零开始学习Python编程的个性化路径",
                        "subject": "programming",
                        "difficulty_level": 2,
                        "estimated_hours": 25,
                        "goals": ["掌握Python基础语法", "能够编写简单的Python程序", "理解面向对象编程概念"],
                        "difficulty": "beginner",
                        "created_by": DEFAULT_USER_ID
                    })
                )
                
                if "error" in path_result:
                    logger.error(f"学习路径创建失败: {path_result['error']}")
                    loop.close()
                    return f"学习路径创建失败: {path_result['error']}"
                
                path_id = path_result.get("id")
                if not path_id:
                    logger.warning("学习路径创建成功，但未返回ID，使用默认ID=1")
                    path_id = 1
                else:
                    logger.info(f"学习路径创建成功，ID: {path_id}")
                
                # 步骤5: 注册学习路径
                logger.info(f"测试步骤5: 注册学习路径 (ID: {path_id})")
                enroll_result = loop.run_until_complete(
                    api_service.request("POST", "learning-paths/enroll", data={
                        "user_id": DEFAULT_USER_ID,
                        "path_id": path_id,
                        "personalization_settings": {
                            "preferred_content_types": ["video", "interactive"],
                            "study_reminder": True
                        }
                    })
                )
                
                loop.close()
                
                if "error" in enroll_result:
                    logger.error(f"注册学习路径失败: {enroll_result['error']}")
                    return f"注册学习路径失败: {enroll_result['error']}"
                
                logger.info("学习路径注册成功")
                
                # 返回完整测试结果
                success_msg = f"测试流程执行成功！\n"
                success_msg += f"评估已提交，学习路径(ID:{path_id})已创建并注册。\n"
                success_msg += "请刷新仪表盘查看结果。"
                
                return success_msg
                    
            except Exception as e:
                import traceback
                logger.error(f"测试流程执行异常: {str(e)}")
                logger.error(traceback.format_exc())
                return f"测试流程执行异常: {str(e)}"
        
        execute_test_btn.click(
            fn=execute_test_flow,
            outputs=[api_status]
        )
        
        # 初始化API状态
        api_status.value = update_api_status()
                
    return app

# 创建并启动应用程序
if __name__ == "__main__":
    app = create_app()
    app.launch(server_port=3000, share=False)
