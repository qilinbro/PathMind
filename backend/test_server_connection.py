#!/usr/bin/env python
"""
简单的服务器连接测试脚本
用于验证服务器是否正常运行并可以响应请求
"""
import sys
import json
import requests
import time

# 服务器地址
SERVER_URL = "http://localhost:8000"

def test_server_connection():
    """测试服务器连接"""
    print(f"尝试连接到服务器: {SERVER_URL}")
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接成功!")
            print(f"响应: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ 服务器返回错误状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 - 连接被拒绝")
        print("请确保服务器已启动: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时 - 服务器没有及时响应")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False

def test_api_endpoints():
    """测试API端点"""
    endpoints = [
        "/",
        "/health",
        "/api/v1/assessment/questions/",
        "/api/v1/content/"
    ]
    
    print("\n测试API端点:")
    for endpoint in endpoints:
        url = f"{SERVER_URL}{endpoint}"
        print(f"\n尝试访问: {url}")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 400:
                print(f"✅ 成功 - 状态码: {response.status_code}")
                try:
                    data = response.json()
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"响应: {response.text[:200]}...")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("服务器连接测试")
    print("=" * 50)
    
    if test_server_connection():
        test_api_endpoints()
    else:
        print("\n服务器连接失败，无法测试API端点")
        sys.exit(1)
