import { NextResponse } from "next/server"
import { users } from "@/lib/mock-data"

export async function GET(request: Request, { params }: { params: { userId: string } }) {
  const userId = Number.parseInt(params.userId)
  const user = users.find((u) => u.id === userId)

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404 })
  }

  return NextResponse.json(user)
}
