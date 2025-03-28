#!/usr/bin/env python
"""
环境检查脚本 - 检查应用运行环境的完整性
"""
import os
import sys
import json
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    current_version = sys.version_info
    required_version = (3, 8)
    
    if current_version < required_version:
        return {
            "status": "error",
            "message": f"Python版本太低: {'.'.join(map(str, current_version[:3]))}，需要 {'.'.join(map(str, required_version))}"
        }
    return {
        "status": "ok",
        "message": f"Python版本: {'.'.join(map(str, current_version[:3]))}"
    }

def check_required_modules():
    """检查必需的模块"""
    required_modules = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
        "zhipuai", "httpx", "asyncio", "python-multipart"
    ]
    
    results = []
    for module in required_modules:
        try:
            m = importlib.import_module(module)
            version = getattr(m, "__version__", "未知")
            results.append({
                "module": module,
                "status": "ok",
                "version": version
            })
        except ImportError:
            results.append({
                "module": module,
                "status": "error",
                "message": f"模块 {module} 未安装"
            })
    
    return results

def check_env_variables():
    """检查环境变量"""
    required_vars = {
        "ZHIPU_API_KEY": "智谱AI API密钥"
    }
    
    optional_vars = {
        "DATABASE_URL": "数据库URL",
        "SECRET_KEY": "密钥",
        "USE_MOCK_DATA": "使用模拟数据"
    }
    
    results = {
        "required": {},
        "optional": {}
    }
    
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            results["required"][var] = {
                "status": "ok",
                "description": desc,
                "value": "已设置 (隐藏内容)"
            }
        else:
            results["required"][var] = {
                "status": "error",
                "description": desc,
                "message": "未设置"
            }
    
    for var, desc in optional_vars.items():
        value = os.environ.get(var)
        status = "ok" if value else "warning"
        results["optional"][var] = {
            "status": status,
            "description": desc,
            "value": "已设置" if value else "未设置"
        }
    
    return results

def check_config():
    """检查配置文件"""
    try:
        from app.core.config import settings
        
        return {
            "status": "ok",
            "config_items": {
                "PROJECT_NAME": settings.PROJECT_NAME,
                "API_V1_STR": settings.API_V1_STR,
                "USE_MOCK_DATA": settings.USE_MOCK_DATA,
                "ENVIRONMENT": settings.ENVIRONMENT,
                "ZHIPU_API_KEY_SET": bool(settings.ZHIPU_API_KEY)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"加载配置时出错: {str(e)}"
        }

def main():
    """主函数"""
    print("开始环境检查...")
    print("-" * 40)
    
    # 检查Python版本
    python_check = check_python_version()
    print(f"Python版本检查: {python_check['status']}")
    print(f"  {python_check['message']}")
    
    # 检查模块
    print("\n模块检查:")
    module_checks = check_required_modules()
    for check in module_checks:
        status_icon = "✅" if check["status"] == "ok" else "❌"
        if check["status"] == "ok":
            print(f"  {status_icon} {check['module']} - 版本: {check['version']}")
        else:
            print(f"  {status_icon} {check['module']} - {check.get('message', '未知错误')}")
    
    # 检查环境变量
    env_checks = check_env_variables()
    
    print("\n必需环境变量:")
    for var, check in env_checks["required"].items():
        status_icon = "✅" if check["status"] == "ok" else "❌"
        if check["status"] == "ok":
            print(f"  {status_icon} {var} - {check['description']}: {check['value']}")
        else:
            print(f"  {status_icon} {var} - {check['description']}: {check.get('message', '未知错误')}")
    
    print("\n可选环境变量:")
    for var, check in env_checks["optional"].items():
        status_icon = "✅" if check["status"] == "ok" else "⚠️"
        print(f"  {status_icon} {var} - {check['description']}: {check['value']}")
    
    # 检查配置
    config_check = check_config()
    print("\n配置检查:")
    if config_check["status"] == "ok":
        print(f"  ✅ 配置加载成功")
        for key, value in config_check["config_items"].items():
            print(f"    - {key}: {value}")
    else:
        print(f"  ❌ 配置检查失败: {config_check.get('message', '未知错误')}")
    
    # 输出总结
    print("\n" + "-" * 40)
    issues = sum(1 for check in module_checks if check["status"] != "ok")
    issues += sum(1 for check in env_checks["required"].values() if check["status"] != "ok")
    issues += 1 if python_check["status"] != "ok" else 0
    issues += 1 if config_check["status"] != "ok" else 0
    
    if issues == 0:
        print("✅ 环境检查通过，没有发现问题")
    else:
        print(f"⚠️ 环境检查完成，发现 {issues} 个问题需要解决")
    print("-" * 40)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"环境检查过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
