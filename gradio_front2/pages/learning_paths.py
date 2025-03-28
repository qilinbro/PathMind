"""
学习路径页面组件
"""
import gradio as gr
import logging
import asyncio

# 设置日志
logger = logging.getLogger(__name__)

def create_learning_paths_tab(api_service, user_id):
    """创建学习路径标签页"""
    with gr.Tabs() as path_tabs:
        with gr.TabItem("我的学习路径"):
            gr.Markdown("### 我的学习路径")
            
            enrolled_paths = api_service._get_test_enrolled_paths()
            path_result = gr.Textbox(label="操作结果", interactive=False, visible=False)
            
            with gr.Row():
                for path in enrolled_paths:
                    with gr.Column():
                        with gr.Group():
                            gr.Markdown(f"#### {path['title']}")
                            gr.Markdown(path['description'])
                            gr.Markdown(f"**进度**: {path['progress']}%")
                            progress_bar = gr.Slider(
                                minimum=0, 
                                maximum=100, 
                                value=path['progress'], 
                                interactive=False,
                                label=""
                            )
                            path_id = path['id']
                            
                            view_btn = gr.Button(f"查看路径 {path_id}", variant="primary")
                            
                            def create_view_handler(pid):
                                def view_handler():
                                    try:
                                        result = asyncio.run(api_service.request(
                                            "GET", 
                                            f"learning-paths/{pid}", 
                                            params={"user_id": user_id}
                                        ))
                                        
                                        if "error" in result:
                                            return gr.update(value=f"获取路径详情失败: {result['error']}", visible=True)
                                        return gr.update(value=f"查看路径 ID: {pid} - 标题: {result.get('title', '未知')}", visible=True)
                                    except Exception as e:
                                        logger.error(f"查看路径失败: {str(e)}")
                                        return gr.update(value=f"查看路径失败: {str(e)}", visible=True)
                                return view_handler
                            
                            view_btn.click(
                                fn=create_view_handler(path_id),
                                outputs=[path_result]
                            )
            
            refresh_paths_btn = gr.Button("刷新学习路径")
        
        with gr.TabItem("推荐学习路径"):
            gr.Markdown("### 为您推荐的学习路径")
            
            recommended_paths = api_service._get_test_recommended_paths()
            
            with gr.Row():
                for path in recommended_paths:
                    with gr.Column():
                        with gr.Group():
                            gr.Markdown(f"#### {path['title']}")
                            gr.Markdown(path['description'])
                            gr.Markdown(f"**匹配度**: {path['match_score']}%")
                            gr.Markdown(f"**预计学时**: {path['estimated_hours']}小时")
                            path_id = path['id']
                            
                            enroll_btn = gr.Button(f"注册路径 {path_id}", variant="primary")
                            
                            def create_enroll_handler(pid):
                                def enroll_handler():
                                    try:
                                        enrollment_data = {
                                            "user_id": user_id,
                                            "path_id": pid,
                                            "personalization_settings": {
                                                "preferred_content_types": ["video", "interactive"],
                                                "study_reminder": True
                                            }
                                        }
                                        
                                        result = asyncio.run(api_service.request(
                                            "POST", 
                                            "learning-paths/enroll", 
                                            data=enrollment_data
                                        ))
                                        
                                        if "error" in result:
                                            return gr.update(value=f"注册路径失败: {result['error']}", visible=True)
                                        return gr.update(value=f"成功注册路径 ID: {pid}", visible=True)
                                    except Exception as e:
                                        logger.error(f"注册路径失败: {str(e)}")
                                        return gr.update(value=f"注册路径失败: {str(e)}", visible=True)
                                return enroll_handler
                            
                            enroll_btn.click(
                                fn=create_enroll_handler(path_id),
                                outputs=[path_result]
                            )
            
            refresh_rec_btn = gr.Button("刷新推荐")
        
        with gr.TabItem("创建学习路径"):
            gr.Markdown("### 创建新的学习路径")
            
            with gr.Row():
                with gr.Column():
                    path_title = gr.Textbox(label="路径标题", placeholder="输入路径标题")
                    path_description = gr.Textbox(
                        label="路径描述", 
                        placeholder="描述这个学习路径的内容和目标",
                        lines=3
                    )
                    path_subject = gr.Dropdown(
                        label="主题领域",
                        choices=["programming", "data_science", "mathematics", "language", "other"],
                        value="programming"
                    )
                
                with gr.Column():
                    path_difficulty = gr.Radio(
                        label="难度级别",
                        choices=["入门", "基础", "中级", "高级", "专家"],
                        value="基础"
                    )
                    path_hours = gr.Number(label="预计学习时间(小时)", value=20)
                    path_goals = gr.Textbox(
                        label="学习目标(每行一个)", 
                        placeholder="输入学习目标，每行一个",
                        lines=3
                    )
            
            create_path_btn = gr.Button("创建学习路径", variant="primary")
            
            def create_path(title, description, subject, difficulty, hours, goals):
                try:
                    goals_list = [goal.strip() for goal in goals.split('\n') if goal.strip()]
                    
                    path_data = {
                        "title": title,
                        "description": description,
                        "subject": subject,
                        "difficulty_level": {"入门": 1, "基础": 2, "中级": 3, "高级": 4, "专家": 5}.get(difficulty, 2),
                        "estimated_hours": float(hours) if hours else 20,
                        "goals": goals_list,
                        "difficulty": {"入门": "beginner", "基础": "beginner", "中级": "intermediate", 
                                    "高级": "advanced", "专家": "expert"}.get(difficulty, "beginner"),
                        "created_by": user_id
                    }
                    
                    result = asyncio.run(api_service.request("POST", "learning-paths", data=path_data))
                    
                    if "error" in result:
                        return gr.update(value=f"创建学习路径失败: {result['error']}", visible=True)
                    
                    return gr.update(value=f"学习路径创建成功！ID: {result.get('id', '未知')}", visible=True)
                except Exception as e:
                    logger.error(f"创建学习路径失败: {str(e)}")
                    return gr.update(value=f"创建学习路径失败: {str(e)}", visible=True)
    
            create_path_btn.click(
                fn=create_path,
                inputs=[path_title, path_description, path_subject, path_difficulty, path_hours, path_goals],
                outputs=[path_result]
            )
    
    return path_result
