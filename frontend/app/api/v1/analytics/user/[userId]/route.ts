import { NextResponse } from "next/server"
import { analyticsData } from "@/lib/mock-data"

export async function GET(request: Request, { params }: { params: { userId: string } }) {
  // In a real app, you would fetch analytics for the specific user
  // For now, return the mock analytics data
  return NextResponse.json(analyticsData)
}
