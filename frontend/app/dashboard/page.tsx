"use client"

import { useEffect, useState } from "react"
import { Activity, BookOpen, Brain, RefreshCw, Route } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// 临时使用的用户ID，实际应用中应该从认证系统获取
const TEMP_USER_ID = 1

interface UserData {
  id: number
  name: string
  email: string
  learningStyle: string
  progress: number
  completedPaths: number
  activePaths: number
  completedTests: number
  recentActivities: Array<{
    id: number
    type: string
    title: string
    date: string
    score?: number
    progress?: number
    result?: string
  }>
}

export default function DashboardPage() {
  const [userData, setUserData] = useState<UserData | null>(null)
  const [recommendedPaths, setRecommendedPaths] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hasAssessment, setHasAssessment] = useState(true)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // 在实际应用中，这些请求应该并行发送
      const userProgress = await apiService.getUserProgress(TEMP_USER_ID)
      const recommendedPathsData = await apiService.getRecommendedPaths()

      // 检查是否有评估数据
      if (!userProgress || !userProgress.learning_style) {
        setHasAssessment(false)
        setUserData({
          id: TEMP_USER_ID,
          name: "新用户",
          email: "user@example.com",
          learningStyle: "未知",
          progress: 0,
          completedPaths: 0,
          activePaths: 0,
          completedTests: 0,
          recentActivities: [],
        })
      } else {
        // 假设API返回的数据需要转换为前端需要的格式
        setUserData({
          id: TEMP_USER_ID,
          name: userProgress.name || "用户名",
          email: userProgress.email || "user@example.com",
          learningStyle: userProgress.learning_style || "视觉",
          progress: userProgress.overall_progress || 0,
          completedPaths: userProgress.completed_paths || 0,
          activePaths: userProgress.active_paths || 0,
          completedTests: userProgress.completed_tests || 0,
          recentActivities: userProgress.recent_activities || [],
        })
        setHasAssessment(true)
      }

      setRecommendedPaths(recommendedPathsData || [])
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error)
      setError("获取数据失败，请稍后再试")

      // 设置默认数据，以防API调用失败
      setUserData({
        id: TEMP_USER_ID,
        name: "用户名",
        email: "user@example.com",
        learningStyle: "未知",
        progress: 0,
        completedPaths: 0,
        activePaths: 0,
        completedTests: 0,
        recentActivities: [],
      })
      setRecommendedPaths([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
        </div>
        <Button onClick={fetchData} disabled={isLoading} size="sm">
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          刷新
        </Button>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {!hasAssessment && !isLoading && (
        <Alert className="mb-6">
          <Brain className="h-4 w-4" />
          <AlertTitle>欢迎使用PathMind</AlertTitle>
          <AlertDescription>
            您尚未完成学习风格评估。完成评估后，我们可以为您提供个性化的学习体验。
            <Button variant="outline" size="sm" className="ml-2" asChild>
              <a href="/assessment">开始评估</a>
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">学习风格</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <>
                <div className="text-2xl font-bold">{userData?.learningStyle}</div>
                <p className="text-xs text-muted-foreground">
                  {hasAssessment ? "基于您的评估" : "完成评估以了解您的学习风格"}
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总体进度</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <>
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-2 w-full" />
              </>
            ) : (
              <>
                <div className="text-2xl font-bold">{userData?.progress}%</div>
                <Progress value={userData?.progress} className="mt-2" />
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">学习路径</CardTitle>
            <Route className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <>
                <Skeleton className="h-8 w-8 mb-1" />
                <Skeleton className="h-4 w-24" />
              </>
            ) : (
              <>
                <div className="text-2xl font-bold">{userData?.activePaths}</div>
                <p className="text-xs text-muted-foreground">{userData?.completedPaths} 已完成</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已完成测试</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <>
                <Skeleton className="h-8 w-8 mb-1" />
                <Skeleton className="h-4 w-36" />
              </>
            ) : (
              <>
                <div className="text-2xl font-bold">{userData?.completedTests}</div>
                <p className="text-xs text-muted-foreground">所有学习路径中</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7 mt-6">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>最近活动</CardTitle>
            <CardDescription>您最近的学习活动</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-4 rounded-lg border p-3">
                    <Skeleton className="h-5 w-5 rounded-full" />
                    <div className="flex-1 space-y-1">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                    </div>
                    <Skeleton className="h-4 w-16" />
                  </div>
                ))}
              </div>
            ) : userData?.recentActivities && userData.recentActivities.length > 0 ? (
              <div className="space-y-4">
                {userData.recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-center gap-4 rounded-lg border p-3">
                    {activity.type === "test" && <BookOpen className="h-5 w-5 text-primary" />}
                    {activity.type === "path" && <Route className="h-5 w-5 text-primary" />}
                    {activity.type === "assessment" && <Brain className="h-5 w-5 text-primary" />}
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">{activity.title}</p>
                      <p className="text-xs text-muted-foreground">{activity.date}</p>
                    </div>
                    <div className="text-sm font-medium">
                      {activity.score && `得分: ${activity.score}%`}
                      {activity.progress && `进度: ${activity.progress}%`}
                      {activity.result && `结果: ${activity.result}`}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-muted-foreground mb-4">暂无活动记录</p>
                <Button variant="outline" asChild>
                  <a href="/learning-paths">开始学习</a>
                </Button>
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full" disabled={!userData?.recentActivities?.length}>
              查看所有活动
            </Button>
          </CardFooter>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>推荐学习路径</CardTitle>
            <CardDescription>基于您的学习风格和进度</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <Skeleton className="h-5 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-full mb-2" />
                    <div className="flex justify-end mt-2">
                      <Skeleton className="h-9 w-20" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recommendedPaths && recommendedPaths.length > 0 ? (
              <div className="space-y-4">
                {recommendedPaths.map((path) => (
                  <div key={path.id} className="rounded-lg border p-3">
                    <h3 className="font-medium">{path.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{path.description}</p>
                    <div className="flex justify-end mt-2">
                      <Button size="sm" onClick={() => apiService.enrollLearningPath(TEMP_USER_ID, path.id)}>
                        加入
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-muted-foreground mb-4">暂无推荐学习路径</p>
                <Button variant="outline" asChild>
                  <a href="/learning-paths">浏览所有路径</a>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
