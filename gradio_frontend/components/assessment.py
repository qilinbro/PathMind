import gradio as gr
import time
from typing import List, Dict, Any

def create_assessment_tab(api_service, user_id):
    """创建学习风格评估选项卡"""
    
    # 状态变量
    assessment_state = gr.State({
        "current_question_index": 0,
        "questions": [],
        "responses": [],
        "start_time": 0,
        "assessment_complete": False
    })
    
    # 获取问题列表
    def load_questions():
        questions = api_service.get_assessment_questions()
        if isinstance(questions, list) and questions:
            return {
                "current_question_index": 0,
                "questions": questions,
                "responses": [],
                "start_time": time.time(),
                "assessment_complete": False
            }
        else:
            return {
                "current_question_index": 0,
                "questions": [],
                "responses": [],
                "start_time": 0,
                "assessment_complete": False,
                "error": "无法加载评估问题"
            }
    
    # 处理用户回答
    def handle_response(value, state):
        if not state["questions"]:
            return state, "没有评估问题可用", gr.update(visible=False), gr.update(visible=True)
        
        current_question = state["questions"][state["current_question_index"]]
        
        # 记录回答
        state["responses"].append({
            "question_id": current_question["id"],
            "response_value": {"answer": str(value)},
            "response_time": time.time() - state["start_time"]
        })
        
        # 更新状态
        state["start_time"] = time.time()
        state["current_question_index"] += 1
        
        # 检查是否完成所有问题
        if state["current_question_index"] >= len(state["questions"]):
            # 提交回答并获取结果
            result = api_service.submit_assessment(user_id, state["responses"])
            state["assessment_complete"] = True
            state["result"] = result
            
            # 生成结果显示
            result_html = generate_result_html(result)
            
            return state, result_html, gr.update(visible=False), gr.update(visible=True)
        else:
            # 显示下一个问题
            next_question = state["questions"][state["current_question_index"]]
            return state, format_question(next_question), gr.update(visible=True), gr.update(visible=False)
    
    # 格式化问题显示
    def format_question(question):
        return f"""### {question["question_text"]}
        
问题 {question["id"]} / (类别: {question["category"]})
        
请选择最符合您的选项 (1-5分):
1 - 完全不符合
5 - 非常符合
"""
    
    # 生成结果HTML
    def generate_result_html(result):
        if isinstance(result, dict) and "learning_style_result" in result:
            style_result = result["learning_style_result"]
            
            html = f"""
            <div style="padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                <h2 style="text-align: center;">您的学习风格分析结果</h2>
                
                <h3>学习风格分数</h3>
                <div style="margin: 20px 0;">
                    <div style="margin-bottom: 10px;">
                        <span>视觉学习 (Visual): {style_result["visual_score"]:.1f}%</span>
                        <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="background-color: #0d6efd; width: {style_result["visual_score"]}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span>听觉学习 (Auditory): {style_result["auditory_score"]:.1f}%</span>
                        <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="background-color: #198754; width: {style_result["auditory_score"]}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span>动觉学习 (Kinesthetic): {style_result["kinesthetic_score"]:.1f}%</span>
                        <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="background-color: #dc3545; width: {style_result["kinesthetic_score"]}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span>阅读学习 (Reading): {style_result["reading_score"]:.1f}%</span>
                        <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="background-color: #ffc107; width: {style_result["reading_score"]}%; height: 10px; border-radius: 5px;"></div>
                        </div>
                    </div>
                </div>
                
                <div style="background-color: #e6f7ff; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <h3>主导学习风格: {style_result["dominant_style"].capitalize()}</h3>
                    {f'<p>次要学习风格: {style_result["secondary_style"].capitalize() if "secondary_style" in style_result and style_result["secondary_style"] else "无"}</p>' if "secondary_style" in style_result else ""}
                </div>
                
                <h3 style="margin-top: 30px;">个性化推荐</h3>
                <div>
            """
            
            # 添加推荐内容
            if "recommendations" in result and result["recommendations"]:
                for i, rec in enumerate(result["recommendations"]):
                    html += f"""
                    <div style="background-color: #ffffff; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h4>{rec["title"]}</h4>
                        <p>{rec["description"]}</p>
                        <span style="color: #6c757d; font-size: 0.9em;">推荐匹配度: {rec.get("match_score", 0) * 100:.0f}%</span>
                    </div>
                    """
            else:
                html += "<p>暂无个性化推荐</p>"
            
            html += """
                </div>
            </div>
            """
            
            return html
        else:
            return "评估结果获取失败，请重试。"
    
    # 重新开始评估
    def restart_assessment():
        return load_questions(), "", gr.update(visible=True), gr.update(visible=False)
        
    # 处理开始评估并更新UI
    def handle_start_assessment():
        state = load_questions()
        if state.get("questions", []):
            question_text = format_question(state["questions"][0])
            return state, question_text, gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        else:
            return state, "无法加载问题", gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)
    
    # 创建UI组件
    with gr.Column():
        with gr.Group():
            gr.Markdown("## 学习风格评估")
            gr.Markdown("完成以下评估问题，我们将分析您的学习风格偏好，并提供个性化学习建议。")
            
            # 介绍内容
            intro_md = gr.Markdown("""
            ### 学习风格评估介绍
            
            这个评估将帮助您了解自己的学习偏好，包括:
            
            - 视觉学习 (Visual) - 通过看、观察和图像学习
            - 听觉学习 (Auditory) - 通过听取和讨论学习
            - 动觉学习 (Kinesthetic) - 通过实践和动手操作学习
            - 阅读学习 (Reading) - 通过阅读和写作学习
            
            完成评估后，系统将生成您的学习风格分析，并提供个性化学习建议。
            
            点击下方按钮开始评估:
            """)
            
            # 开始按钮
            start_btn = gr.Button("开始评估", variant="primary")
            
            # 问题显示和回答区域
            question_md = gr.Markdown(visible=False)
            response_slider = gr.Slider(
                minimum=1, 
                maximum=5, 
                step=1, 
                label="您的回答", 
                visible=False,
            )
            submit_btn = gr.Button("提交回答", variant="primary", visible=False)
            
            # 结果显示
            result_html = gr.HTML(visible=False)
            restart_btn = gr.Button("重新评估", variant="secondary", visible=False)
    
    # 事件处理    
    # 修复重复的 outputs 参数错误
    start_btn.click(
        fn=handle_start_assessment,
        outputs=[assessment_state, question_md, response_slider, submit_btn, start_btn, intro_md]
    )
    
    submit_btn.click(
        fn=handle_response,
        inputs=[response_slider, assessment_state],
        outputs=[assessment_state, question_md, submit_btn, result_html]
    )
    
    restart_btn.click(
        fn=restart_assessment,
        outputs=[assessment_state, result_html, start_btn, result_html]
    )
    
    return assessment_state
