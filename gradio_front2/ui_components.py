import gradio as gr
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import asyncio
import json
import traceback
from datetime import datetime

matplotlib.use('Agg')  # 使用非交互式后端

# 设置日志
logger = logging.getLogger("ui_components")

def create_learning_style_chart(visual=70, auditory=50, kinesthetic=80, reading=40):
    """创建学习风格雷达图"""
    try:
        # 创建雷达图
        categories = ['视觉学习', '听觉学习', '动觉学习', '阅读学习']
        values = [visual, auditory, kinesthetic, reading]
        
        # 创建角度并闭合图形
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # 闭合图形
        values += values[:1]  # 闭合数据
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # 填充雷达图
        ax.fill(angles, values, color='skyblue', alpha=0.7)
        ax.plot(angles, values, 'o-', color='blue', linewidth=2)
        
        # 设置标签
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, 100)
        ax.set_title('学习风格分析', fontsize=15, pad=20)
        ax.grid(True)
        
        for angle, value in zip(angles[:-1], values[:-1]):
            ax.text(angle, value + 10, f"{value}%", 
                    horizontalalignment='center', 
                    verticalalignment='center')
        
        return fig
    except Exception as e:
        logger.error(f"创建学习风格图表失败: {str(e)}")
        # 创建一个错误图表
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, f"图表生成失败: {str(e)}", ha='center', va='center', wrap=True)
        ax.axis('off')
        return fig

def create_dashboard_tab(api_service, user_id):
    """创建仪表盘标签页 - 增强版"""
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
    
    # 增强版刷新数据处理函数，获取更多API数据
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
            
            # 2. 获取学习路径
            try:
                # 已注册的路径
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
                    logger.info(f"成功获取 {len(paths_data)} 个已注册学习路径")
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
                    logger.warning("未获取到已注册路径数据，使用测试数据")
            except Exception as e:
                logger.error(f"获取已注册路径失败: {str(e)}")
                results["enrolled_paths"] = enrolled_paths.value
            
            # 3. 获取推荐路径
            try:
                # 推荐路径
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
                    logger.info(f"成功获取 {len(rec_data)} 个推荐学习路径")
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
                    logger.warning("未获取到推荐路径数据，使用测试数据")
            except Exception as e:
                logger.error(f"获取推荐路径失败: {str(e)}")
                results["recommended_paths"] = recommended_paths.value
            
            # 4. 获取学习进度分析
            try:
                progress_result = asyncio.run(api_service.request(
                    "GET", f"assessment/progress/{user_id}"
                ))
                
                if "error" not in progress_result:
                    # 创建学习进度HTML
                    progress_metrics = progress_result.get("progress_metrics", {})
                    progress_html = """
                    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                        <h4>学习进度分析</h4>
                        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;">
                    """
                    
                    # 添加进度指标
                    for metric_name, metric_value in progress_metrics.items():
                        if isinstance(metric_value, (int, float)):
                            progress_html += f"""
                            <div style="flex:1;min-width:120px;background:white;padding:10px;border-radius:5px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                                <div style="font-weight:bold;color:#555;">{metric_name}</div>
                                <div style="font-size:1.5em;margin:5px 0;">{metric_value}</div>
                            </div>
                            """
                    
                    progress_html += """
                        </div>
                        <div style="margin-top:15px;">
                            <h5>改进建议</h5>
                            <ul>
                    """
                    
                    # 添加改进建议
                    suggestions = progress_result.get("improvement_suggestions", [])
                    for suggestion in suggestions:
                        progress_html += f"<li>{suggestion}</li>"
                    
                    if not suggestions:
                        progress_html += "<li>继续保持当前学习节奏</li>"
                        progress_html += "<li>尝试不同类型的学习内容</li>"
                    
                    progress_html += """
                            </ul>
                        </div>
                    </div>
                    """
                    
                    results["progress_info"] = progress_html
                    logger.info("成功获取学习进度分析")
                else:
                    # 使用默认内容
                    results["progress_info"] = """
                    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                        <h4>学习进度分析</h4>
                        <p>未能获取进度数据，请稍后再试</p>
                    </div>
                    """
                    logger.warning("未获取到学习进度数据")
            except Exception as e:
                logger.error(f"获取学习进度数据失败: {str(e)}")
                results["progress_info"] = """
                <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                    <h4>学习进度分析</h4>
                    <p>获取数据时出错，请稍后再试</p>
                    <small style="color:red;">错误: {}</small>
                </div>
                """.format(str(e))
            
            # 5. 获取学习弱点分析
            try:
                weaknesses_result = asyncio.run(api_service.request(
                    "GET", f"analytics/weaknesses/{user_id}"
                ))
                
                if "error" not in weaknesses_result:
                    # 创建学习弱点HTML
                    weak_areas = weaknesses_result.get("weak_areas", [])
                    strength_areas = weaknesses_result.get("strength_areas", [])
                    
                    weaknesses_html = """
                    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                        <h4>学习弱点分析</h4>
                    """
                    
                    # 弱点区域
                    if weak_areas:
                        weaknesses_html += """
                        <div style="margin-top:10px;">
                            <h5>需要加强的领域</h5>
                            <ul style="color:#dc3545;">
                        """
                        
                        for area in weak_areas:
                            topic = area.get("topic", "未知")
                            confidence = area.get("confidence_level", 0)
                            weaknesses_html += f"<li><strong>{topic}</strong> (掌握程度: {confidence}%)</li>"
                        
                        weaknesses_html += """
                            </ul>
                        </div>
                        """
                    
                    # 强项区域
                    if strength_areas:
                        weaknesses_html += """
                        <div style="margin-top:10px;">
                            <h5>您的强项领域</h5>
                            <ul style="color:#198754;">
                        """
                        
                        for area in strength_areas:
                            topic = area.get("topic", "未知")
                            confidence = area.get("confidence_level", 0)
                            weaknesses_html += f"<li><strong>{topic}</strong> (掌握程度: {confidence}%)</li>"
                        
                        weaknesses_html += """
                            </ul>
                        </div>
                        """
                    
                    # 改进计划
                    improvement_plan = weaknesses_result.get("improvement_plan", {})
                    if improvement_plan:
                        weaknesses_html += """
                        <div style="margin-top:15px;">
                            <h5>改进计划建议</h5>
                            <div style="background:white;padding:10px;border-radius:5px;">
                        """
                        
                        for step, description in improvement_plan.items():
                            weaknesses_html += f"<p><strong>{step}</strong>: {description}</p>"
                        
                        weaknesses_html += """
                            </div>
                        </div>
                        """
                    
                    weaknesses_html += "</div>"
                    results["weaknesses_info"] = weaknesses_html
                    logger.info("成功获取学习弱点分析")
                else:
                    # 使用默认内容
                    results["weaknesses_info"] = """
                    <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                        <h4>学习弱点分析</h4>
                        <p>未能获取弱点数据，请稍后再试</p>
                    </div>
                    """
                    logger.warning("未获取到学习弱点数据")
            except Exception as e:
                logger.error(f"获取学习弱点数据失败: {str(e)}")
                results["weaknesses_info"] = """
                <div style="padding:15px;background:#f8f9fa;border-radius:5px;">
                    <h4>学习弱点分析</h4>
                    <p>获取数据时出错，请稍后再试</p>
                    <small style="color:red;">错误: {}</small>
                </div>
                """.format(str(e))
            
            # 返回所有结果
            return (
                results.get("style_chart", chart), 
                results.get("enrolled_paths", enrolled_paths.value),
                results.get("recommended_paths", recommended_paths.value),
                results.get("progress_info", progress_info.value),
                results.get("weaknesses_info", weaknesses_info.value)
            )
            
        except Exception as e:
            logger.error(f"刷新仪表盘失败: {str(e)}")
            logger.error(traceback.format_exc())
            return initial_chart, enrolled_paths.value, recommended_paths.value, progress_info.value, weaknesses_info.value
    
    # 更新按钮处理函数以包含新的输出组件
    refresh_btn.click(
        fn=refresh_dashboard,
        outputs=[learning_style_chart, enrolled_paths, recommended_paths, progress_info, weaknesses_info]
    )
    
    return enrolled_paths, recommended_paths

def create_assessment_tab(api_service, user_id):
    """创建学习风格评估标签页 - 处理真实用户输入"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 学习风格评估")
            gr.Markdown("回答以下问题，帮助我们了解您的学习风格偏好。")
            
            # 使用固定的评估问题，确保稳定性
            questions_list = [
                {
                    "id": 1,
                    "question_text": "我更喜欢通过图表和图像学习新概念。（视觉学习偏好）",
                    "question_type": "scale",
                    "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
                },
                {
                    "id": 2,
                    "question_text": "我喜欢听讲座和音频材料来学习。（听觉学习偏好）",
                    "question_type": "scale",
                    "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
                },
                {
                    "id": 3,
                    "question_text": "我通过动手实践学习效果最好。（动觉学习偏好）",
                    "question_type": "scale",
                    "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
                },
                {
                    "id": 4,
                    "question_text": "我喜欢阅读书籍和文章来学习新知识。（阅读学习偏好）",
                    "question_type": "scale",
                    "options": {"min": 1, "max": 5, "min_label": "非常不同意", "max_label": "非常同意"}
                }
            ]
            
            # 创建评估问题组件
            response_sliders = []
            for q in questions_list:
                gr.Markdown(f"**问题 {q['id']}**: {q['question_text']}")
                slider = gr.Slider(
                    minimum=q['options']['min'],
                    maximum=q['options']['max'],
                    value=3,  # 默认中间值
                    step=1,
                    label=f"{q['options']['min_label']} - {q['options']['max_label']}"
                )
                response_sliders.append(slider)
            
            submit_btn = gr.Button("提交评估", variant="primary")
            assessment_result = gr.Textbox(label="评估结果", visible=False)
            
        with gr.Column():
            gr.Markdown("### 您的学习风格")
            
            # 使用Plot组件显示学习风格
            style_chart = gr.Plot(label="学习风格分布")
            with gr.Group():
                learning_style_result = gr.HTML("完成评估后，您的学习风格将显示在这里。")
            
            gr.Markdown("### 基于您学习风格的推荐")
            with gr.Group():
                recommendations = gr.HTML("完成评估后，我们将为您提供个性化的学习建议。")
    
    # 提交评估处理函数 - 直接使用用户输入值计算学习风格
    def submit_assessment(visual_score, auditory_score, kinesthetic_score, reading_score):
        try:
            # 使用用户输入的评分计算百分比值
            visual = (visual_score / 5) * 100
            auditory = (auditory_score / 5) * 100
            kinesthetic = (kinesthetic_score / 5) * 100
            reading = (reading_score / 5) * 100
            
            # 记录用户输入值，便于调试
            logger.info(f"用户评估输入: visual={visual_score}, auditory={auditory_score}, kinesthetic={kinesthetic_score}, reading={reading_score}")
            logger.info(f"转换为百分比: visual={visual}%, auditory={auditory}%, kinesthetic={kinesthetic}%, reading={reading}%")
            
            # 构建请求数据 - 将用户输入发送到API
            assessment_data = {
                "user_id": user_id,
                "responses": [
                    {"question_id": 1, "response_value": {"answer": str(visual_score)}, "response_time": 2.5},
                    {"question_id": 2, "response_value": {"answer": str(auditory_score)}, "response_time": 3.0},
                    {"question_id": 3, "response_value": {"answer": str(kinesthetic_score)}, "response_time": 2.0},
                    {"question_id": 4, "response_value": {"answer": str(reading_score)}, "response_time": 2.5}
                ]
            }
            
            # 调用API
            try:
                loop = asyncio.new_event_loop()
                api_result = loop.run_until_complete(
                    api_service.request("POST", "assessment/submit", data=assessment_data)
                )
                loop.close()
                logger.info(f"API响应: {json.dumps(api_result, ensure_ascii=False)[:500]}")
            except Exception as e:
                logger.error(f"API调用失败: {str(e)}")
                api_result = {"error": str(e)}
            
            # 确定主要学习风格
            scores = {
                "视觉": visual,
                "听觉": auditory,
                "动觉": kinesthetic,
                "阅读": reading
            }
            
            # 找出前两个最高分
            sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            primary_style = f"{sorted_styles[0][0]}-{sorted_styles[1][0]}"
            
            # 创建学习风格图表
            chart = create_learning_style_chart(visual, auditory, kinesthetic, reading)
            
            # 生成描述文本
            description = f"您通过{sorted_styles[0][0]}({sorted_styles[0][1]:.0f}%)和{sorted_styles[1][0]}({sorted_styles[1][1]:.0f}%)方式学习效果最好。"
            
            # 生成HTML展示
            style_html = f"""
            <div style="margin-bottom:15px">
                <h4>您的学习风格分析</h4>
                <div style="display:flex;margin-top:10px">
                    <div style="flex:1">
                        <div style="font-weight:bold">视觉偏好</div>
                        <div style="background:#e9ecef;height:20px;border-radius:3px;margin-top:5px">
                            <div style="width:{visual}%;background:#4CAF50;height:100%;border-radius:3px"></div>
                        </div>
                        <div style="text-align:right">{visual:.0f}%</div>
                    </div>
                    <div style="width:20px"></div>
                    <div style="flex:1">
                        <div style="font-weight:bold">听觉偏好</div>
                        <div style="background:#e9ecef;height:20px;border-radius:3px;margin-top:5px">
                            <div style="width:{auditory}%;background:#2196F3;height:100%;border-radius:3px"></div>
                        </div>
                        <div style="text-align:right">{auditory:.0f}%</div>
                    </div>
                </div>
                <div style="display:flex;margin-top:15px">
                    <div style="flex:1">
                        <div style="font-weight:bold">动觉偏好</div>
                        <div style="background:#e9ecef;height:20px;border-radius:3px;margin-top:5px">
                            <div style="width:{kinesthetic}%;background:#FFC107;height:100%;border-radius:3px"></div>
                        </div>
                        <div style="text-align:right">{kinesthetic:.0f}%</div>
                    </div>
                    <div style="width:20px"></div>
                    <div style="flex:1">
                        <div style="font-weight:bold">阅读偏好</div>
                        <div style="background:#e9ecef;height:20px;border-radius:3px;margin-top:5px">
                            <div style="width:{reading}%;background:#9C27B0;height:100%;border-radius:3px"></div>
                        </div>
                        <div style="text-align:right">{reading:.0f}%</div>
                    </div>
                </div>
            </div>
            <p><strong>您的学习风格偏好</strong>: 您是一个<strong>{primary_style}型学习者</strong>。{description}</p>
            """
            
            # 根据学习风格生成推荐
            recommendations_map = {
                "视觉": [
                    "使用图表、思维导图和可视化工具来组织和理解信息",
                    "观看教学视频和演示",
                    "使用颜色编码和高亮来强调重点内容",
                    "绘制概念图和流程图来理解复杂概念"
                ],
                "听觉": [
                    "参加讲座和小组讨论",
                    "使用语音笔记和录音",
                    "阅读时大声朗读重要内容",
                    "与他人讨论学习内容以加深理解"
                ],
                "动觉": [
                    "通过实践和动手项目学习",
                    "使用角色扮演和模拟练习",
                    "边走边思考或学习",
                    "参与互动式学习活动和实验"
                ],
                "阅读": [
                    "通过阅读书籍、文章和书面材料学习",
                    "做笔记和总结",
                    "使用清单和步骤指南",
                    "查找和阅读不同的信息来源"
                ]
            }
            
            # 根据最高的两种学习风格推荐策略
            top_styles = [s[0] for s in sorted_styles[:2]]
            rec_items = []
            for style in top_styles:
                rec_items.extend(recommendations_map.get(style, []))
            
            rec_html = f"""
            <div style="margin-top:10px">
                <p>基于您的<strong>{primary_style}型</strong>学习风格，我们推荐以下学习策略：</p>
                <ul>
                    {"".join([f'<li>{item}</li>' for item in rec_items])}
                </ul>
            </div>
            """
            
            # 可以尝试从API获取推荐，如果失败使用本地生成的
            if "error" not in api_result and "recommendations" in api_result and api_result["recommendations"]:
                api_recs = api_result["recommendations"]
                rec_html += f"""
                <div style="margin-top:20px">
                    <p>来自API的其他推荐：</p>
                    <ul>
                        {"".join([f'<li>{item}</li>' for item in api_recs])}
                    </ul>
                </div>
                """
            
            # 生成提交状态消息
            status_msg = "评估提交成功！您的学习风格分析已更新。"
            if "error" in api_result:
                status_msg += f" (API通信错误: {api_result['error']} - 显示的是本地计算结果)"
            
            # 返回结果，更新所有组件
            return gr.update(value=status_msg, visible=True), chart, style_html, rec_html
                
        except Exception as e:
            logger.error(f"评估提交处理异常: {str(e)}")
            logger.error(traceback.format_exc())
            return gr.update(value=f"评估提交处理失败: {str(e)}", visible=True), None, "", ""
    
    # 绑定事件，提交用户输入的评估内容
    submit_btn.click(
        fn=submit_assessment,
        inputs=response_sliders,  # 直接传递四个滑块的值
        outputs=[assessment_result, style_chart, learning_style_result, recommendations]
    )
    
    return assessment_result, style_chart, learning_style_result, recommendations

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

def create_content_viewer_tab(api_service, user_id):
    """创建学习内容查看器标签页"""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 内容目录")
            content_list = gr.Radio(
                label="选择内容",
                choices=[
                    "Python安装和环境设置",
                    "变量和数据类型", 
                    "控制流语句",
                    "函数和模块",
                    "面向对象编程"
                ],
                value="变量和数据类型"
            )
            
            gr.Markdown("### 内容信息")
            content_info = gr.JSON(
                {
                    "标题": "变量和数据类型",
                    "类型": "interactive",
                    "时长": "25分钟",
                    "难度": "基础"
                },
                label="内容元数据"
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 内容查看器")
            
            content_container = gr.HTML(
                """
                <div style="border:1px solid #ccc;border-radius:5px;padding:20px">
                    <h2>变量和数据类型</h2>
                    
                    <p>Python中的变量不需要声明类型，可以直接赋值使用。基本数据类型包括：</p>
                    
                    <ul>
                        <li><strong>整数 (int)</strong>: 如 <code>x = 10</code></li>
                        <li><strong>浮点数 (float)</strong>: 如 <code>y = 3.14</code></li>
                        <li><strong>字符串 (str)</strong>: 如 <code>name = "Python"</code></li>
                        <li><strong>布尔值 (bool)</strong>: <code>True</code> 或 <code>False</code></li>
                    </ul>
                    
                    <p>复合数据类型包括：</p>
                    
                    <ul>
                        <li><strong>列表 (list)</strong>: 如 <code>my_list = [1, 2, 3]</code></li>
                        <li><strong>元组 (tuple)</strong>: 如 <code>my_tuple = (1, 2, 3)</code></li>
                        <li><strong>字典 (dict)</strong>: 如 <code>my_dict = {"key": "value"}</code></li>
                        <li><strong>集合 (set)</strong>: 如 <code>my_set = {1, 2, 3}</code></li>
                    </ul>
                    
                    <div style="margin-top:20px;background:#f8f9fa;padding:15px;border-radius:5px">
                        <h4>练习</h4>
                        <p>1. 在Python中，如何声明一个整数变量x并赋值为10？</p>
                        <div style="margin:10px 0">
                            <input type="radio" id="q1_1" name="q1"><label for="q1_1"> x = 10</label><br>
                            <input type="radio" id="q1_2" name="q1"><label for="q1_2"> int x = 10</label><br>
                            <input type="radio" id="q1_3" name="q1"><label for="q1_3"> x := 10</label><br>
                            <input type="radio" id="q1_4" name="q1"><label for="q1_4"> x <- 10</label>
                        </div>
                    </div>
                </div>
                """
            )
            
            with gr.Row():
                prev_btn = gr.Button("上一页")
                progress_indicator = gr.Slider(
                    minimum=0, maximum=100, value=40, 
                    interactive=False, label="进度"
                )
                next_btn = gr.Button("下一页")
            
            with gr.Row():
                mark_complete_btn = gr.Button("标记为完成", variant="primary")
                status_msg = gr.Textbox(label="状态", visible=False)
    
    def update_content(content_name):
        try:
            test_content = api_service._get_test_content(2)
            
            content_html = f"""
            <div style="border:1px solid #ccc;border-radius:5px;padding:20px">
                <h2>{content_name}</h2>
                
                <p>这是{content_name}的内容示例。实际应用中，这里会显示实际的学习内容。</p>
                
                <div style="margin-top:20px;background:#f8f9fa;padding:15px;border-radius:5px">
                    <h4>内容概要</h4>
                    <ul>
                        <li>主题点1</li>
                        <li>主题点2</li>
                        <li>主题点3</li>
                    </ul>
                </div>
            </div>
            """
            
            info = {
                "标题": content_name,
                "类型": "交互式",
                "时长": "25分钟",
                "难度": "基础"
            }
            
            return content_html, info
        except Exception as e:
            logger.error(f"更新内容失败: {str(e)}")
            return "加载内容失败", {"错误": str(e)}
    
    content_list.change(
        fn=update_content,
        inputs=[content_list],
        outputs=[content_container, content_info]
    )
    
    def mark_complete():
        return gr.update(value="内容已标记为完成", visible=True)
    
    def next_page():
        return gr.update(value="已跳转到下一页", visible=True)
    
    def prev_page():
        return gr.update(value="已跳转到上一页", visible=True)
    
    mark_complete_btn.click(fn=mark_complete, outputs=[status_msg])
    next_btn.click(fn=next_page, outputs=[status_msg])
    prev_btn.click(fn=prev_page, outputs=[status_msg])
    
    return content_container, content_info

def format_api_status_html(status_info):
    """格式化API状态信息为HTML"""
    status_text = f"<div class='backend-status'>"
    if status_info["status"] == "正常":
        status_text += "<span class='status-indicator status-normal'></span>"
    elif status_info["status"] == "部分可用" or status_info["status"] == "功能受限":
        status_text += "<span class='status-indicator status-partial'></span>"
    else:
        status_text += "<span class='status-indicator status-error'></span>"
    
    status_text += f"<span>{status_info['status']}</span></div>"
    status_text += f"<div>{status_info['message']}</div>"
    
    if "api_info" in status_info:
        status_text += f"<div><small>{status_info['api_info']}</small></div>"
        
    if "details" in status_info:
        status_text += "<details><summary>查看详细信息</summary><div class='detail-view'>"
        for name, info in status_info["details"].items():
            status_emoji = "✅" if info["ok"] else "❌"
            status_text += f"<div>{status_emoji} {name}: {info['status']}</div>"
        status_text += "</div></details>"
    
    return status_text

def create_adaptive_test_tab(api_service, user_id):
    """创建自适应测试标签页"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 自适应测试")
            gr.Markdown("根据您的学习进度和学习风格生成个性化测试题目。")
            
            # 测试设置
            with gr.Group():
                gr.Markdown("#### 测试设置")
                subject = gr.Dropdown(
                    label="主题领域",
                    choices=["programming", "data_science", "mathematics", "language", "other"],
                    value="programming"
                )
                topic = gr.Textbox(
                    label="具体主题", 
                    placeholder="例如：Python基础、数据可视化",
                    value="Python基础"
                )
                difficulty = gr.Dropdown(
                    label="难度级别",
                    choices=["auto", "beginner", "intermediate", "advanced"],
                    value="auto"
                )
                generate_btn = gr.Button("生成测试", variant="primary")
            
            # 测试结果
            test_result = gr.Textbox(
                label="测试结果",
                value="",
                visible=False
            )
        
        with gr.Column():
            # 测试问题区域
            test_container = gr.HTML("""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <p>点击"生成测试"按钮开始测试</p>
            </div>
            """)
            
            # 提交区域
            submit_container = gr.Group(visible=False)
            with submit_container:
                answers = gr.JSON(
                    label="答案",
                    value={}
                )
                submit_test_btn = gr.Button("提交测试", variant="primary")
    
    # 测试生成函数
    def generate_test(subject_val, topic_val, difficulty_val):
        try:
            test_request = {
                "user_id": user_id,
                "subject": subject_val,
                "topic": topic_val,
                "difficulty": difficulty_val
            }
            
            # 调用API
            loop = asyncio.new_event_loop()
            test_result = loop.run_until_complete(
                api_service.request("POST", "assessment/adaptive-test", data=test_request)
            )
            loop.close()
            
            if "error" in test_result:
                return (
                    gr.update(value=f"生成测试失败: {test_result['error']}", visible=True),
                    f"""
                    <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                        <p>生成测试失败，请稍后再试</p>
                        <p>错误: {test_result['error']}</p>
                    </div>
                    """,
                    gr.update(visible=False),
                    {}
                )
            
            # 处理测试问题
            questions = test_result.get("questions", [])
            if not questions:
                return (
                    gr.update(value="生成测试失败: 未返回任何问题", visible=True),
                    """
                    <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                        <p>未能生成任何测试问题，请尝试其他主题或难度</p>
                    </div>
                    """,
                    gr.update(visible=False),
                    {}
                )
            
            # 创建测试HTML
            estimated_difficulty = test_result.get("estimated_difficulty", "未知")
            topics_covered = test_result.get("topics_covered", [])
            
            test_html = f"""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h3>测试信息</h3>
                <p><strong>主题:</strong> {topic_val}</p>
                <p><strong>难度:</strong> {estimated_difficulty}</p>
                <p><strong>问题数量:</strong> {len(questions)}</p>
            """
            
            if topics_covered:
                test_html += "<p><strong>涵盖的主题:</strong> " + ", ".join(topics_covered) + "</p>"
            
            test_html += """
                <hr>
                <h3>测试问题</h3>
                <form id="test-form">
            """
            
            # 生成问题HTML
            answers_data = {}
            for i, q in enumerate(questions):
                q_id = q.get("id", i+1)
                q_content = q.get("content", f"问题 {q_id}")
                q_type = q.get("question_type", "choice")
                q_options = q.get("options", [])
                
                test_html += f"""
                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                    <p><strong>问题 {i+1}:</strong> {q_content}</p>
                """
                
                if q_type == "choice" and q_options:
                    test_html += "<div style='margin-top: 10px;'>"
                    for j, option in enumerate(q_options):
                        option_id = f"q{i+1}_opt{j+1}"
                        test_html += f"""
                        <div style="margin: 5px 0;">
                            <input type="radio" id="{option_id}" name="q{i+1}" value="{j}" onclick="window.updateTestAnswer({q_id}, {j})">
                            <label for="{option_id}"> {option}</label>
                        </div>
                        """
                    test_html += "</div>"
                    
                    # 添加答案数据
                    answers_data[str(q_id)] = {
                        "question_id": q_id,
                        "selected_option": None
                    }
                elif q_type == "text":
                    test_html += f"""
                    <div style="margin-top: 10px;">
                        <textarea id="q{i+1}_answer" rows="3" style="width: 100%; padding: 5px;"
                            placeholder="输入您的答案..." oninput="window.updateTextTestAnswer({q_id}, this.value)"></textarea>
                    </div>
                    """
                    
                    # 添加答案数据
                    answers_data[str(q_id)] = {
                        "question_id": q_id,
                        "text_answer": ""
                    }
                
                test_html += "</div>"
            
            test_html += """
                </form>
            </div>
            
            <script>
                // 定义全局函数，方便从HTML直接调用
                window.testAnswers = {};
                
                window.updateTestAnswer = function(questionId, optionIndex) {
                    console.log("选择了问题 " + questionId + " 的选项 " + optionIndex);
                    // 存储到全局变量
                    window.testAnswers[questionId] = optionIndex;
                    
                    // 将答案数据更新到隐藏文本区域
                    try {
                        const answersTextarea = document.querySelector('textarea[data-testid="answers"]');
                        if (!answersTextarea) {
                            console.error("找不到答案文本区域");
                            return;
                        }
                        
                        let answersData = JSON.parse(answersTextarea.value);
                        if (answersData[questionId]) {
                            answersData[questionId].selected_option = optionIndex;
                            answersTextarea.value = JSON.stringify(answersData);
                            
                            // 通过模拟输入事件触发Gradio状态更新
                            answersTextarea.dispatchEvent(new Event('input', {bubbles: true}));
                            console.log("已更新答案数据:", answersData);
                        }
                    } catch (error) {
                        console.error("更新答案时出错:", error);
                    }
                };
                
                window.updateTextTestAnswer = function(questionId, text) {
                    console.log("输入了问题 " + questionId + " 的文本答案");
                    
                    // 将答案数据更新到隐藏文本区域
                    try {
                        const answersTextarea = document.querySelector('textarea[data-testid="answers"]');
                        if (!answersTextarea) {
                            console.error("找不到答案文本区域");
                            return;
                        }
                        
                        let answersData = JSON.parse(answersTextarea.value);
                        if (answersData[questionId]) {
                            answersData[questionId].text_answer = text;
                            answersTextarea.value = JSON.stringify(answersData);
                            
                            // 通过模拟输入事件触发Gradio状态更新
                            answersTextarea.dispatchEvent(new Event('input', {bubbles: true}));
                            console.log("已更新文本答案数据");
                        }
                    } catch (error) {
                        console.error("更新文本答案时出错:", error);
                    }
                };
                
                // 添加观察器，确保Gradio重新渲染后能找到元素
                const observer = new MutationObserver(function(mutations) {
                    for (const mutation of mutations) {
                        if (mutation.addedNodes.length) {
                            // 查找是否有新的textarea被添加
                            const answersTextarea = document.querySelector('textarea[data-testid="answers"]');
                            if (answersTextarea) {
                                console.log("找到答案文本区域，初始化测试数据");
                                if (answersTextarea.value) {
                                    window.testAnswers = JSON.parse(answersTextarea.value);
                                }
                                // 找到后就不需要继续观察
                                observer.disconnect();
                                break;
                            }
                        }
                    }
                });
                
                // 开始观察document.body
                observer.observe(document.body, {childList: true, subtree: true});
                
                // 调试信息
                console.log("测试脚本已加载");
            </script>
            """
            
            return (
                gr.update(value="测试生成成功，请作答后提交", visible=True),
                test_html,
                gr.update(visible=True),
                answers_data
            )
            
        except Exception as e:
            logger.error(f"生成测试失败: {str(e)}")
            logger.error(traceback.format_exc())
            return (
                gr.update(value=f"生成测试异常: {str(e)}", visible=True),
                f"""
                <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                    <p>生成测试时发生错误</p>
                    <p>错误: {str(e)}</p>
                </div>
                """,
                gr.update(visible=False),
                {}
            )
    
    # 测试提交函数
    def submit_test(answers_data):
        try:
            if not answers_data:
                return gr.update(value="提交失败: 未找到任何答案", visible=True)
            
            # 增加日志记录，帮助调试
            logger.info(f"提交测试答案: {json.dumps(answers_data, ensure_ascii=False)}")
            
            # 构建提交数据
            submit_data = {
                "user_id": user_id,
                "answers": []
            }
            
            # 处理答案
            for q_id, answer_info in answers_data.items():
                answer_item = {"question_id": answer_info["question_id"]}
                
                if "selected_option" in answer_info and answer_info["selected_option"] is not None:
                    answer_item["answer"] = answer_info["selected_option"]
                elif "text_answer" in answer_info and answer_info["text_answer"]:
                    answer_item["answer"] = answer_info["text_answer"]
                else:
                    continue  # 跳过未回答的问题
                
                submit_data["answers"].append(answer_item)
            
            if not submit_data["answers"]:
                return gr.update(value="提交失败: 请至少回答一道题", visible=True)
            
            # 输出构建的提交数据
            logger.info(f"构建的提交数据: {json.dumps(submit_data, ensure_ascii=False)}")
            
            # 调用API
            loop = asyncio.new_event_loop()
            submit_result = loop.run_until_complete(
                api_service.request("POST", "assessment/submit-test", data=submit_data)
            )
            loop.close()
            
            if "error" in submit_result:
                return gr.update(value=f"提交测试失败: {submit_result['error']}", visible=True)
            
            score = submit_result.get("score", 0)
            feedback = submit_result.get("feedback", "")
            return gr.update(value=f"测试提交成功！得分: {score}/100\n\n{feedback}", visible=True)
            
        except Exception as e:
            logger.error(f"提交测试失败: {str(e)}")
            logger.error(traceback.format_exc())
            return gr.update(value=f"提交测试异常: {str(e)}", visible=True)
    
    # 绑定按钮事件
    generate_btn.click(
        fn=generate_test,
        inputs=[subject, topic, difficulty],
        outputs=[test_result, test_container, submit_container, answers]
    )
    
    submit_test_btn.click(
        fn=submit_test,
        inputs=[answers],
        outputs=[test_result]
    )
    
    return test_result, test_container

def create_analytics_tab(api_service, user_id):
    """创建学习分析标签页"""
    with gr.Tabs() as analytics_tabs:
        with gr.TabItem("学习行为分析"):
            gr.Markdown("### 学习行为分析")
            gr.Markdown("分析您的学习行为模式，帮助您理解自己的学习习惯。")
            
            # 行为分析结果
            behavior_result = gr.HTML("""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <p>点击"分析学习行为"按钮开始分析</p>
            </div>
            """)
            
            analyze_btn = gr.Button("分析学习行为", variant="primary")
        
        with gr.TabItem("学习弱点分析"):
            gr.Markdown("### 学习弱点分析")
            gr.Markdown("识别您的学习弱点，并提供有针对性的改进建议。")
            
            # 弱点分析结果
            weaknesses_result = gr.HTML("""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <p>点击"识别学习弱点"按钮开始分析</p>
            </div>
            """)
            
            weaknesses_btn = gr.Button("识别学习弱点", variant="primary")
        
        with gr.TabItem("学习进度分析"):
            gr.Markdown("### 学习进度分析")
            gr.Markdown("跟踪您的学习进度，分析学习效果。")
            
            # 进度分析结果
            progress_result = gr.HTML("""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <p>点击"获取学习进度"按钮开始分析</p>
            </div>
            """)
            
            progress_btn = gr.Button("获取学习进度", variant="primary")
    
    # 分析学习行为
    def analyze_behavior():
        try:
            # 构造学习行为数据
            behavior_data = {
                "user_id": user_id,
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
            
            # 调用API
            loop = asyncio.new_event_loop()
            behavior_result = loop.run_until_complete(
                api_service.request("POST", "analytics/behavior", data=behavior_data)
            )
            loop.close()
            
            if "error" in behavior_result:
                return f"""
                <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                    <h4>分析失败</h4>
                    <p>错误: {behavior_result['error']}</p>
                </div>
                """
            
            # 处理结果
            engagement = behavior_result.get("engagement_level", "中等")
            patterns = behavior_result.get("behavior_patterns", {})
            areas = behavior_result.get("improvement_areas", [])
            
            result_html = f"""
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h4>学习行为分析结果</h4>
                
                <div style="display: flex; margin: 20px 0;">
                    <div style="flex: 1; text-align: center; padding: 15px; background: #e9f7ef; border-radius: 5px; margin-right: 10px;">
                        <h5>参与度</h5>
                        <div style="font-size: 2em; font-weight: bold;">{engagement}</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h5>行为模式</h5>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            """
            
            for pattern, value in patterns.items():
                result_html += f"""
                <div style="flex: 1; min-width: 200px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <strong>{pattern}</strong>
                    <p>{value}</p>
                </div>
                """
            
            result_html += """
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h5>改进领域</h5>
                    <ul>
            """
            
            for area in areas:
                result_html += f"<li>{area}</li>"
            
            result_html += """
                    </ul>
                </div>
            </div>
            """
            
            return result_html
        except Exception as e:
            logger.error(f"分析学习行为失败: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""
            <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                <h4>发生错误</h4>
                <p>分析学习行为时发生异常: {str(e)}</p>
            </div>
            """
    
    # 识别学习弱点
    def identify_weaknesses():
        try:
            # 调用API
            loop = asyncio.new_event_loop()
            weaknesses_result = loop.run_until_complete(
                api_service.request("GET", f"analytics/weaknesses/{user_id}")
            )
            loop.close()
            
            if "error" in weaknesses_result:
                return f"""
                <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                    <h4>分析失败</h4>
                    <p>错误: {weaknesses_result['error']}</p>
                </div>
                """
            
            # 处理结果
            weak_areas = weaknesses_result.get("weak_areas", [])
            strength_areas = weaknesses_result.get("strength_areas", [])
            improvement_plan = weaknesses_result.get("improvement_plan", {})
            
            result_html = """
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h4>学习弱点分析结果</h4>
            """
            
            # 弱点区域
            if weak_areas:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>需要加强的领域</h5>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """
                
                for area in weak_areas:
                    topic = area.get("topic", "未知")
                    confidence = area.get("confidence_level", 0)
                    resources = area.get("suggested_resources", [])
                    
                    result_html += f"""
                    <div style="flex: 1; min-width: 200px; padding: 15px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                        <h6>{topic}</h6>
                        <div style="margin: 10px 0;">
                            <div>掌握程度: {confidence}%</div>
                            <div style="background: #e9ecef; height: 10px; border-radius: 5px; margin-top: 5px;">
                                <div style="width: {confidence}%; background: #ffc107; height: 100%; border-radius: 5px;"></div>
                            </div>
                        </div>
                    """
                    
                    if resources:
                        result_html += "<div><strong>建议资源:</strong><ul>"
                        for resource in resources[:3]:  # 最多显示3个
                            result_html += f"<li>{resource}</li>"
                        result_html += "</ul></div>"
                    
                    result_html += "</div>"
                
                result_html += """
                    </div>
                </div>
                """
            
            # 强项区域
            if strength_areas:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>您的强项领域</h5>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """
                
                for area in strength_areas:
                    topic = area.get("topic", "未知")
                    confidence = area.get("confidence_level", 0)
                    
                    result_html += f"""
                    <div style="flex: 1; min-width: 150px; padding: 15px; background: #d1e7dd; border-radius: 5px; border-left: 4px solid #198754;">
                        <h6>{topic}</h6>
                        <div style="margin: 10px 0;">
                            <div>掌握程度: {confidence}%</div>
                            <div style="background: #e9ecef; height: 10px; border-radius: 5px; margin-top: 5px;">
                                <div style="width: {confidence}%; background: #198754; height: 100%; border-radius: 5px;"></div>
                            </div>
                        </div>
                    </div>
                    """
                
                result_html += """
                    </div>
                </div>
                """
            
            # 改进计划
            if improvement_plan:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>个性化改进计划</h5>
                    <ol style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                """
                
                for step, description in improvement_plan.items():
                    result_html += f"<li><strong>{step}</strong>: {description}</li>"
                
                result_html += """
                    </ol>
                </div>
                """
            
            result_html += "</div>"
            return result_html
        except Exception as e:
            logger.error(f"识别学习弱点失败: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""
            <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                <h4>发生错误</h4>
                <p>识别学习弱点时发生异常: {str(e)}</p>
            </div>
            """
    
    # 获取学习进度
    def get_progress():
        try:
            # 调用API
            loop = asyncio.new_event_loop()
            progress_result = loop.run_until_complete(
                api_service.request("GET", f"assessment/progress/{user_id}")
            )
            loop.close()
            
            if "error" in progress_result:
                return f"""
                <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                    <h4>获取失败</h4>
                    <p>错误: {progress_result['error']}</p>
                </div>
                """
            
            # 处理结果
            learning_style = progress_result.get("current_learning_style", {})
            metrics = progress_result.get("progress_metrics", {})
            suggestions = progress_result.get("improvement_suggestions", [])
            
            result_html = """
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h4>学习进度分析</h4>
            """
            
            # 学习风格
            if learning_style:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>当前学习风格</h5>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """
                
                for style, value in learning_style.items():
                    if isinstance(value, (int, float)):
                        result_html += f"""
                        <div style="flex: 1; min-width: 120px; padding: 10px; text-align: center; background: #f8f9fa; border-radius: 5px;">
                            <div>{style}</div>
                            <div style="font-size: 1.5em; font-weight: bold;">{value}%</div>
                        </div>
                        """
                
                result_html += """
                    </div>
                </div>
                """
            
            # 进度指标
            if metrics:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>进度指标</h5>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """
                
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        result_html += f"""
                        <div style="flex: 1; min-width: 150px; padding: 15px; background: #e9f7ef; border-radius: 5px;">
                            <div>{metric_name}</div>
                            <div style="font-size: 1.8em; font-weight: bold;">{metric_value}</div>
                        </div>
                        """
                    elif isinstance(metric_value, str):
                        result_html += f"""
                        <div style="flex: 1; min-width: 150px; padding: 15px; background: #e9f7ef; border-radius: 5px;">
                            <div>{metric_name}</div>
                            <div style="font-size: 1.2em; margin-top: 5px;">{metric_value}</div>
                        </div>
                        """
                
                result_html += """
                    </div>
                </div>
                """
            
            # 改进建议
            if suggestions:
                result_html += """
                <div style="margin-top: 20px;">
                    <h5>改进建议</h5>
                    <ul style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                """
                
                for suggestion in suggestions:
                    result_html += f"<li>{suggestion}</li>"
                
                result_html += """
                    </ul>
                </div>
                """
            
            result_html += "</div>"
            return result_html
        except Exception as e:
            logger.error(f"获取学习进度失败: {str(e)}")
            logger.error(traceback.format_exc())
            return f"""
            <div style="padding: 20px; border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da; color: #721c24;">
                <h4>发生错误</h4>
                <p>获取学习进度时发生异常: {str(e)}</p>
            </div>
            """
    
    # 绑定按钮事件
    analyze_btn.click(
        fn=analyze_behavior,
        outputs=[behavior_result]
    )
    
    weaknesses_btn.click(
        fn=identify_weaknesses,
        outputs=[weaknesses_result]
    )
    
    progress_btn.click(
        fn=get_progress,
        outputs=[progress_result]
    )
    
    return behavior_result, weaknesses_result, progress_result
