"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, BookOpen, CheckCircle, Clock, ExternalLink, Route } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { apiService } from "@/lib/api-service"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"

// 临时使用的用户ID，实际应用中应该从认证系统获取
const TEMP_USER_ID = 1

// 默认学习路径数据
const DEFAULT_PATH = {
  id: 0,
  title: "学习路径不可用",
  description: "无法加载请求的学习路径",
  estimated_time: "未知",
  total_steps: 0,
  completed_steps: 0,
  progress: 0,
  nodes: [],
  connections: [],
  tags: [],
}

export default function LearningPathDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [path, setPath] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEnrolled, setIsEnrolled] = useState(false)

  useEffect(() => {
    const fetchPathDetails = async () => {
      if (!params.id) return

      setIsLoading(true)
      try {
        const pathId = Number(params.id)
        console.log(`Fetching path details for ID: ${pathId}`)

        // 获取学习路径详情
        const data = await apiService.getLearningPath(pathId)
        console.log("Path data received:", data)

        if (data) {
          setPath(data)
          setIsEnrolled(!!data.enrolled)
        } else {
          console.warn(`Path with ID ${pathId} not found, using default path`)
          setPath(DEFAULT_PATH)
          setError("找不到请求的学习路径，显示默认内容")
        }
      } catch (err) {
        console.error("Error fetching path details:", err)
        setPath(DEFAULT_PATH)
        setError("加载学习路径时发生错误，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    fetchPathDetails()
  }, [params.id])

  // 处理加入学习路径
  const handleEnroll = async () => {
    if (!path?.id) return

    try {
      console.log(`Enrolling in path ID: ${path.id}`)
      await apiService.enrollLearningPath(TEMP_USER_ID, path.id)
      setIsEnrolled(true)
      // 重新获取路径数据以更新UI
      const updatedPath = await apiService.getLearningPath(path.id)
      if (updatedPath) {
        setPath(updatedPath)
      }
    } catch (error) {
      console.error("Failed to enroll in learning path:", error)
      setError("加入学习路径失败，请稍后再试")
    }
  }

  const handleNodeClick = (node: any) => {
    console.log("Node clicked:", node)
    // 这里可以根据节点类型导航到不同的页面
    if (node.type === "content" && node.content_id) {
      router.push(`/content/${node.content_id}`)
    } else if (node.type === "test" && node.test_id) {
      router.push(`/adaptive-tests/${node.test_id}`)
    }
  }

  const getNodeStatusColor = (status: string) => {
    switch (status) {
      case "已完成":
        return "bg-green-500"
      case "进行中":
        return "bg-blue-500"
      case "未开始":
      default:
        return "bg-gray-300 dark:bg-gray-600"
    }
  }

  return (
    <div className="container py-6">
      <div className="flex items-center gap-2 mb-6">
        <SidebarTrigger />
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="mr-2">
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">学习路径详情</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="space-y-6">
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-6 w-1/2" />
          <div className="flex items-center gap-2 mt-4">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-6 w-12" />
          </div>
          <Skeleton className="h-4 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      ) : (
        <>
          <Card className="mb-6">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl">{path?.title}</CardTitle>
                  <CardDescription className="mt-1">{path?.description}</CardDescription>
                </div>
                <Route className="h-6 w-6 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">预计时间: {path?.estimated_time}</span>
                  {isEnrolled && (
                    <>
                      <Separator orientation="vertical" className="mx-2 h-4" />
                      <span className="text-sm text-muted-foreground">
                        {path?.completed_steps || 0} / {path?.total_steps || 0} 步骤已完成
                      </span>
                    </>
                  )}
                </div>

                {isEnrolled && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>进度</span>
                      <span>{path?.progress || 0}%</span>
                    </div>
                    <Progress value={path?.progress || 0} />
                  </div>
                )}

                <div className="flex flex-wrap gap-2">
                  {path?.tags?.map((tag: string, index: number) => (
                    <Badge key={tag || index} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
            <CardFooter>
              {!isEnrolled ? (
                <Button className="w-full sm:w-auto" onClick={handleEnroll}>
                  加入学习路径
                </Button>
              ) : (
                <Button className="w-full sm:w-auto">
                  继续学习
                  <CheckCircle className="ml-2 h-4 w-4" />
                </Button>
              )}
            </CardFooter>
          </Card>

          <Tabs defaultValue="content" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="content">内容</TabsTrigger>
              <TabsTrigger value="structure">结构</TabsTrigger>
              {path?.resources && <TabsTrigger value="resources">资源</TabsTrigger>}
            </TabsList>

            <TabsContent value="content">
              <Card>
                <CardHeader>
                  <CardTitle>学习内容</CardTitle>
                  <CardDescription>按顺序完成以下学习节点</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {path?.nodes?.length > 0 ? (
                    path.nodes.map((node: any, index: number) => (
                      <div
                        key={node.id || index}
                        className="rounded-lg border p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                        onClick={() => handleNodeClick(node)}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${getNodeStatusColor(node.status)}`} />
                          <div className="flex-1">
                            <h3 className="font-medium">{node.title}</h3>
                            <p className="text-sm text-muted-foreground mt-1">{node.description}</p>
                          </div>
                          <Badge variant="outline">{node.type}</Badge>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">该学习路径暂无内容</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="structure">
              <Card>
                <CardHeader>
                  <CardTitle>路径结构</CardTitle>
                  <CardDescription>学习路径的可视化结构</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-96 flex items-center justify-center bg-muted/50 rounded-lg">
                    <p className="text-muted-foreground">路径结构图将在这里显示</p>
                    {/* 实际应用中，这里应该是一个使用d3.js或类似库的路径可视化组件 */}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {path?.resources && (
              <TabsContent value="resources">
                <Card>
                  <CardHeader>
                    <CardTitle>额外资源</CardTitle>
                    <CardDescription>帮助您学习的补充材料</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {path.resources.length > 0 ? (
                        path.resources.map((resource: any, index: number) => (
                          <div key={index} className="rounded-lg border p-3">
                            <div className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4 text-muted-foreground" />
                              <h3 className="font-medium">{resource.title}</h3>
                            </div>
                            <div className="mt-2 flex justify-between items-center">
                              <Badge variant="outline">{resource.type}</Badge>
                              <Button variant="ghost" size="sm" asChild>
                                <a
                                  href={resource.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1"
                                >
                                  查看
                                  <ExternalLink className="h-3 w-3 ml-1" />
                                </a>
                              </Button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">该学习路径暂无额外资源</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>
        </>
      )}
    </div>
  )
}
