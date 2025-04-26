"use client"

import { useEffect, useState } from "react"
import { CheckCircle, ChevronRight, Clock, Route, Search } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"

// 临时使用的用户ID，实际应用中应该从认证系统获取
const TEMP_USER_ID = 1

interface LearningPath {
  id: number
  title: string
  description: string
  progress?: number
  totalSteps?: number
  completedSteps?: number
  estimatedTime: string
  tags: string[]
}

export default function LearningPathsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [enrolledPaths, setEnrolledPaths] = useState<LearningPath[]>([])
  const [recommendedPaths, setRecommendedPaths] = useState<LearningPath[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      // 获取所有学习路径
      const paths = await apiService.getLearningPaths()

      // 获取推荐的学习路径
      const recommendedPathsData = await apiService.getRecommendedPaths()

      // 假设API返回的数据需要转换为前端需要的格式
      // 实际情况下，这里的转换逻辑应该根据API的实际返回格式调整
      const enrolled = paths
        .filter((path) => path.enrolled)
        .map((path) => ({
          id: path.id,
          title: path.title,
          description: path.description,
          progress: path.progress || 0,
          totalSteps: path.total_steps || 0,
          completedSteps: path.completed_steps || 0,
          estimatedTime: path.estimated_time || "未知",
          tags: path.tags || [],
        }))

      const recommended = recommendedPathsData.map((path) => ({
        id: path.id,
        title: path.title,
        description: path.description,
        estimatedTime: path.estimated_time || "未知",
        tags: path.tags || [],
      }))

      setEnrolledPaths(enrolled)
      setRecommendedPaths(recommended)
    } catch (error) {
      console.error("Failed to fetch learning paths:", error)
      // 在实际应用中，应该显示错误消息给用户
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const filteredEnrolled = enrolledPaths.filter(
    (path) =>
      path.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      path.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      path.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const filteredRecommended = recommendedPaths.filter(
    (path) =>
      path.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      path.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      path.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleEnroll = async (pathId: number) => {
    try {
      await apiService.enrollLearningPath(TEMP_USER_ID, pathId)
      // 重新获取数据以更新UI
      fetchData()
    } catch (error) {
      console.error("Failed to enroll in learning path:", error)
    }
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">学习路径</h1>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索路径..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <Tabs defaultValue="enrolled" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="enrolled">已加入</TabsTrigger>
          <TabsTrigger value="recommended">推荐</TabsTrigger>
        </TabsList>

        <TabsContent value="enrolled">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {isLoading ? (
              // 加载状态的骨架屏
              Array(3)
                .fill(0)
                .map((_, index) => (
                  <Card key={index} className="flex flex-col">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <Skeleton className="h-6 w-3/4" />
                        <Skeleton className="h-5 w-5 rounded-full" />
                      </div>
                      <Skeleton className="h-4 w-full mt-2" />
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <Skeleton className="h-4 w-16" />
                            <Skeleton className="h-4 w-8" />
                          </div>
                          <Skeleton className="h-2 w-full" />
                        </div>
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                        <div className="flex flex-wrap gap-2 mt-2">
                          <Skeleton className="h-6 w-16 rounded-full" />
                          <Skeleton className="h-6 w-24 rounded-full" />
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Skeleton className="h-10 w-full" />
                    </CardFooter>
                  </Card>
                ))
            ) : filteredEnrolled.length > 0 ? (
              filteredEnrolled.map((path) => (
                <Card key={path.id} className="flex flex-col">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle>{path.title}</CardTitle>
                      <Route className="h-5 w-5 text-primary" />
                    </div>
                    <CardDescription>{path.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1">
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>进度</span>
                          <span>{path.progress}%</span>
                        </div>
                        <Progress value={path.progress} />
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <CheckCircle className="h-4 w-4" />
                        <span>
                          {path.completedSteps} / {path.totalSteps} 步骤已完成
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>预计时间: {path.estimatedTime}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {path.tags.map((tag) => (
                          <Badge key={tag} variant="secondary">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button className="w-full" asChild>
                      <a href={`/learning-paths/${path.id}`}>
                        继续学习
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </a>
                    </Button>
                  </CardFooter>
                </Card>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-muted-foreground">您尚未加入任何学习路径</p>
                <Button className="mt-4" onClick={() => document.querySelector('[data-value="recommended"]')?.click()}>
                  浏览推荐路径
                </Button>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="recommended">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {isLoading ? (
              // 加载状态的骨架屏
              Array(3)
                .fill(0)
                .map((_, index) => (
                  <Card key={index} className="flex flex-col">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <Skeleton className="h-6 w-3/4" />
                        <Skeleton className="h-5 w-5 rounded-full" />
                      </div>
                      <Skeleton className="h-4 w-full mt-2" />
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="space-y-4">
                        <Skeleton className="h-4 w-1/2" />
                        <div className="flex flex-wrap gap-2 mt-2">
                          <Skeleton className="h-6 w-16 rounded-full" />
                          <Skeleton className="h-6 w-24 rounded-full" />
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Skeleton className="h-10 w-full" />
                    </CardFooter>
                  </Card>
                ))
            ) : filteredRecommended.length > 0 ? (
              filteredRecommended.map((path) => (
                <Card key={path.id} className="flex flex-col">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle>{path.title}</CardTitle>
                      <Route className="h-5 w-5 text-primary" />
                    </div>
                    <CardDescription>{path.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1">
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>预计时间: {path.estimatedTime}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {path.tags.map((tag) => (
                          <Badge key={tag} variant="secondary">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button className="w-full" onClick={() => handleEnroll(path.id)}>
                      立即加入
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-muted-foreground">暂无推荐学习路径</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
