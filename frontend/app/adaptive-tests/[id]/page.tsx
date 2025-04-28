"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Brain, CheckCircle, Clock, TestTube } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { apiService } from "@/lib/api-service"

export default function TestDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [test, setTest] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTestDetails = async () => {
      setIsLoading(true)
      setError(null)
      try {
        // 从后端API获取测试详情
        const testId = typeof params.id === 'string' ? parseInt(params.id, 10) : Number(params.id)
        const data = await apiService.getTestDetails(testId)
        
        if (!data) {
          setError("未找到测试详情")
          return
        }
        
        setTest(data)
      } catch (error) {
        console.error("Failed to fetch test details:", error)
        setError("获取测试详情失败，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    if (params.id) {
      fetchTestDetails()
    }
  }, [params.id])

  const handleStartTest = () => {
    router.push(`/adaptive-tests/${params.id}/take`)
  }

  return (
    <div className="container py-6">
      <div className="flex items-center gap-2 mb-6">
        <SidebarTrigger />
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="mr-2">
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">测试详情</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-3/4 mb-2" />
            <Skeleton className="h-4 w-full" />
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
              </div>
              <Skeleton className="h-4 w-1/4 mb-2" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Skeleton className="h-10 w-full max-w-xs mx-auto" />
          </CardFooter>
        </Card>
      ) : test ? (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl">{test.title}</CardTitle>
                <CardDescription className="mt-2">{test.description}</CardDescription>
              </div>
              <TestTube className="h-6 w-6 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="rounded-lg border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                    <h3 className="font-medium">预计时间</h3>
                  </div>
                  <p>{test.estimatedTime || "30分钟"}</p>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-5 w-5 text-muted-foreground" />
                    <h3 className="font-medium">难度</h3>
                  </div>
                  <p>{test.difficulty || "中级"}</p>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-muted-foreground" />
                    <h3 className="font-medium">问题数量</h3>
                  </div>
                  <p>{test.questions || test.questionCount || 0}个问题</p>
                </div>
              </div>

              {test.tags && test.tags.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-2">标签</h3>
                  <div className="flex flex-wrap gap-2">
                    {test.tags.map((tag: string) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {test.instructions && test.instructions.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-2">测试说明</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {test.instructions.map((instruction: string, index: number) => (
                      <li key={index} className="text-muted-foreground">
                        {instruction}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full max-w-xs mx-auto" onClick={handleStartTest}>
              开始测试
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">未找到测试信息</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push("/adaptive-tests")}>
            返回测试列表
          </Button>
        </div>
      )}
    </div>
  )
}
