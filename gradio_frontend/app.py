import gradio as gr
import logging
import os
import json
from services.api_service import ApiService
from components.assessment import create_assessment_tab
from components.learning_paths import create_learning_paths_tab
from components.content_viewer import create_content_viewer_tab
from components.dashboard import create_dashboard_tab

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gradio_frontend.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("app")

# 全局设置
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
DEFAULT_USER_ID = int(os.environ.get("DEFAULT_USER_ID", 1))  # 简化用户管理，实际应用中应实现登录功能

# 初始化API服务
api_service = ApiService(API_BASE_URL)

def check_api_status():
    """检查API服务状态"""
    try:
        # 使用诊断API功能
        api_info = api_service.diagnose_api()
        
        # 分析诊断结果
        available_endpoints = [name for name, info in api_info.items() if info["ok"]]
        unavailable_endpoints = [name for name, info in api_info.items() if not info["ok"]]
        
        # 获取API版本信息
        api_version = "未知"
        api_name = "学习路径API"
        if "API根" in api_info and api_info["API根"]["ok"]:
            api_data = api_info["API根"]["response"]
            api_version = api_data.get("version", "未知")
            api_name = api_data.get("message", "学习路径API").replace("Welcome to ", "").replace(" API", "")
            
        # 检查一些关键API端点，使用正确的格式
        key_endpoints = [
            # 使用简单端点确保API基础功能可用
            ("/assessment/questions", "评估问题"),
            ("/content", "内容列表"),
            # 使用正确的查询参数格式检查学习路径端点
            ("/learning-paths", "已注册路径", {"user_id": 1, "enrolled": "true"})
        ]
        
        failed_endpoints = []
        partial_endpoints = []
        
        for endpoint_info in key_endpoints:
            endpoint = endpoint_info[0]
            name = endpoint_info[1]
            params = endpoint_info[2] if len(endpoint_info) > 2 else None
            
            result = api_service._request("GET", endpoint, params=params)
            if "error" in result:
                # 区分404和其他错误
                if "404" in result["error"]:
                    partial_endpoints.append(f"{name} ({endpoint})")
                else:
                    failed_endpoints.append(f"{name} ({endpoint})")
        
        # 确定状态
        if len(unavailable_endpoints) == 0 and len(failed_endpoints) == 0:
            status = "正常"
            message = "所有API服务正常运行"
        elif "健康检查" in unavailable_endpoints or len(failed_endpoints) > 0:
            status = "不可用"
            message = "API服务不可用，请确保后端服务已启动"
        elif len(available_endpoints) >= 3 or len(partial_endpoints) > 0:  # 至少健康检查、API根、评估问题可用
            status = "部分可用"
            message = f"部分API端点可用，不可用端点: {', '.join(unavailable_endpoints + failed_endpoints)}"
        else:
            status = "严重受限"
            message = f"大部分API端点不可用，仅有: {', '.join(available_endpoints)}"
            
        return {
            "status": status,
            "message": message,
            "api_info": f"{api_name} {api_version}",
            "details": api_info
        }
    except Exception as e:
        logger.error(f"API状态检查异常: {str(e)}")
        return {
            "status": "错误",
            "message": f"API状态检查失败: {str(e)}"
        }

def create_app():
    """创建Gradio应用程序"""
    
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
            <strong>⚠️ 开发模式</strong> - 部分功能可能依赖测试数据，API尚未完全实现
        </div>
        """)
        
        # API状态指示器
        with gr.Row():
            api_status = gr.Textbox(
                label="API状态", 
                value="正在检查...",
                interactive=False
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
        
        # 创建标签页
        with gr.Tabs() as tabs:
            with gr.TabItem("仪表盘"):
                create_dashboard_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习风格评估"):
                create_assessment_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习路径"):
                create_learning_paths_tab(api_service, DEFAULT_USER_ID)
                
            with gr.TabItem("学习内容"):
                create_content_viewer_tab(api_service, DEFAULT_USER_ID)
        
        # 检查API状态事件处理
        def update_api_status():
            status = check_api_status()
            status_text = f"<div class='backend-status'>"
            if status["status"] == "正常":
                status_text += "<span class='status-indicator status-normal'></span>"
            elif status["status"] == "部分可用" or status["status"] == "功能受限":
                status_text += "<span class='status-indicator status-partial'></span>"
            else:
                status_text += "<span class='status-indicator status-error'></span>"
            
            status_text += f"<span>{status['status']}</span></div>"
            status_text += f"<div>{status['message']}</div>"
            
            if "api_info" in status:
                status_text += f"<div><small>{status['api_info']}</small></div>"
                
            # 添加详细信息折叠面板
            if "details" in status:
                status_text += "<details><summary>查看详细信息</summary><div class='detail-view'>"
                for name, info in status["details"].items():
                    status_emoji = "✅" if info["ok"] else "❌"
                    status_text += f"<div>{status_emoji} {name}: {info['status']}</div>"
                status_text += "</div></details>"
                
            return status_text
        
        # 绑定API状态按钮事件
        check_api_btn.click(
            fn=update_api_status,
            outputs=[api_status]
        )
        
        # 调试面板逻辑
        def toggle_debug_panel():
            # 收集测试数据
            test_data = {
                "assessment_questions": api_service._get_test_assessment_questions(),
                "enrolled_paths": api_service._get_test_enrolled_paths(),
                "recommended_paths": api_service._get_test_recommended_paths(),
                "path_details": api_service._get_test_path_details(1),
                "content": api_service._get_test_content(1)
            }
            return gr.update(value=test_data, visible=True)
        
        debug_btn.click(
            fn=toggle_debug_panel,
            outputs=[debug_panel]
        )

        # 运行测试流程
        def execute_test_flow():
            try:
                # 尝试创建一个学习路径
                path_data = {
                    "title": "Python编程基础路径",
                    "description": "从零开始学习Python编程的个性化路径",
                    "subject": "programming",
                    "difficulty_level": 2,
                    "estimated_hours": 25,
                    "goals": ["掌握Python基础语法", "能够编写简单的Python程序", "理解面向对象编程概念"],
                    "created_by": DEFAULT_USER_ID
                }
                
                path_result = api_service._request("POST", "/learning-paths", data=path_data)
                if "error" in path_result:
                    logger.warning(f"创建学习路径失败: {path_result['error']}")
                    # 尝试替代端点
                    path_result = api_service._request("POST", "/paths", data=path_data)
                
                # 然后尝试提交评估
                result = api_service._request("POST", "/assessment/submit", data={
                    "user_id": DEFAULT_USER_ID,
                    "responses": [
                        {"question_id": 1, "response_value": {"answer": "5"}, "response_time": 3.5},
                        {"question_id": 2, "response_value": {"answer": "3"}, "response_time": 4.2},
                        {"question_id": 3, "response_value": {"answer": "4"}, "response_time": 2.8},
                        {"question_id": 4, "response_value": {"answer": "2"}, "response_time": 5.0}
                    ]
                })
                
                if "error" in result:
                    return f"测试流程失败: {result['error']}"
                
                success_msg = "测试流程执行成功! 学习风格评估已提交"
                
                if not "error" in path_result:
                    success_msg += f"，并创建了学习路径 (ID: {path_result.get('id', '未知')})"
                    
                success_msg += "。请刷新仪表盘查看结果。"
                    
                return success_msg
                
            except Exception as e:
                return f"测试流程异常: {str(e)}"

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
