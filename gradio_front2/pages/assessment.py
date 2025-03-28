"""
学习风格评估页面组件
"""
import gradio as gr
import logging
import asyncio
import json
import traceback
from utils.chart_utils import create_learning_style_chart

# 设置日志
logger = logging.getLogger(__name__)

def create_assessment_tab(api_service, user_id):
    """创建学习风格评估标签页 - 处理真实用户输入"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 学习风格评估")
            gr.Markdown("回答以下问题，帮助我们了解您的学习风格偏好。")
            
            # 问题定义
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
            
            style_chart = gr.Plot(label="学习风格分布")
            learning_style_result = gr.HTML("完成评估后，您的学习风格将显示在这里。")
            
            gr.Markdown("### 基于您学习风格的推荐")
            recommendations = gr.HTML("完成评估后，我们将为您提供个性化的学习建议。")
    
    # 提交评估处理函数
    def submit_assessment(visual_score, auditory_score, kinesthetic_score, reading_score):
        try:
            # 使用用户输入的评分计算百分比值
            visual = (visual_score / 5) * 100
            auditory = (auditory_score / 5) * 100
            kinesthetic = (kinesthetic_score / 5) * 100
            reading = (reading_score / 5) * 100
            
            logger.info(f"用户评估输入: visual={visual_score}, auditory={auditory_score}, kinesthetic={kinesthetic_score}, reading={reading_score}")
            logger.info(f"转换为百分比: visual={visual}%, auditory={auditory}%, kinesthetic={kinesthetic}%, reading={reading}%")
            
            # 构建请求数据
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
            
            # 生成HTML展示和推荐内容
            style_html = generate_style_html(visual, auditory, kinesthetic, reading, primary_style, description)
            rec_html = generate_recommendations_html(sorted_styles, api_result)
            
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
        inputs=response_sliders,
        outputs=[assessment_result, style_chart, learning_style_result, recommendations]
    )
    
    return assessment_result, style_chart, learning_style_result, recommendations

# 辅助函数: 生成学习风格HTML
def generate_style_html(visual, auditory, kinesthetic, reading, primary_style, description):
    return f"""
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

# 辅助函数: 生成推荐内容HTML
def generate_recommendations_html(sorted_styles, api_result):
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
        <p>基于您的<strong>{'-'.join(top_styles)}型</strong>学习风格，我们推荐以下学习策略：</p>
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
    
    return rec_html
