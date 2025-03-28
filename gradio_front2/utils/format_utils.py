"""
格式化工具函数
"""

def format_api_status_html(status_info):
    """格式化API状态信息为HTML"""
    status_text = f"<div class='backend-status'>"
    if status_info["status"] == "正常":
        status_text += "<span class='status-indicator status-normal'></span>"
    elif status_info["status"] == "部分可用" or status_info["status"] == "功能受限":
        status_text += "<span class='status-indicator status-partial'></span>"
    else:
        status_text += "<span class='status-indicator status-error'></span>"
    
    status_text += f"<span>{status_info['status']}</span></div>"
    status_text += f"<div>{status_info['message']}</div>"
    
    if "api_info" in status_info:
        status_text += f"<div><small>{status_info['api_info']}</small></div>"
        
    if "details" in status_info:
        status_text += "<details><summary>查看详细信息</summary><div class='detail-view'>"
        for name, info in status_info["details"].items():
            status_emoji = "✅" if info["ok"] else "❌"
            status_text += f"<div>{status_emoji} {name}: {info['status']}</div>"
        status_text += "</div></details>"
    
    return status_text
