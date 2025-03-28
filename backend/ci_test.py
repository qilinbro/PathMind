#!/usr/bin/env python
"""
CI/CD测试脚本 - 用于自动化测试管道
使用方式: python ci_test.py --env [dev|staging|prod]
"""
import argparse
import sys
import os
import asyncio
from pathlib import Path

# 设置环境
def setup_environment(env_type):
    """设置测试环境变量"""
    os.environ["TEST_ENV"] = env_type
    os.environ["ZHIPU_API_TIMEOUT"] = "10"  # 10秒超时
    
    # 在CI环境中使用测试API密钥
    if env_type != "prod":
        os.environ["ZHIPU_API_KEY"] = os.environ.get("ZHIPU_TEST_API_KEY", "")

# 运行测试套件
async def run_tests(env_type):
    """运行测试套件"""
    from scripts.test_zhipuai import main as run_zhipu_tests
    
    print(f"在 {env_type} 环境运行智谱AI测试...")
    await run_zhipu_tests()
    
    # 可以添加其他测试套件

# 主函数
def main():
    parser = argparse.ArgumentParser(description="运行CI/CD测试")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], 
                        default="dev", help="测试环境")
    args = parser.parse_args()
    
    # 将项目根目录添加到Python路径
    ROOT_DIR = Path(__file__).resolve().parent
    sys.path.append(str(ROOT_DIR))
    
    # 设置环境
    setup_environment(args.env)
    
    # 运行测试
    asyncio.run(run_tests(args.env))

if __name__ == "__main__":
    main()
