#!/usr/bin/env python
"""
直接测试智谱AI API 
这个简单脚本避免了对pytest等测试框架的依赖
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

def test_imports():
    """测试导入必要的模块"""
    print("测试导入必要的模块...")
    try:
        import zhipuai
        print("✓ 成功导入 zhipuai")
    except ImportError as e:
        print(f"✗ 导入zhipuai失败: {e}")
        print("  请确保已安装: pip install zhipuai")
        return False
    
    try:
        from app.core.config import settings
        print("✓ 成功导入 app.core.config")
        print(f"  API密钥状态: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
        return True
    except ImportError as e:
        print(f"✗ 导入app.core.config失败: {e}")
        return False

async def test_direct_api():
    """直接测试智谱AI API"""
    try:
        from zhipuai import ZhipuAI
        from app.core.config import settings
        
        api_key = settings.ZHIPU_API_KEY
        if not api_key:
            print("✗ 未配置API密钥，无法进行API测试")
            return
        
        print("\n执行简单API调用...")
        client = ZhipuAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="glm-4-plus",  # 如果需要，可以改为其他可用模型
            messages=[
                {"role": "user", "content": "用一句话解释什么是人工智能"}
            ]
        )
        
        print("\n调用结果:")
        print(f"模型: {response.model}")
        print(f"内容: {response.choices[0].message.content}")
        print("\n✓ API调用成功!")
        return True
    except Exception as e:
        print(f"\n✗ API调用失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("智谱AI简单测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n导入测试失败，无法继续测试")
        return
    
    # 测试API
    try:
        asyncio.run(test_direct_api())
    except Exception as e:
        print(f"API测试出错: {e}")

if __name__ == "__main__":
    main()
