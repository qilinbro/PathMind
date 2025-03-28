#!/usr/bin/env python
"""
测试运行脚本 - 运行所有智谱AI集成测试
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_environment():
    """检查测试环境是否正确配置"""
    try:
        import pytest
        import zhipuai
        print("✓ 测试环境已正确配置")
        return True
    except ImportError as e:
        print(f"✗ 环境配置不完整: {e}")
        print("请先运行 'python setup_test_env.py' 设置环境")
        return False

def run_pytest(verbose=False, test_file=None):
    """运行pytest测试"""
    # 确保当前Python解释器正确
    python_executable = sys.executable
    
    cmd = [python_executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if test_file:
        cmd.append(test_file)
    else:
        cmd.append("tests/test_zhipuai_integration.py")
    
    print(f"执行命令: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"运行测试失败: {e}")
        print("提示: 尝试手动运行 'python -m pytest tests/test_zhipuai_integration.py'")

def run_manual_test(script_name):
    """运行手动测试脚本"""
    script_path = f"scripts/{script_name}"
    if not Path(script_path).exists():
        print(f"错误: 脚本 {script_path} 不存在")
        return
    
    python_executable = sys.executable
    cmd = [python_executable, script_path]
    print(f"执行命令: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"运行脚本失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="运行智谱AI集成测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--pytest", action="store_true", help="运行pytest测试")
    parser.add_argument("--manual", action="store_true", help="运行手动测试脚本")
    parser.add_argument("--batch", action="store_true", help="运行批量测试")
    parser.add_argument("--quick", action="store_true", help="运行快速测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 默认运行所有测试
    if not (args.pytest or args.manual or args.batch or args.quick):
        args.quick = True  # 默认运行快速测试
    
    # 添加项目根目录到Python路径
    ROOT_DIR = Path(__file__).resolve().parent
    sys.path.append(str(ROOT_DIR))
    
    if args.quick:
        print("\n=== 运行快速测试 ===")
        cmd = [sys.executable, "quick_test.py"]
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
        return
        
    # 检查环境
    if not check_environment():
        return
    
    if args.all or args.pytest:
        print("\n=== 运行pytest测试 ===")
        run_pytest(verbose=args.verbose)
    
    if args.all or args.manual:
        print("\n=== 运行手动测试脚本 ===")
        run_manual_test("test_zhipuai.py")
    
    if args.all or args.batch:
        print("\n=== 运行批量测试 ===")
        run_manual_test("batch_test_ai_features.py")

if __name__ == "__main__":
    main()
