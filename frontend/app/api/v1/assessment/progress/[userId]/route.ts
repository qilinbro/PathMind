import { NextResponse } from "next/server";
import { users } from "@/data/users";

// 后端API基础URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000/api/v1";

export async function GET(request: Request, { params }: { params: { userId: string } }) {
  try {
    // 正确处理 params：先将其解析为 Promise
    const resolvedParams = await Promise.resolve(params);
    const userId = parseInt(resolvedParams.userId, 10);
    
    // 优先尝试从后端获取用户进度数据
    try {
      const backendResponse = await fetch(`${BACKEND_API_URL}/assessment/progress/${userId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (backendResponse.ok) {
        // 如果后端返回成功，直接返回数据
        const data = await backendResponse.json();
        console.log("成功从后端获取用户进度数据，使用后端数据");
        return NextResponse.json(data);
      } else {
        console.log(`后端返回错误: ${backendResponse.status}，尝试本地数据`);
      }
    } catch (error) {
      console.error("从后端获取数据失败，尝试其他源:", error);
    }

    // 从本地用户数据获取信息
    const user = users.find((u) => u.id === userId);
    
    if (!user) {
      return NextResponse.json({ error: "用户不存在" }, { status: 404 });
    }

    // 模拟的用户进度数据
    const progressData = {
      name: user.name,
      email: user.email,
      learning_style: user.learningStyle || "视觉",
      overall_progress: user.overallProgress || 35,
      completed_paths: user.completedPaths || 1,
      active_paths: user.activePaths || 2,
      completed_tests: user.completedTests || 3,
      current_learning_style: user.assessment || {
        visual: 65,
        auditory: 30,
        kinesthetic: 45,
        reading: 50
      },
      progress_metrics: {
        weekly_study_time: 12.5,
        completion_rate: 68,
        consistency: "良好",
        engagement: "中等"
      },
      improvement_suggestions: [
        "增加每周学习时间到15小时",
        "尝试更多的视觉学习资源",
        "定期复习已完成的内容"
      ],
      recent_activities: [
        {
          id: 1,
          type: "path",
          title: "完成了Python基础课程的第3章",
          date: "2025-04-25",
          progress: 40
        },
        {
          id: 2,
          type: "test",
          title: "通过了Python函数测验",
          date: "2025-04-23",
          score: 85
        },
        {
          id: 3,
          type: "path",
          title: "开始学习Web开发入门",
          date: "2025-04-20",
          progress: 10
        }
      ]
    };

    console.log("返回本地用户进度数据:", progressData);
    return NextResponse.json(progressData);
  } catch (error) {
    console.error("获取用户进度失败:", error);
    return NextResponse.json({ error: "获取用户进度失败" }, { status: 500 });
  }
}
