import gradio as gr
from typing import Dict, List, Any

def create_learning_paths_tab(api_service, user_id):
    """创建学习路径选项卡"""
    
    # 状态管理
    path_state = gr.State({
        "selected_path": None,
        "enrolled_paths": [],
        "recommended_paths": [],
        "current_path_details": None
    })
    
    # 加载学习路径数据
    def load_paths():
        enrolled = api_service.get_enrolled_paths(user_id)
        recommended = api_service.get_recommended_paths(user_id)
        
        return {
            "selected_path": None,
            "enrolled_paths": enrolled if isinstance(enrolled, list) else [],
            "recommended_paths": recommended if isinstance(recommended, list) else [],
            "current_path_details": None
        }
    
    # 生成路径选项列表
    def generate_path_options(state):
        enrolled_options = [(f"已注册: {path['title']}", path["id"]) for path in state["enrolled_paths"]]
        recommended_options = [(f"推荐: {path['title']}", path["id"]) for path in state["recommended_paths"]]
        
        all_options = enrolled_options + recommended_options
        if not all_options:
            all_options = [("无可用学习路径", -1)]
        
        return all_options
    
    # 加载并显示路径详情
    def load_path_details(path_id, state):
        if path_id == -1:
            return state, "没有选择学习路径"
        
        details = api_service.get_path_details(path_id, user_id)
        state["current_path_details"] = details
        state["selected_path"] = path_id
        
        html = generate_path_details_html(details)
        return state, html
    
    # 注册学习路径
    def enroll_path(path_id, state):
        if path_id == -1:
            return state, "请先选择一个学习路径"
        
        # 检查是否已注册
        if any(p["id"] == path_id for p in state["enrolled_paths"]):
            return state, "您已经注册了这个学习路径"
        
        # 注册新路径
        result = api_service.enroll_in_path(user_id, path_id)
        
        if "error" in result:
            return state, f"注册失败: {result['error']}"
        
        # 刷新路径列表
        new_state = load_paths()
        new_state["selected_path"] = path_id
        
        # 重新加载路径详情
        details = api_service.get_path_details(path_id, user_id)
        new_state["current_path_details"] = details
        
        return new_state, "成功注册学习路径！"
    
    # 注册路径并更新UI
    def handle_enroll(path_id, state):
        new_state, message = enroll_path(path_id, state)
        options = generate_path_options(new_state)
        return new_state, message, options
    
    # 生成路径详情HTML
    def generate_path_details_html(details):
        if not details or "error" in details:
            return "无法加载路径详情"
        
        html = f"""
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
            <h2>{details['title']}</h2>
            
            <div style="margin-top: 10px; color: #6c757d;">
                <span>学科: {details['subject']}</span> | 
                <span>难度: {details['difficulty_level']}/5</span> | 
                <span>预计学时: {details['estimated_hours']}小时</span>
            </div>
            
            <div style="margin-top: 15px;">
                <p>{details['description']}</p>
            </div>
        """
        
        # 添加用户进度（如果已注册）
        if "user_progress" in details and details["user_progress"]:
            progress = details["user_progress"]["overall_progress"]
            html += f"""
            <div style="margin-top: 20px;">
                <h3>学习进度</h3>
                <div style="margin-top: 10px;">
                    <div style="display: flex; align-items: center;">
                        <span style="width: 100px;">总体进度:</span>
                        <div style="flex-grow: 1; background-color: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="background-color: #0d6efd; width: {progress}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                        <span style="margin-left: 10px;">{progress:.1f}%</span>
                    </div>
                </div>
            </div>
            """
        
        # 添加内容列表
        html += """
            <div style="margin-top: 20px;">
                <h3>学习内容</h3>
                <div style="margin-top: 10px;">
        """
        
        if "contents" in details and details["contents"]:
            for i, content in enumerate(details["contents"]):
                # 检查内容进度
                progress = 0
                if ("user_progress" in details and details["user_progress"] and 
                    "content_progress" in details["user_progress"] and 
                    str(content["id"]) in details["user_progress"]["content_progress"]):
                    progress = details["user_progress"]["content_progress"][str(content["id"])]
                
                # 内容类型图标
                icon = "📄"
                if content["content_type"] == "video":
                    icon = "🎬"
                elif content["content_type"] == "interactive":
                    icon = "🎮"
                elif content["content_type"] == "quiz":
                    icon = "❓"
                elif content["content_type"] == "article":
                    icon = "📝"
                
                # 生成内容项
                html += f"""
                <div style="padding: 10px; margin-bottom: 10px; background-color: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: bold;">{i+1}. {icon} {content['title']}</span>
                            <p style="margin-top: 5px; font-size: 0.9em; color: #6c757d;">{content['description']}</p>
                        </div>
                        <div>
                            <span style="font-size: 0.8em; color: #6c757d;">难度: {content['difficulty_level']}/5</span>
                        </div>
                    </div>
                """
                
                # 添加进度条（如果有进度）
                if progress > 0:
                    html += f"""
                    <div style="margin-top: 10px;">
                        <div style="display: flex; align-items: center;">
                            <div style="flex-grow: 1; background-color: #e9ecef; height: 8px; border-radius: 4px;">
                                <div style="background-color: #0d6efd; width: {progress}%; height: 8px; border-radius: 4px;"></div>
                            </div>
                            <span style="margin-left: 10px; font-size: 0.8em;">{progress:.0f}%</span>
                        </div>
                    </div>
                    """
                
                html += "</div>"
        else:
            html += "<p>此学习路径暂无内容</p>"
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html
    
    # 处理刷新按钮，加载路径并生成选项
    def handle_refresh():
        state = load_paths()
        options = generate_path_options(state)
        return state, options
    
    # 创建UI组件
    with gr.Column():
        with gr.Group():
            gr.Markdown("## 学习路径浏览")
            
            # 刷新按钮
            refresh_btn = gr.Button("刷新学习路径列表", variant="secondary")
            
            # 路径选择器
            path_dropdown = gr.Dropdown(
                label="选择学习路径",
                choices=[("加载中...", -1)],
                type="value"
            )
            
            # 查看和注册按钮
            with gr.Row():
                view_btn = gr.Button("查看详情", variant="primary")
                enroll_btn = gr.Button("注册路径", variant="secondary")
            
            # 通知消息
            notification = gr.Textbox(label="通知", interactive=False)
            
            # 路径详情展示
            path_details = gr.HTML()
    
    # 事件处理
    refresh_btn.click(
        fn=handle_refresh,
        outputs=[path_state, path_dropdown]
    )
    
    view_btn.click(
        fn=load_path_details,
        inputs=[path_dropdown, path_state],
        outputs=[path_state, path_details]
    )
    
    enroll_btn.click(
        fn=handle_enroll,
        inputs=[path_dropdown, path_state],
        outputs=[path_state, notification, path_dropdown]
    )
    
    # 初始数据加载
    initial_state, initial_options = handle_refresh()
    path_state.value = initial_state
    path_dropdown.choices = initial_options
    
    return path_state
