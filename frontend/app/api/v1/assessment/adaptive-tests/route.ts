import { NextResponse } from "next/server";
import { adaptiveTests } from "@/data/users";

// 后端API基础URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000/api/v1";

export async function GET(request: Request) {
  try {
    // 尝试从后端获取数据
    try {
      const backendResponse = await fetch(`${BACKEND_API_URL}/assessment/adaptive-tests`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (backendResponse.ok) {
        const data = await backendResponse.json();
        console.log("成功从后端获取自适应测试列表");
        return NextResponse.json(data);
      } else {
        console.log(`后端返回错误: ${backendResponse.status}，使用本地数据`);
      }
    } catch (error) {
      console.error("从后端获取数据失败，使用本地数据:", error);
    }

    // 返回本地模拟数据
    console.log("返回本地自适应测试列表");
    return NextResponse.json(adaptiveTests);
  } catch (error) {
    console.error("获取自适应测试列表失败:", error);
    return NextResponse.json({ error: "获取自适应测试列表失败" }, { status: 500 });
  }
}
