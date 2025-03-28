import gradio as gr
import time
import logging
from typing import Dict, Any

# 设置日志
logger = logging.getLogger("content_viewer")

def create_content_viewer_tab(api_service, user_id):
    """创建内容查看选项卡"""
    
    # 状态变量
    content_state = gr.State({
        "path_id": None,
        "content_id": None,
        "content_data": None,
        "start_time": 0,
        "progress": 0,
        "has_interacted": False,
        "learning_paths": []
    })
    
    # 加载用户的学习路径
    def load_user_paths():
        paths = api_service.get_enrolled_paths(user_id)
        
        if isinstance(paths, list) and paths:
            path_options = [(path["title"], path["id"]) for path in paths]
            return {
                "learning_paths": paths,
                "path_options": path_options
            }
        else:
            return {
                "learning_paths": [],
                "path_options": [("无可用学习路径", -1)]
            }
    
    # 加载路径内容
    def load_path_contents(path_id, state):
        if path_id == -1:
            return state, [("请先选择学习路径", -1)]
        
        path_details = api_service.get_path_details(path_id, user_id)
        
        state["path_id"] = path_id
        state["path_details"] = path_details
        
        if "contents" in path_details and path_details["contents"]:
            # 确保内容选项格式正确
            content_options = []
            for content in path_details["contents"]:
                # 处理可能的不同ID字段名
                content_id = content.get("id", content.get("content_id", -1))
                content_options.append((content["title"], content_id))
            return state, content_options
        else:
            return state, [("此学习路径暂无内容", -1)]
    
    # 加载内容详情
    def load_content(content_id):
        """从API加载内容"""
        if content_id is None or content_id == -1:
            return gr.update(visible=False), "请选择一个学习内容查看"
        
        # 处理特殊情况：没有内容时的列表
        if isinstance(content_id, list):
            if content_id and content_id[0] and content_id[0][0] == "此学习路径暂无内容":
                return gr.update(visible=True), "### 此学习路径暂无内容\n\n请等待内容更新或选择其他学习路径。"
        
        try:
            # 调用API服务获取内容
            content = api_service.get_content(content_id)
            
            if content and "id" in content and content["id"] != -1:
                # 根据内容类型渲染不同的UI
                if content["content_type"] == "video":
                    html = f"""
                    <div class="content-container">
                        <h2>{content["title"]}</h2>
                        <div class="video-container">
                            <iframe width="100%" height="400" src="{content["content_data"]["url"]}" 
                            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; 
                            gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </div>
                        <div class="description">
                            <p>{content["description"]}</p>
                        </div>
                    </div>
                    """
                    return gr.update(visible=True), html
                elif content["content_type"] == "text":
                    # 渲染Markdown内容
                    md_content = f"""
                    # {content["title"]}
                    
                    {content["description"]}
                    
                    ---
                    
                    {content["content_data"]["text"]}
                    """
                    return gr.update(visible=True), md_content
                else:
                    return gr.update(visible=True), f"### 不支持的内容类型: {content['content_type']}"
            else:
                return gr.update(visible=False), "无法加载内容，请选择其他内容"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"加载内容失败: {str(e)}\n{error_details}")
            return gr.update(visible=False), f"加载内容失败: {str(e)}"
    
    # 记录交互
    def record_interaction(state):
        if not state["has_interacted"] and state["content_id"] and state["path_id"]:
            state["has_interacted"] = True
            state["progress"] = 10  # 初始进度设为10%
            
            # 更新学习进度 - 修正函数名为update_learning_progress
            api_service.update_learning_progress(state["path_id"], user_id, state["content_id"], state["progress"])
        
        return state, f"已记录交互，当前进度: {state['progress']}%"
    
    # 完成学习
    def complete_learning(state):
        if state["content_id"] and state["path_id"]:
            state["progress"] = 100
            
            # 更新学习进度 - 修正函数名为update_learning_progress
            result = api_service.update_learning_progress(state["path_id"], user_id, state["content_id"], state["progress"])
            
            if "error" in result:
                return state, f"更新进度失败: {result['error']}"
            
            return state, "恭喜！您已完成本节学习内容。"
        
        return state, "无法更新学习进度，请确保已选择内容。"
    
    # 更新进度
    def update_progress(progress_value, state):
        if state["content_id"] and state["path_id"]:
            state["progress"] = progress_value
            
            # 更新学习进度 - 修正函数名为update_learning_progress
            result = api_service.update_learning_progress(state["path_id"], user_id, state["content_id"], state["progress"])
            
            if "error" in result:
                return state, f"更新进度失败: {result['error']}"
            
            return state, f"进度已更新: {progress_value}%"
        
        return state, "无法更新学习进度，请确保已选择内容。"
    
    # 创建UI组件
    with gr.Column():
        with gr.Group():
            gr.Markdown("## 学习内容查看器")
            
            # 路径选择
            path_dropdown = gr.Dropdown(
                label="选择学习路径",
                choices=[("加载中...", -1)],
                type="value",
                value=-1  # 确保有默认值
            )
            
            # 内容选择 - 添加allow_custom_value=True
            content_dropdown = gr.Dropdown(
                label="选择学习内容",
                choices=[("请先选择学习路径", -1)],
                type="value",
                value=-1,  # 确保有默认值
                allow_custom_value=True  # 允许自定义值
            )
            
            # 查看按钮
            view_btn = gr.Button("查看内容", variant="primary")
            
            # 内容显示
            content_display = gr.HTML()
            
            # 进度更新组件
            with gr.Group(visible=False) as progress_group:
                gr.Markdown("### 更新学习进度")
                
                # 进度滑块
                progress_slider = gr.Slider(
                    minimum=0,
                    maximum=100,
                    step=5,
                    label="学习进度",
                    value=0
                )
                
                # 更新按钮
                update_btn = gr.Button("更新进度", variant="primary")
                complete_btn = gr.Button("完成学习", variant="secondary")
                interact_btn = gr.Button("记录交互", variant="secondary")
            
            # 通知消息
            notification = gr.Textbox(label="通知", interactive=False)
    
    # 事件处理
    path_dropdown.change(
        fn=load_path_contents,
        inputs=[path_dropdown, content_state],
        outputs=[content_state, content_dropdown]
    )
    
    view_btn.click(
        fn=load_content,
        inputs=[content_dropdown],
        outputs=[content_display]
    )
    
    interact_btn.click(
        fn=record_interaction,
        inputs=[content_state],
        outputs=[content_state, notification]
    )
    
    update_btn.click(
        fn=update_progress,
        inputs=[progress_slider, content_state],
        outputs=[content_state, notification]
    )
    
    complete_btn.click(
        fn=complete_learning,
        inputs=[content_state],
        outputs=[content_state, notification]
    )
    
    # 初始加载 - 确保安全初始化
    try:
        user_paths = load_user_paths()
        path_options = user_paths.get("path_options", [("无可用学习路径", -1)])
        path_dropdown.choices = path_options
    except Exception as e:
        logger.error(f"初始化路径下拉框失败: {str(e)}")
        path_dropdown.choices = [("加载失败", -1)]
    
    return content_state
