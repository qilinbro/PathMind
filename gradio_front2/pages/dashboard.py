"""
仪表盘页面组件
"""
import gradio as gr
import logging
import asyncio
from utils.chart_utils import create_learning_style_chart

# 设置日志
logger = logging.getLogger(__name__)

def create_dashboard_tab(api_service, user_id):
    """创建仪表盘标签页"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 学习风格概览")
            # 使用实际函数生成初始图表
            initial_chart = create_learning_style_chart()
            learning_style_chart = gr.Plot(value=initial_chart, label="学习风格分布")
            
            gr.Markdown("### 最近活动")
            recent_activity = gr.Dataframe(
                headers=["日期", "活动", "详情"],
                value=[
                    ["2023-08-15", "完成学习内容", "Python基础 - 变量和数据类型"],
                    ["2023-08-14", "开始学习路径", "Python编程基础"],
                    ["2023-08-13", "完成学习风格评估", "视觉偏好: 高, 听觉偏好: 中等"]
                ]
            )
            
            # 添加学习进度小节
            gr.Markdown("### 学习进度概览")
            progress_info = gr.HTML("""
                <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <p>点击"刷新数据"获取您的学习进度信息</p>
                </div>
            """)
        
        with gr.Column():
            gr.Markdown("### 进行中的学习路径")
            enrolled_paths = gr.Dataframe(
                headers=["路径", "进度", "最近活动"],
                value=[
                    ["Python编程基础", "35%", "2023-08-15"],
                    ["数据科学入门", "20%", "2023-08-10"]
                ]
            )
            
            gr.Markdown("### 推荐学习路径")
            recommended_paths = gr.Dataframe(
                headers=["路径", "匹配度", "预计学时"],
                value=[
                    ["机器学习基础", "85%", "40小时"],
                    ["Web开发入门", "75%", "30小时"]
                ]
            )
            
            # 添加学习弱点部分
            gr.Markdown("### 学习弱点分析")
            weaknesses_info = gr.HTML("""
                <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <p>点击"刷新数据"获取您的学习弱点分析</p>
                </div>
            """)
            
            refresh_btn = gr.Button("刷新数据", variant="primary")
    
    # 定义刷新仪表盘函数
    def refresh_dashboard():
        try:
            results = {}
            
            # 1. 获取用户学习风格数据
            try:
                style_result = asyncio.run(api_service.request("GET", f"assessment/user/{user_id}"))
                if "error" not in style_result and "learning_style_result" in style_result:
                    ls = style_result["learning_style_result"]
                    chart = create_learning_style_chart(
                        visual=ls.get("visual", 70),
                        auditory=ls.get("auditory", 50),
                        kinesthetic=ls.get("kinesthetic", 80),
                        reading=ls.get("reading", 40)
                    )
                    results["style_chart"] = chart
                    logger.info("成功获取学习风格数据")
                else:
                    chart = create_learning_style_chart()
                    results["style_chart"] = chart
                    logger.warning("未获取到学习风格数据，使用默认值")
            except Exception as e:
                logger.error(f"获取学习风格数据失败: {str(e)}")
                chart = create_learning_style_chart()
                results["style_chart"] = chart
            
            # 2. 获取学习路径 - 只保留异常处理和返回部分，减少代码量
            try:
                enrolled_result = asyncio.run(api_service.request(
                    "GET", "learning-paths", 
                    params={"user_id": user_id, "enrolled": "true"}
                ))
                
                if "error" not in enrolled_result and isinstance(enrolled_result, list):
                    paths_data = [
                        [path.get("title", "未知路径"), 
                        f"{path.get('progress', 0)}%", 
                        path.get("last_activity", "未知").split("T")[0]]
                        for path in enrolled_result
                    ]
                    results["enrolled_paths"] = paths_data
                else:
                    # 使用测试数据
                    paths = api_service._get_test_enrolled_paths()
                    paths_data = [
                        [path.get("title", "未知路径"), 
                        f"{path.get('progress', 0)}%", 
                        path.get("last_activity", "未知").split("T")[0]]
                        for path in paths
                    ]
                    results["enrolled_paths"] = paths_data
            except Exception as e:
                logger.error(f"获取已注册路径失败: {str(e)}")
                results["enrolled_paths"] = enrolled_paths.value
            
            # 3. 获取推荐路径 - 类似操作
            try:
                recommended_result = asyncio.run(api_service.request(
                    "GET", "learning-paths/recommended", 
                    params={"user_id": user_id}
                ))
                
                if "error" not in recommended_result and isinstance(recommended_result, list):
                    rec_data = [
                        [path.get("title", "未知路径"), 
                        f"{path.get('match_score', 0)}%", 
                        f"{path.get('estimated_hours', 0)}小时"]
                        for path in recommended_result
                    ]
                    results["recommended_paths"] = rec_data
                else:
                    # 使用测试数据
                    paths = api_service._get_test_recommended_paths()
                    rec_data = [
                        [path.get("title", "未知路径"), 
                        f"{path.get('match_score', 0)}%", 
                        f"{path.get('estimated_hours', 0)}小时"]
                        for path in paths
                    ]
                    results["recommended_paths"] = rec_data
            except Exception as e:
                logger.error(f"获取推荐路径失败: {str(e)}")
                results["recommended_paths"] = recommended_paths.value
            
            # 4 & 5. 获取学习进度和弱点分析 - 简化错误处理
            progress_html = """<div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                <h4>学习进度分析</h4>
                <p>未能获取进度数据，请稍后再试</p>
            </div>"""
            
            weaknesses_html = """<div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                <h4>学习弱点分析</h4>
                <p>未能获取弱点数据，请稍后再试</p>
            </div>"""
            
            try:
                progress_result = asyncio.run(api_service.request(
                    "GET", f"assessment/progress/{user_id}"
                ))
                if "error" not in progress_result:
                    # 创建学习进度HTML
                    progress_metrics = progress_result.get("progress_metrics", {})
                    progress_html = create_progress_html(progress_metrics, 
                                                       progress_result.get("improvement_suggestions", []))
                    results["progress_info"] = progress_html
            except Exception as e:
                logger.error(f"获取学习进度数据失败: {str(e)}")
                
            try:
                weaknesses_result = asyncio.run(api_service.request(
                    "GET", f"analytics/weaknesses/{user_id}"
                ))
                if "error" not in weaknesses_result:
                    weaknesses_html = create_weaknesses_html(
                        weaknesses_result.get("weak_areas", []),
                        weaknesses_result.get("strength_areas", []),
                        weaknesses_result.get("improvement_plan", {})
                    )
                    results["weaknesses_info"] = weaknesses_html
            except Exception as e:
                logger.error(f"获取学习弱点数据失败: {str(e)}")
            
            # 返回所有结果
            return (
                results.get("style_chart", chart), 
                results.get("enrolled_paths", enrolled_paths.value),
                results.get("recommended_paths", recommended_paths.value),
                results.get("progress_info", progress_html),
                results.get("weaknesses_info", weaknesses_html)
            )
            
        except Exception as e:
            logger.error(f"刷新仪表盘失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return initial_chart, enrolled_paths.value, recommended_paths.value, progress_info.value, weaknesses_info.value
    
    # 更新按钮处理函数以包含新的输出组件
    refresh_btn.click(
        fn=refresh_dashboard,
        outputs=[learning_style_chart, enrolled_paths, recommended_paths, progress_info, weaknesses_info]
    )
    
    return enrolled_paths, recommended_paths

# 辅助函数: 创建进度HTML
def create_progress_html(metrics, suggestions):
    html = """
    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
        <h4>学习进度分析</h4>
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;">
    """
    
    for metric_name, metric_value in metrics.items():
        if isinstance(metric_value, (int, float)):
            html += f"""
            <div style="flex:1;min-width:120px;background:white;padding:10px;border-radius:5px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-weight:bold;color:#555;">{metric_name}</div>
                <div style="font-size:1.5em;margin:5px 0;">{metric_value}</div>
            </div>
            """
    
    html += """
        </div>
        <div style="margin-top:15px;">
            <h5>改进建议</h5>
            <ul>
    """
    
    for suggestion in suggestions:
        html += f"<li>{suggestion}</li>"
    
    if not suggestions:
        html += "<li>继续保持当前学习节奏</li>"
        html += "<li>尝试不同类型的学习内容</li>"
    
    html += """
            </ul>
        </div>
    </div>
    """
    
    return html

# 辅助函数: 创建弱点分析HTML
def create_weaknesses_html(weak_areas, strength_areas, improvement_plan):
    html = """
    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
        <h4>学习弱点分析</h4>
    """
    
    # 弱点区域
    if weak_areas:
        html += """
        <div style="margin-top:10px;">
            <h5>需要加强的领域</h5>
            <ul style="color:#dc3545;">
        """
        
        for area in weak_areas:
            topic = area.get("topic", "未知")
            confidence = area.get("confidence_level", 0)
            html += f"<li><strong>{topic}</strong> (掌握程度: {confidence}%)</li>"
        
        html += """
            </ul>
        </div>
        """
    
    # 强项区域
    if strength_areas:
        html += """
        <div style="margin-top:10px;">
            <h5>您的强项领域</h5>
            <ul style="color:#198754;">
        """
        
        for area in strength_areas:
            topic = area.get("topic", "未知")
            confidence = area.get("confidence_level", 0)
            html += f"<li><strong>{topic}</strong> (掌握程度: {confidence}%)</li>"
        
        html += """
            </ul>
        </div>
        """
    
    # 改进计划
    if improvement_plan:
        html += """
        <div style="margin-top:15px;">
            <h5>改进计划建议</h5>
            <div style="background:white;padding:10px;border-radius:5px;">
        """
        
        for step, description in improvement_plan.items():
            html += f"<p><strong>{step}</strong>: {description}</p>"
        
        html += """
            </div>
        </div>
        """
    
    html += "</div>"
    return html
