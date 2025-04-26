import { NextResponse } from "next/server"
import { learningPaths } from "@/lib/mock-data"

export async function GET() {
  return NextResponse.json(learningPaths)
}

export async function POST() {
  return NextResponse.json(learningPaths)
}
