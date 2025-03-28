#!/usr/bin/env python
"""
生成HTML测试报告
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# 报告目录
REPORT_DIR = ROOT_DIR / "tests" / "reports"
HTML_REPORT_DIR = ROOT_DIR / "tests" / "html_reports"
HTML_REPORT_DIR.mkdir(exist_ok=True, parents=True)

def generate_html_report():
    """生成HTML格式的测试报告"""
    # 查找最新的JSON报告
    json_reports = list(REPORT_DIR.glob("ai_test_report_*.json"))
    if not json_reports:
        print("未找到测试报告")
        return False
    
    latest_report = max(json_reports, key=lambda p: p.stat().st_mtime)
    
    # 读取JSON报告
    with open(latest_report, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    
    # 生成HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>智谱AI测试报告 - {report_data['test_date']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
            .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .summary-item {{ padding: 10px; background-color: #f5f5f5; border-radius: 5px; flex: 1; margin: 0 10px; text-align: center; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>智谱AI集成测试报告</h1>
                <p>测试时间: {report_data['test_date']}</p>
            </div>
            
            <div class="summary">
                <div class="summary-item">
                    <h3>总测试</h3>
                    <p>{report_data['total_tests']}</p>
                </div>
                <div class="summary-item">
                    <h3>成功</h3>
                    <p class="success">{report_data['successful_tests']}</p>
                </div>
                <div class="summary-item">
                    <h3>失败</h3>
                    <p class="failure">{report_data['failed_tests']}</p>
                </div>
                <div class="summary-item">
                    <h3>总耗时</h3>
                    <p>{report_data['total_duration']}</p>
                </div>
            </div>
            
            <h2>测试结果详情</h2>
            <table>
                <tr>
                    <th>测试名称</th>
                    <th>状态</th>
                    <th>耗时</th>
                </tr>
    """
    
    # 添加每个测试的结果行
    for result in report_data['results']:
        status_class = "success" if result["status"] == "成功" else "failure"
        html_content += f"""
                <tr>
                    <td>{result['name']}</td>
                    <td class="{status_class}">{result['status']}</td>
                    <td>{result['duration']}</td>
                </tr>
        """
    
    # 结束HTML
    html_content += """
            </table>
        </div>
    </body>
    </html>
    """
    
    # 保存HTML报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_path = HTML_REPORT_DIR / f"ai_test_report_{timestamp}.html"
    with open(html_report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML报告已生成: {html_report_path}")
    return True

if __name__ == "__main__":
    generate_html_report()
