"""
学习分析页面组件
"""
import gradio as gr
import logging
import asyncio
import json
import traceback

# 设置日志
logger = logging.getLogger(__name__)

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
