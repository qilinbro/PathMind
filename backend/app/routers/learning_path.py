from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from ..services.learning_path_service import (
    get_learning_path_by_params,
    get_user_learning_paths,
    update_learning_progress
)
from ..services.video_service import search_videos
from ..models.learning_path import LearningPathResponse, VideoSearchResponse, VideoSearchRequest

router = APIRouter(
    prefix="/api/v1/learning",
    tags=["learning"],
    responses={404: {"description": "Not found"}}
)

# 添加兼容性端点，通过代理将/learning-paths/{path_id}转发到/learning/path
@router.get("/paths/{path_id}", response_model=LearningPathResponse)
async def get_learning_path_by_id_proxy(
    path_id: int,
    user_id: int = Query(..., description="用户ID")
):
    """获取指定ID的学习路径详情（兼容性端点）"""
    # 将请求映射到对应的主题和路径名称
    subject = "编程与开发"
    path_name = "Python从入门到精通"
    if path_id == 2:
        subject = "数据科学"
        path_name = "数据分析师成长路径"
    
    # 调用原有的学习路径获取函数
    path_data = await get_learning_path_by_params(
        user_id=user_id,
        subject_area=subject,
        path_name=path_name,
        target_level="中级"
    )
    
    if not path_data:
        raise HTTPException(status_code=404, detail=f"学习路径ID {path_id} 不存在")
        
    # 确保响应中的path_id字段匹配请求的ID
    path_data["path_id"] = str(path_id)
    return path_data

# 修正路径参数名称，确保与前端请求一致
@router.get("/path", response_model=LearningPathResponse)
async def get_learning_path(
    user_id: int,
    subject_area: str,
    path_name: str,
    target_level: str = "中级"
):
    """获取学习路径详情"""
    try:
        path_data = await get_learning_path_by_params(
            user_id=user_id, 
            subject_area=subject_area,
            path_name=path_name,
            target_level=target_level
        )
        
        if not path_data:
            raise HTTPException(status_code=404, detail="找不到指定的学习路径")
            
        return path_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习路径失败: {str(e)}")

# 添加用户注册学习路径的兼容性端点
@router.post("/paths/enroll", status_code=201)
async def enroll_learning_path_proxy(enrollment_data: dict):
    """用户注册学习路径（兼容性端点）"""
    # 在实际应用中，这里应该将用户注册添加到数据库
    return {
        "success": True,
        "message": f"用户 {enrollment_data.get('user_id')} 成功注册学习路径 {enrollment_data.get('path_id')}",
        "enrollment_id": 1,  # 模拟ID
        "path_id": enrollment_data.get('path_id'),
        "user_id": enrollment_data.get('user_id')
    }

@router.get("/user-paths", response_model=List[LearningPathResponse])
async def get_user_paths(user_id: int):
    """获取用户所有学习路径"""
    try:
        user_paths = await get_user_learning_paths(user_id)
        return user_paths
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户学习路径失败: {str(e)}")

@router.get("/search-videos", response_model=VideoSearchResponse)
async def search_learning_videos(
    query: str = Query(..., description="视频搜索关键词"),
    max_results: int = Query(5, description="最大返回结果数量"),
    type: str = Query("video", description="搜索类型")
):
    """搜索学习视频"""
    try:
        search_request = VideoSearchRequest(
            query=query,
            max_results=max_results,
            type=type
        )
        
        video_results = await search_videos(search_request)
        if not video_results or not video_results.videos:
            return VideoSearchResponse(videos=[])
            
        return video_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频搜索失败: {str(e)}")

@router.post("/update-progress")
async def update_node_progress(
    user_id: int,
    path_id: str,
    node_id: str,
    status: str
):
    """更新学习节点进度状态"""
    try:
        await update_learning_progress(user_id, path_id, node_id, status)
        return {"success": True, "message": "学习进度已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新学习进度失败: {str(e)}")
