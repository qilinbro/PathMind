import gradio as gr
import logging
from typing import Dict, List, Any

# 设置日志
logger = logging.getLogger("dashboard")

def create_dashboard_tab(api_service, user_id):
    """创建仪表盘选项卡"""
    
    # 加载用户学习数据
    def load_dashboard_data():
        logger.info("加载仪表盘数据")
        
        # 使用异常处理避免一个API调用失败影响整个数据加载
        try:
            enrolled_paths = api_service.get_enrolled_paths(user_id)
            if "error" in enrolled_paths:
                logger.error(f"获取已注册路径错误: {enrolled_paths['error']}")
                enrolled_paths = []
            elif not isinstance(enrolled_paths, list):
                logger.warning("已注册路径数据格式错误")
                enrolled_paths = []
        except Exception as e:
            logger.error(f"获取已注册路径异常: {str(e)}")
            enrolled_paths = []
        
        try:
            recommended_paths = api_service.get_recommended_paths(user_id)
            if "error" in recommended_paths:
                logger.error(f"获取推荐路径错误: {recommended_paths['error']}")
                recommended_paths = []
            elif not isinstance(recommended_paths, list):
                logger.warning("推荐路径数据格式错误")
                recommended_paths = []
        except Exception as e:
            logger.error(f"获取推荐路径异常: {str(e)}")
            recommended_paths = []
            
        try:
            learning_progress = api_service.get_learning_progress(user_id)
            if "error" in learning_progress:
                # 这里我们不用警告，因为404是预期行为 - 表示用户没有评估记录
                if "404" in learning_progress["error"]:
                    logger.info("用户没有评估记录")
                else:
                    logger.error(f"获取学习进度错误: {learning_progress['error']}")
                learning_progress = {}
            elif not isinstance(learning_progress, dict):
                logger.warning("学习进度数据格式错误")
                learning_progress = {}
        except Exception as e:
            logger.error(f"获取学习进度异常: {str(e)}")
            learning_progress = {}
            
        return {
            "enrolled_paths": enrolled_paths if isinstance(enrolled_paths, list) else [],
            "recommended_paths": recommended_paths if isinstance(recommended_paths, list) else [],
            "learning_progress": learning_progress if isinstance(learning_progress, dict) else {}
        }
    
    # 生成仪表盘HTML
    def generate_dashboard_html(data):
        enrolled_paths = data.get("enrolled_paths", [])
        recommended_paths = data.get("recommended_paths", [])
        learning_progress = data.get("learning_progress", {})
        
        html = """
        <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
            <h2 style="margin-bottom: 20px;">学习仪表盘</h2>
        """
        
        # 学习风格信息
        current_style = learning_progress.get("current_learning_style", {})
        if current_style:
            html += """
            <div style="margin-bottom: 30px;">
                <h3>您的学习风格</h3>
                <div style="margin-top: 15px; display: flex; justify-content: space-between;">
            """
            
            # 各维度得分
            styles = [
                ("视觉学习", current_style.get("visual", 0), "#0d6efd"),
                ("听觉学习", current_style.get("auditory", 0), "#198754"),
                ("动觉学习", current_style.get("kinesthetic", 0), "#dc3545"),
                ("阅读学习", current_style.get("reading", 0), "#ffc107")
            ]
            
            for name, score, color in styles:
                html += f"""
                <div style="width: 22%; text-align: center;">
                    <div style="position: relative; width: 100%; padding-top: 100%; background-color: #e9ecef; border-radius: 50%; overflow: hidden;">
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: conic-gradient({color} 0% {score}%, #e9ecef {score}% 100%);">
                        </div>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; height: 80%; background-color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center;">
                            <span style="font-size: 1.2em; font-weight: bold;">{score}%</span>
                        </div>
                    </div>
                    <p style="margin-top: 10px;">{name}</p>
                </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        # 已注册的学习路径
        html += """
            <div style="margin-bottom: 30px;">
                <h3>已注册的学习路径</h3>
        """
        
        if enrolled_paths:
            html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">'
            
            for path in enrolled_paths:
                # 进度条颜色
                progress_color = "#0d6efd"
                if path.get("progress", 0) >= 100:
                    progress_color = "#198754"  # 完成为绿色
                
                html += f"""
                <div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                    <h4>{path['title']}</h4>
                    <p style="color: #6c757d; height: 60px; overflow: hidden;">{path.get('description', '')}</p>
                    
                    <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                        <span>难度: {path.get('difficulty_level', 0)}/5</span>
                        <span>预计时间: {path.get('estimated_hours', 0)}小时</span>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>进度</span>
                            <span>{path.get('progress', 0)}%</span>
                        </div>
                        <div style="height: 10px; background-color: #e9ecef; border-radius: 5px;">
                            <div style="height: 100%; width: {path.get('progress', 0)}%; background-color: {progress_color}; border-radius: 5px;">
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            html += '</div>'
        else:
            html += """
            <div style="margin-top: 15px; text-align: center; padding: 40px; background-color: white; border-radius: 8px;">
                <p style="color: #6c757d;">您还没有注册任何学习路径</p>
                <p style="margin-top: 10px;">完成<a href="javascript:void(0);" onclick="switchToTab('学习风格评估')" style="color: #0d6efd; text-decoration: none;">学习风格评估</a>后获取个性化推荐</p>
            </div>
            """
        
        # 推荐的学习路径
        html += """
            </div>
            
            <div>
                <h3>推荐学习路径</h3>
        """
        
        if recommended_paths:
            html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">'
            
            for path in recommended_paths:
                html += f"""
                <div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                    <h4>{path['title']}</h4>
                    <p style="color: #6c757d; height: 60px; overflow: hidden;">{path.get('description', '')}</p>
                    
                    <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                        <span>难度: {path.get('difficulty_level', 0)}/5</span>
                        <span>预计时间: {path.get('estimated_hours', 0)}小时</span>
                    </div>
                    
                    <div style="margin-top: 15px; text-align: right;">
                        <a href="javascript:void(0);" onclick="viewPath({path['id']})" style="display: inline-block; padding: 5px 15px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px;">
                            查看详情
                        </a>
                    </div>
                </div>
                """
            
            html += '</div>'
        else:
            html += """
            <div style="margin-top: 15px; text-align: center; padding: 40px; background-color: white; border-radius: 8px;">
                <p style="color: #6c757d;">暂无推荐的学习路径</p>
            </div>
            """
        
        html += """
            </div>
        </div>
        
        <script>
            function switchToTab(tabName) {
                // 在实际应用中，需要在Gradio中实现相应的标签页切换逻辑
                console.log('Switch to tab:', tabName);
            }
            
            function viewPath(pathId) {
                // 在实际应用中，需要在Gradio中实现路径查看逻辑
                console.log('View path:', pathId);
            }
        </script>
        """
        
        return html
    
    # 创建UI组件
    with gr.Column():
        with gr.Group():
            gr.Markdown("## 学习仪表盘")
            
            # 刷新按钮
            refresh_btn = gr.Button("刷新数据", variant="secondary")
            
            # 仪表盘显示
            dashboard_display = gr.HTML()
    
    # 事件处理
    refresh_btn.click(
        fn=lambda: generate_dashboard_html(load_dashboard_data()),
        outputs=[dashboard_display]
    )
    
    # 初始加载
    dashboard_html = generate_dashboard_html(load_dashboard_data())
    dashboard_display.value = dashboard_html
    
    return dashboard_display
