import { NextResponse } from "next/server"
import { learningPaths } from "@/lib/mock-data"

export async function GET() {
  // Filter paths that are not enrolled
  const recommendedPaths = learningPaths.filter((path) => !path.enrolled)
  return NextResponse.json(recommendedPaths)
}

export async function POST() {
  // Filter paths that are not enrolled
  const recommendedPaths = learningPaths.filter((path) => !path.enrolled)
  return NextResponse.json(recommendedPaths)
}
