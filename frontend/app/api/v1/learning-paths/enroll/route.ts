import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const body = await request.json()

  // In a real app, you would update the database here
  // For now, just return a success response
  return NextResponse.json({
    success: true,
    message: `User ${body.user_id} enrolled in path ${body.path_id}`,
  })
}
