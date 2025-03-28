"""
学习内容查看器页面组件
"""
import gradio as gr
import logging

# 设置日志
logger = logging.getLogger(__name__)

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
