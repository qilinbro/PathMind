import { NextResponse } from "next/server";

// 后端API基础URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000/api/v1";

export async function GET(request: Request, { params }: { params: { userId: string } }) {
  try {
    // 解决动态路由参数问题
    const resolvedParams = await Promise.resolve(params);
    const userId = parseInt(resolvedParams.userId, 10);
    
    // 尝试从后端获取数据
    try {
      const backendResponse = await fetch(`${BACKEND_API_URL}/assessment/user/${userId}/tests`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (backendResponse.ok) {
        const data = await backendResponse.json();
        console.log(`成功从后端获取用户${userId}的已完成测试`);
        return NextResponse.json(data);
      } else {
        console.log(`后端返回错误: ${backendResponse.status}，返回空数组`);
      }
    } catch (error) {
      console.error("从后端获取数据失败:", error);
    }

    // 用户可能没有完成任何测试，返回空数组
    console.log(`用户${userId}没有已完成的测试`);
    return NextResponse.json([]);
  } catch (error) {
    console.error("获取用户已完成测试失败:", error);
    return NextResponse.json({ error: "获取用户已完成测试失败" }, { status: 500 });
  }
}
