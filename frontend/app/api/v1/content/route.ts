import { NextResponse } from "next/server"
import { contentItems } from "@/lib/mock-data"

export async function GET() {
  return NextResponse.json(contentItems)
}
