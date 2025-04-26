import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const body = await request.json()

  // In a real app, you would process the assessment responses here
  // For now, return a mock result
  return NextResponse.json({
    dominant_style: "visual",
    secondary_style: "kinesthetic",
    recommended_content: [
      "使用视觉辅助工具如图表、思维导图和在笔记中使用颜色编码",
      "观看学习新概念时的视频演示",
      "融入动手实践和实验",
      "尝试向他人教授概念以加强理解",
      "在学习过程中定期休息以保持专注",
    ],
  })
}
