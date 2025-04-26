import { NextResponse } from "next/server"
import { learningPaths } from "@/lib/mock-data"

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const pathId = Number.parseInt(params.id)
  const path = learningPaths.find((p) => p.id === pathId)

  if (!path) {
    return NextResponse.json({ error: "Learning path not found" }, { status: 404 })
  }

  return NextResponse.json(path)
}
