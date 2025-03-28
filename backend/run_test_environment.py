#!/usr/bin/env python
"""
启动测试环境并运行全流程测试
"""
import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

def start_server(port=8000):
    """启动FastAPI服务器"""
    print(f"启动服务器在端口 {port}...")
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 打开日志文件
    stdout_log = open("logs/server_stdout.log", "w")
    stderr_log = open("logs/server_stderr.log", "w")
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
        stdout=stdout_log,
        stderr=stderr_log
    )
    
    # 等待服务器启动
    print("服务器启动中，请等待...")
    for i in range(10):
        time.sleep(1)
        print(f"等待服务器启动... {i+1}/10")
        
        # 尝试连接服务器
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:{port}/health"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and "healthy" in result.stdout:
                print(f"服务器已成功启动在端口 {port}!")
                return server_process, stdout_log, stderr_log
        except Exception:
            pass
    
    print("警告: 服务器可能未正确启动，但将继续测试")
    return server_process, stdout_log, stderr_log

def run_test():
    """运行全流程测试"""
    print("运行全流程测试...")
    print("=" * 50)
    print("直接执行测试脚本输出:")
    print("=" * 50)
    
    # 使用实时输出的方式运行脚本
    process = subprocess.Popen(
        [sys.executable, "scripts/test_full_flow.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # 实时显示输出
    for line in iter(process.stdout.readline, ''):
        print(line, end='')
    
    process.stdout.close()
    return_code = process.wait()
    
    return return_code == 0

def init_test_data():
    """初始化测试数据"""
    print("初始化测试数据...")
    
    try:
        # 尝试直接在当前进程中初始化数据
        sys.path.append(os.getcwd())
        from app.db.init_data import init_data
        init_data()
        print("✅ 测试数据初始化成功")
    except Exception as e:
        print(f"❌ 直接方式初始化失败: {e}")
        
        try:
            # 尝试子进程方式初始化
            result = subprocess.run(
                [sys.executable, "-c", "from app.db.init_data import init_data; init_data()"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ 测试数据初始化成功 (子进程方式)")
            else:
                print(f"❌ 子进程方式初始化失败: {result.stderr}")
        except Exception as e2:
            print(f"❌ 子进程方式也失败: {e2}")
            print("请手动初始化数据: python -c 'from app.db.init_data import init_data; init_data()'")

def main():
    parser = argparse.ArgumentParser(description="运行全流程测试环境")
    parser.add_argument("--no-server", action="store_true", help="不启动服务器，假设服务器已经运行")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--no-init", action="store_true", help="不初始化数据库")
    
    args = parser.parse_args()
    
    server_process = None
    log_files = []
    
    try:
        if not args.no_server:
            server_process, stdout_log, stderr_log = start_server(args.port)
            log_files = [stdout_log, stderr_log]
            
        # 初始化数据库
        if not args.no_init:
            init_test_data()
        
        print("\n准备开始测试...")
        time.sleep(2)  # 给服务器一点额外时间
        
        success = run_test()
        
        if success:
            print("\n✅ 全流程测试成功!")
        else:
            print("\n❌ 全流程测试失败!")
            print("查看logs/full_flow_test.log以获取详细信息")
            
    finally:
        # 关闭日志文件
        for f in log_files:
            if f:
                f.close()
                
        # 停止服务器
        if server_process:
            print("关闭服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("服务器已关闭")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print("服务器被强制关闭")

if __name__ == "__main__":
    main()
