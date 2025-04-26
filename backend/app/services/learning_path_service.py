from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from ..db.session import get_db
from ..models.learning_path import LearningPath, PathEnrollment
from ..models.content import LearningContent
from ..models.user import User

# 设置日志
logger = logging.getLogger(__name__)

# 保留原模拟数据作为备用
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

async def get_learning_path_by_params(
    user_id: int, 
    subject_area: str,
    path_name: str,
    target_level: str = "中级",
    db: Session = None
) -> Optional[Dict[str, Any]]:
    """根据参数获取学习路径"""
    logger.info(f"获取学习路径: 用户={user_id}, 主题={subject_area}, 路径={path_name}, 级别={target_level}")
    
    # 数据库会话管理
    close_db = False
    if db is None:
        try:
            db_generator = get_db()
            db = next(db_generator)
            close_db = True
        except Exception as e:
            logger.error(f"无法创建数据库会话: {str(e)}")
            # 如果无法创建数据库连接，回退到使用模拟数据
            return fallback_to_mock_data(user_id, subject_area, path_name, target_level)
    
    try:
        # 构建查询
        query = db.query(LearningPath)
        
        # 应用过滤条件
        if subject_area:
            query = query.filter(LearningPath.subject.ilike(f"%{subject_area}%"))
        if path_name:
            query = query.filter(LearningPath.title.ilike(f"%{path_name}%"))
            
        # 根据目标级别过滤
        level_map = {"初学者": 1, "中级": 2, "高级": 3, "专家": 4}
        target_level_num = level_map.get(target_level, 2)  # 默认中级
        
        # 查找符合级别的路径
        path = query.filter(LearningPath.difficulty_level <= target_level_num).first()
        
        if path:
            # 路径存在，转换为API响应格式
            return await format_path_for_api(path, user_id, db)
        else:
            # 路径不存在，回退到模拟数据
            logger.info(f"未找到匹配的学习路径，生成默认路径")
            return fallback_to_mock_data(user_id, subject_area, path_name, target_level)
            
    except Exception as e:
        logger.exception(f"获取学习路径失败: {str(e)}")
        return fallback_to_mock_data(user_id, subject_area, path_name, target_level)
        
    finally:
        if close_db and db:
            db.close()

async def get_user_learning_paths(user_id: int, db: Session = None) -> List[Dict[str, Any]]:
    """获取用户的所有学习路径"""
    # 数据库会话管理
    close_db = False
    if db is None:
        try:
            db_generator = get_db()
            db = next(db_generator)
            close_db = True
        except Exception as e:
            logger.error(f"无法创建数据库会话: {str(e)}")
            # 如果无法创建数据库连接，回退到使用模拟数据
            paths = []
            for path_key, path_data in MOCK_LEARNING_PATHS.items():
                path_copy = path_data.copy()
                paths.append(path_copy)
            return paths
    
    try:
        # 获取用户注册的学习路径
        enrollments = (
            db.query(PathEnrollment)
            .filter(PathEnrollment.user_id == user_id)
            .all()
        )
        
        if not enrollments:
            logger.info(f"用户 {user_id} 没有注册的学习路径")
            return []
            
        paths = []
        for enrollment in enrollments:
            # 获取学习路径详情
            path = db.query(LearningPath).filter(LearningPath.id == enrollment.path_id).first()
            if not path:
                continue
                
            # 获取路径内容数量
            content_count = len(path.contents) if path.contents else 0
                
            # 构建路径数据
            path_data = {
                "id": path.id,
                "title": path.title,
                "description": path.description,
                "subject": path.subject,
                "difficulty_level": path.difficulty_level,
                "estimated_hours": path.estimated_hours,
                "progress": enrollment.progress,
                "content_count": content_count,
                "last_activity": enrollment.last_activity_at,
                "enrolled_at": enrollment.enrolled_at
            }
            
            paths.append(path_data)
            
        return paths
        
    except Exception as e:
        logger.exception(f"获取用户学习路径失败: {str(e)}")
        return []
        
    finally:
        if close_db and db:
            db.close()

async def update_learning_progress(
    user_id: int, 
    path_id: str, 
    node_id: str,
    status: str,
    db: Session = None
) -> bool:
    """更新用户学习进度"""
    logger.info(f"更新学习进度: 用户={user_id}, 路径={path_id}, 节点={node_id}, 状态={status}")
    
    # 验证状态是否有效
    valid_statuses = ["未开始", "进行中", "已完成"]
    if status not in valid_statuses:
        raise ValueError(f"无效的状态值: {status}. 有效值为: {', '.join(valid_statuses)}")
    
    # 数据库会话管理
    close_db = False
    if db is None:
        try:
            db_generator = get_db()
            db = next(db_generator)
            close_db = True
        except Exception as e:
            logger.error(f"无法创建数据库会话: {str(e)}")
            # 如果无法创建数据库连接，回退到模拟数据进度更新
            if path_id in MOCK_LEARNING_PATHS:
                user_progress_key = f"{user_id}:{path_id}"
                if user_progress_key not in USER_PROGRESS:
                    USER_PROGRESS[user_progress_key] = {}
                USER_PROGRESS[user_progress_key][node_id] = status
                return True
            return False
    
    try:
        # 转换ID格式
        try:
            path_id_int = int(path_id)
            node_id_int = int(node_id)
        except (ValueError, TypeError):
            logger.error(f"无效的ID格式: path_id={path_id}, node_id={node_id}")
            return False
        
        # 查找用户路径注册记录
        enrollment = (
            db.query(PathEnrollment)
            .filter(
                PathEnrollment.user_id == user_id,
                PathEnrollment.path_id == path_id_int
            )
            .first()
        )
        
        # 如果未注册，创建注册记录
        if not enrollment:
            enrollment = PathEnrollment(
                user_id=user_id,
                path_id=path_id_int,
                progress=0,
                content_progress={},
                enrolled_at=datetime.now()
            )
            db.add(enrollment)
        
        # 更新内容进度
        content_progress = enrollment.content_progress or {}
        
        # 根据状态设置进度值
        progress_value = 0
        if status == "进行中":
            progress_value = 50
        elif status == "已完成":
            progress_value = 100
            
        content_progress[str(node_id_int)] = progress_value
        enrollment.content_progress = content_progress
        
        # 更新整体进度
        if content_progress:
            total_progress = sum(progress_value for progress_value in content_progress.values())
            enrollment.progress = min(100, total_progress / len(content_progress))
        
        # 更新最后活动时间
        enrollment.last_activity_at = datetime.now()
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.exception(f"更新学习进度失败: {str(e)}")
        return False
        
    finally:
        if close_db and db:
            db.close()

async def format_path_for_api(path, user_id, db):
    """将数据库路径对象格式化为API响应格式"""
    try:
        # 基本路径数据
        path_data = {
            "path_id": str(path.id),
            "title": path.title,
            "description": path.description,
            "estimated_duration": f"{path.estimated_hours or 10}-{(path.estimated_hours or 10) * 2}小时",
            "nodes": [],
            "connections": []
        }
        
        # 获取路径内容
        path_contents = path.contents
        
        # 获取用户进度
        user_progress = {}
        if user_id:
            enrollment = (
                db.query(PathEnrollment)
                .filter(
                    PathEnrollment.user_id == user_id,
                    PathEnrollment.path_id == path.id
                )
                .first()
            )
            if enrollment and enrollment.content_progress:
                user_progress = enrollment.content_progress
        
        # 创建节点
        nodes = []
        for i, content in enumerate(path_contents):
            # 确定节点状态
            status = "未开始"
            content_id_str = str(content.id)
            if content_id_str in user_progress:
                progress = user_progress[content_id_str]
                if progress >= 100:
                    status = "已完成"
                elif progress > 0:
                    status = "进行中"
            
            # 映射难度级别
            level_map = {1: "初级", 2: "中级", 3: "高级", 4: "专家"}
            level = level_map.get(content.difficulty_level, "中级")
            
            # 创建节点
            node = {
                "id": content_id_str,
                "title": content.title,
                "description": content.description or "",
                "type": content.content_type or "topic",
                "level": level,
                "status": status
            }
            
            # 添加资源
            if hasattr(content, 'resources') and content.resources:
                resources = []
                for resource in content.resources:
                    resources.append({
                        "title": resource.get('title', "学习资源"),
                        "url": resource.get('url', "#"),
                        "type": resource.get('type', "链接")
                    })
                node["resources"] = resources
            
            nodes.append(node)
            
        path_data["nodes"] = nodes
        
        # 创建连接
        connections = []
        for i in range(len(nodes) - 1):
            connections.append({
                "source": nodes[i]["id"],
                "target": nodes[i+1]["id"]
            })
        
        path_data["connections"] = connections
        
        return path_data
    
    except Exception as e:
        logger.exception(f"格式化学习路径失败: {str(e)}")
        return generate_default_path(path.subject, path.title, "中级")

def fallback_to_mock_data(user_id, subject_area, path_name, target_level):
    """当数据库操作失败时回退到使用模拟数据"""
    logger.warning("回退到使用模拟数据")
    
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
                    
        return path_data
        
    # 如果没有找到匹配的路径，返回一个通用的默认路径
    return generate_default_path(subject_area, path_name, target_level)

def generate_default_path(subject: str, path_name: str, level: str) -> Dict[str, Any]:
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

# 用户学习进度数据 (作为模拟数据的备份)
USER_PROGRESS = {}
