"""
图表生成工具
"""
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from matplotlib import font_manager as fm

matplotlib.use('Agg')  # 使用非交互式后端
# 设置中文字体
font_path = "C:\\Users\\77139\\AppData\\Local\\Microsoft\\Windows\\Fonts\\SourceHanSansSC-Regular.otf"
my_font = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = my_font.get_name()

# 设置日志
logger = logging.getLogger(__name__)

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
