#!/usr/bin/env python
"""
设置测试环境 - 安装所需的依赖并准备测试目录
"""
import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """创建必要的目录结构"""
    dirs = [
        "logs",
        "tests/reports"
    ]
    
    print("创建必要的目录...")
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True, parents=True)
        print(f"  ✓ 创建目录: {dir_path}")

def install_dependencies():
    """安装测试所需的Python依赖"""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-xdist",
        "httpx",
        "zhipuai"
    ]
    
    print("安装必要的Python包...")
    
    # 确认当前Python解释器路径
    python_executable = sys.executable
    print(f"使用Python解释器: {python_executable}")
    
    # 显示当前Python路径
    print(f"Python路径: {sys.path}")
    
    # 尝试多种安装方式
    pip_commands = [
        [python_executable, "-m", "pip", "install"],  # 标准pip方式
        ["pip", "install"],                         # 直接pip命令
        ["pip3", "install"]                         # pip3命令
    ]
    
    for package in required_packages:
        print(f"\n安装 {package}...")
        installed = False
        
        for pip_cmd in pip_commands:
            try:
                cmd = pip_cmd + [package]
                print(f"尝试命令: {' '.join(cmd)}")
                subprocess.check_call(cmd)
                print(f"  ✓ 成功安装: {package}")
                installed = True
                break
            except subprocess.CalledProcessError as e:
                print(f"  - 命令失败: {e}")
            except Exception as e:
                print(f"  - 错误: {e}")
        
        if not installed:
            print(f"  ✗ 无法安装 {package}，请手动安装")

def check_dependencies():
    """检查依赖是否可用"""
    dependencies = ["pytest", "zhipuai"]
    
    print("\n检查依赖是否可用...")
    all_available = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep} 已安装且可用")
        except ImportError:
            print(f"  ✗ {dep} 不可用或未安装")
            all_available = False
    
    return all_available

def check_api_key():
    """检查API密钥是否已配置"""
    try:
        from app.core.config import settings
        
        if not settings.ZHIPU_API_KEY:
            print("\n警告: 未在配置中找到ZHIPU_API_KEY")
            print("您可以通过以下方式设置API密钥:")
            print("1. 在环境变量中设置 ZHIPU_API_KEY")
            print("2. 在 .env 文件中设置 ZHIPU_API_KEY=your-api-key")
            print("3. 直接在 app/core/config.py 修改设置")
        else:
            print("\n✓ API密钥已配置")
    except ImportError as e:
        print(f"\n无法检查API密钥: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("设置智谱AI测试环境")
    print("=" * 50)
    
    # 添加项目根目录到Python路径
    ROOT_DIR = Path(__file__).resolve().parent
    sys.path.append(str(ROOT_DIR))
    
    # 创建必要的目录
    create_directories()
    
    # 安装依赖
    install_dependencies()
    
    # 检查依赖
    deps_available = check_dependencies()
    
    # 检查API密钥
    check_api_key()
    
    print("\n环境设置结果:")
    if deps_available:
        print("✓ 所有依赖已成功安装")
    else:
        print("✗ 某些依赖安装失败，请手动安装缺失的依赖")
        print("  推荐命令: pip install pytest pytest-asyncio pytest-xdist httpx zhipuai")
    
    print("\n您可以运行测试:")
    print("1. 运行简单测试: python quick_test.py")
    print("2. 运行所有测试: python run_tests.py")

if __name__ == "__main__":
    main()
