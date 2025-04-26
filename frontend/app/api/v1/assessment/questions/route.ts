import { NextResponse } from "next/server"
import { assessmentQuestions } from "@/lib/mock-data"

export async function GET() {
  return NextResponse.json(assessmentQuestions)
}
