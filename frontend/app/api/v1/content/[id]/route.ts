import { NextResponse } from "next/server"
import { contentItems } from "@/lib/mock-data"

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const contentId = Number.parseInt(params.id)
  const content = contentItems.find((c) => c.id === contentId)

  if (!content) {
    return NextResponse.json({ error: "Content not found" }, { status: 404 })
  }

  return NextResponse.json(content)
}
