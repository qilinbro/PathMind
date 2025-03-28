import logging
import json
import os
import httpx
from typing import Dict, List, Optional
import asyncio
from ..models.learning_path import VideoSearchRequest, VideoSearchResponse, Video

# 设置日志
logger = logging.getLogger(__name__)

# YouTube API 密钥 (实际应用需要从环境变量或配置文件获取)
# YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_API_KEY = None  # 现在不设置，使用模拟数据

# 模拟视频数据
MOCK_VIDEOS = {
    "python": [
        {
            "video_id": "rfscVS0vtbw",
            "title": "Python教程 - 初学者全套课程",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://i.ytimg.com/vi/rfscVS0vtbw/mqdefault.jpg"
        },
        {
            "video_id": "_uQrJ0TkZlc",
            "title": "Python Tutorial - Python for Beginners [2023]",
            "channel": "Programming with Mosh",
            "thumbnail": "https://i.ytimg.com/vi/_uQrJ0TkZlc/mqdefault.jpg"
        },
        {
            "video_id": "kqtD5dpn9C8",
            "title": "Python速成课程 - 30分钟学会Python基础",
            "channel": "Python入门",
            "thumbnail": "https://i.ytimg.com/vi/kqtD5dpn9C8/mqdefault.jpg"
        }
    ],
    "data": [
        {
            "video_id": "r-uOLxNrNk8",
            "title": "数据分析全套教程 - 从零开始学数据分析",
            "channel": "数据分析师训练营",
            "thumbnail": "https://i.ytimg.com/vi/r-uOLxNrNk8/mqdefault.jpg"
        },
        {
            "video_id": "GPVsHOlRBBI",
            "title": "Python数据分析库Pandas入门教程",
            "channel": "Python数据科学",
            "thumbnail": "https://i.ytimg.com/vi/GPVsHOlRBBI/mqdefault.jpg"
        }
    ],
    "default": [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "视频教程",
            "channel": "学习频道",
            "thumbnail": "https://via.placeholder.com/120x67"
        },
        {
            "video_id": "C0DPdy98e4c",
            "title": "从入门到精通",
            "channel": "教育课堂",
            "thumbnail": "https://via.placeholder.com/120x67"
        }
    ]
}

async def search_videos(search_request: VideoSearchRequest) -> VideoSearchResponse:
    """搜索学习视频"""
    query = search_request.query.lower()
    max_results = search_request.max_results
    
    logger.info(f"搜索视频: 查询={query}, 最大结果={max_results}")
    
    # 如果有YouTube API密钥，使用真实API
    if YOUTUBE_API_KEY:
        try:
            return await search_youtube_videos(search_request)
        except Exception as e:
            logger.error(f"YouTube API调用失败: {str(e)}，使用模拟数据")
    
    # 否则使用模拟数据
    logger.info("使用模拟视频数据")
    videos = []
    
    # 从模拟数据中选择匹配的视频
    if "python" in query:
        videos = MOCK_VIDEOS["python"]
    elif "数据" in query or "data" in query:
        videos = MOCK_VIDEOS["data"]
    else:
        # 通用视频，但添加查询词到标题中
        videos = []
        for video in MOCK_VIDEOS["default"]:
            video_copy = video.copy()
            video_copy["title"] = f"{query} - {video['title']}"
            videos.append(video_copy)
    
    # 限制结果数量
    videos = videos[:max_results]
    
    return VideoSearchResponse(videos=videos)

async def search_youtube_videos(search_request: VideoSearchRequest) -> VideoSearchResponse:
    """使用YouTube API搜索视频"""
    if not YOUTUBE_API_KEY:
        raise ValueError("未设置YouTube API密钥")
    
    query = search_request.query
    max_results = min(search_request.max_results, 10)  # YouTube限制
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": max_results,
        "q": query,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append(Video(
            video_id=video_id,
            title=snippet["title"],
            channel=snippet["channelTitle"],
            thumbnail=snippet["thumbnails"]["medium"]["url"]
        ))
    
    return VideoSearchResponse(videos=videos)
