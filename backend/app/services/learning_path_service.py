from typing import List, Dict, Any, Optional
import logging
import json
from pathlib import Path
from ..models.learning_path import LearningPathResponse, LearningPathNode, PathConnection, Resource

# 设置日志
logger = logging.getLogger(__name__)

# 模拟数据库
# 实际应用中，这些数据应该存储在数据库中
# 这里使用内存中的模拟数据以便测试

# 预设学习路径数据
MOCK_LEARNING_PATHS = {
    "python-beginner-to-advanced": {
        "path_id": "python-beginner-to-advanced",
        "title": "Python从入门到精通",
        "description": "全面学习Python编程，从基础语法到高级应用",
        "estimated_duration": "3-6个月",
        "nodes": [
            {
                "id": "python-basics",
                "title": "Python基础语法",
                "description": "学习Python的基本语法、数据类型、变量、条件语句和循环。掌握Python编程的基础知识，为后续更深入的学习打下基础。",
                "type": "topic",
                "level": "初级",
                "status": "未开始",
                "resources": [
                    {
                        "title": "Python官方教程",
                        "url": "https://docs.python.org/zh-cn/3/tutorial/",
                        "type": "文档"
                    },
                    {
                        "title": "Python编程：从入门到实践",
                        "url": "https://book-link-placeholder.com/python-crash-course",
                        "type": "书籍"
                    }
                ]
            },
            {
                "id": "python-data-structures",
                "title": "Python数据结构",
                "description": "学习Python的列表、元组、字典和集合等数据结构，以及它们的使用方法和适用场景。",
                "type": "topic",
                "level": "初级",
                "status": "未开始",
                "resources": [
                    {
                        "title": "Python数据结构与算法",
                        "url": "https://realpython.com/python-data-structures/",
                        "type": "教程"
                    }
                ]
            },
            {
                "id": "python-functions",
                "title": "Python函数与模块",
                "description": "学习如何定义和使用函数，创建和导入模块，理解函数参数和返回值。",
                "type": "topic",
                "level": "初级",
                "status": "未开始"
            }
        ],
        "connections": [
            {"source": "python-basics", "target": "python-data-structures"},
            {"source": "python-data-structures", "target": "python-functions"}
        ]
    },
    "data-analysis-path": {
        "path_id": "data-analysis-path",
        "title": "数据分析师成长路径",
        "description": "从零开始成为一名专业数据分析师",
        "estimated_duration": "4-8个月",
        "nodes": [
            {
                "id": "data-basics",
                "title": "数据分析基础",
                "description": "了解数据分析的基本概念、数据类型和分析流程。学习如何提出正确的问题，并通过数据寻找答案。",
                "type": "topic",
                "level": "初级",
                "status": "未开始"
            },
            {
                "id": "excel-analytics",
                "title": "Excel数据分析",
                "description": "学习使用Excel进行数据整理、分析和可视化，掌握常用函数、数据透视表和图表制作。",
                "type": "topic",
                "level": "初级",
                "status": "未开始"
            }
        ],
        "connections": [
            {"source": "data-basics", "target": "excel-analytics"}
        ]
    }
}

# 用户学习进度数据
USER_PROGRESS = {}

# 移除LearningPathService类，使用函数式API保持一致性

async def get_learning_path_by_params(
    user_id: int, 
    subject_area: str,
    path_name: str,
    target_level: str = "中级"
) -> Optional[LearningPathResponse]:
    """根据参数获取学习路径"""
    logger.info(f"获取学习路径: 用户={user_id}, 主题={subject_area}, 路径={path_name}, 级别={target_level}")
    
    # 在实际应用中，这里应该查询数据库
    # 现在我们使用模拟数据
    
    # 根据路径名称查找对应的学习路径
    path_key = None
    if "Python" in path_name:
        path_key = "python-beginner-to-advanced"
    elif "数据分析" in path_name or "data" in path_name.lower():
        path_key = "data-analysis-path"
        
    if path_key and path_key in MOCK_LEARNING_PATHS:
        # 获取基础路径数据
        path_data = MOCK_LEARNING_PATHS[path_key].copy()
        
        # 应用用户进度数据（如果有）
        user_progress_key = f"{user_id}:{path_key}"
        if user_progress_key in USER_PROGRESS:
            progress_data = USER_PROGRESS[user_progress_key]
            # 更新节点状态
            for i, node in enumerate(path_data["nodes"]):
                node_id = node["id"]
                if node_id in progress_data:
                    path_data["nodes"][i]["status"] = progress_data[node_id]
        
        # 根据目标级别筛选节点
        if target_level != "专家":
            filtered_nodes = []
            level_mapping = {
                "初学者": ["初级"],
                "中级": ["初级", "中级"],
                "高级": ["初级", "中级", "高级"],
                "专家": ["初级", "中级", "高级", "专家"]
            }
            allowed_levels = level_mapping.get(target_level, ["初级", "中级", "高级", "专家"])
            
            for node in path_data["nodes"]:
                if node.get("level") in allowed_levels:
                    filtered_nodes.append(node)
                    
            path_data["nodes"] = filtered_nodes
            
            # 更新连接以匹配筛选后的节点
            filtered_node_ids = [node["id"] for node in filtered_nodes]
            filtered_connections = []
            
            for conn in path_data["connections"]:
                if conn["source"] in filtered_node_ids and conn["target"] in filtered_node_ids:
                    filtered_connections.append(conn)
                    
            path_data["connections"] = filtered_connections
        
        return path_data
        
    # 如果没有找到匹配的路径，返回一个通用的默认路径
    return generate_default_path(subject_area, path_name, target_level)

async def get_user_learning_paths(user_id: int) -> List[LearningPathResponse]:
    """获取用户的所有学习路径"""
    # 在实际应用中，这里应该查询数据库中用户注册的路径
    # 现在我们简单返回所有可用路径
    
    user_paths = []
    for path_key, path_data in MOCK_LEARNING_PATHS.items():
        # 复制一份以避免修改原始数据
        path_copy = path_data.copy()
        
        # 应用用户进度数据（如果有）
        user_progress_key = f"{user_id}:{path_key}"
        if user_progress_key in USER_PROGRESS:
            progress_data = USER_PROGRESS[user_progress_key]
            # 更新节点状态
            for i, node in enumerate(path_copy["nodes"]):
                node_id = node["id"]
                if node_id in progress_data:
                    path_copy["nodes"][i]["status"] = progress_data[node_id]
        
        user_paths.append(path_copy)
    
    return user_paths

async def update_learning_progress(
    user_id: int, 
    path_id: str, 
    node_id: str,
    status: str
) -> bool:
    """更新用户学习进度"""
    logger.info(f"更新学习进度: 用户={user_id}, 路径={path_id}, 节点={node_id}, 状态={status}")
    
    # 验证状态是否有效
    valid_statuses = ["未开始", "进行中", "已完成"]
    if status not in valid_statuses:
        raise ValueError(f"无效的状态值: {status}. 有效值为: {', '.join(valid_statuses)}")
    
    # 更新用户进度数据
    user_progress_key = f"{user_id}:{path_id}"
    if user_progress_key not in USER_PROGRESS:
        USER_PROGRESS[user_progress_key] = {}
    
    USER_PROGRESS[user_progress_key][node_id] = status
    logger.info(f"用户{user_id}的学习进度已更新")
    
    return True

def generate_default_path(subject: str, path_name: str, level: str) -> LearningPathResponse:
    """生成默认学习路径"""
    path_id = f"{subject.lower()}-{path_name.lower().replace(' ', '-')}"
    return {
        "path_id": path_id,
        "title": path_name,
        "description": f"{subject}领域的学习路径",
        "estimated_duration": "3-6个月",
        "nodes": [
            {
                "id": "basics",
                "title": "基础知识",
                "description": f"{path_name}的基础知识与核心概念。",
                "type": "topic",
                "level": "初级",
                "status": "未开始"
            },
            {
                "id": "intermediate",
                "title": "进阶内容",
                "description": f"{path_name}的进阶知识与技能。",
                "type": "topic",
                "level": "中级",
                "status": "未开始"
            },
            {
                "id": "project",
                "title": "实践项目",
                "description": "通过动手项目巩固所学知识。",
                "type": "project",
                "level": "中级",
                "status": "未开始"
            },
            {
                "id": "advanced",
                "title": "高级内容",
                "description": "深入学习高级技术与概念。",
                "type": "topic",
                "level": "高级",
                "status": "未开始"
            }
        ],
        "connections": [
            {"source": "basics", "target": "intermediate"},
            {"source": "intermediate", "target": "project"},
            {"source": "project", "target": "advanced"}
        ]
    }
