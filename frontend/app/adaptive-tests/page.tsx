"use client"

import { useEffect, useState } from "react"
import { Brain, CheckCircle, ChevronRight, Clock, Search, TestTube } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useRouter } from "next/navigation"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// 临时使用的用户ID
const TEMP_USER_ID = 1

export default function AdaptiveTestsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [difficultyFilter, setDifficultyFilter] = useState("all")
  const [availableTests, setAvailableTests] = useState<any[]>([])
  const [completedTests, setCompletedTests] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTests() {
      setIsLoading(true)
      setError(null)
      
      try {
        console.log("开始获取测试数据...")
        
        // 从后端API获取可用测试列表
        const available = await apiService.getAvailableTests()
        console.log("获取到可用测试:", available?.length || 0)
        setAvailableTests(available || []);
        
        // 获取已完成测试列表
        const completed = await apiService.getCompletedTests(TEMP_USER_ID)
        console.log("获取到已完成测试:", completed?.length || 0)
        setCompletedTests(completed || []);
      } catch (e) {
        console.error("获取测试数据失败:", e)
        setError("获取测试数据失败，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchTests()
  }, [])

  const filteredAvailableTests = availableTests.filter((test) => {
    const matchesSearch =
      test.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesDifficulty =
      difficultyFilter === "all" || test.difficulty?.toLowerCase() === difficultyFilter.toLowerCase()

    return matchesSearch && matchesDifficulty
  })

  const filteredCompletedTests = completedTests.filter(
    (test) =>
      test.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleTestClick = (testId: number) => {
    router.push(`/adaptive-tests/${testId}`)
  }

  const handleResultsClick = (testId: number) => {
    router.push(`/adaptive-tests/${testId}/results`)
  }

  if (error) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <SidebarTrigger />
            <h1 className="text-3xl font-bold tracking-tight">自适应测试</h1>
          </div>
        </div>
        
        <Alert variant="destructive">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        
        <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
          重试
        </Button>
      </div>
    )
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">自适应测试</h1>
        </div>
        <div className="flex gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索测试..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="按难度过滤" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">所有难度</SelectItem>
              <SelectItem value="beginner">初级</SelectItem>
              <SelectItem value="intermediate">中级</SelectItem>
              <SelectItem value="advanced">高级</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="flex flex-col">
              <CardHeader>
                <Skeleton className="h-6 w-2/3 mb-2" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent className="flex-1">
                <div className="space-y-4">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-4 w-2/3" />
                  <div className="flex flex-wrap gap-2 mt-2">
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-6 w-20" />
                    <Skeleton className="h-6 w-12" />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Skeleton className="h-10 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : (
        <Tabs defaultValue="available" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="available">可用测试</TabsTrigger>
            <TabsTrigger value="completed">已完成测试</TabsTrigger>
          </TabsList>

          <TabsContent value="available">
            {filteredAvailableTests.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {filteredAvailableTests.map((test) => (
                  <Card
                    key={test.id}
                    className="flex flex-col cursor-pointer hover:border-primary/50 transition-colors"
                    onClick={() => handleTestClick(test.id)}
                  >
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <CardTitle>{test.title}</CardTitle>
                        <TestTube className="h-5 w-5 text-primary" />
                      </div>
                      <CardDescription>{test.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>预计时间: {test.estimatedTime || "30分钟"}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Brain className="h-4 w-4" />
                          <span>难度: {test.difficulty || "中等"}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="h-4 w-4" />
                          <span>{test.questions || 10} 个问题</span>
                        </div>
                        {test.tags && test.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {test.tags.map((tag: string) => (
                              <Badge key={tag} variant="secondary">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button
                        className="w-full"
                        onClick={(e) => {
                          e.stopPropagation()
                          router.push(`/adaptive-tests/${test.id}/take`)
                        }}
                      >
                        开始测试
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">暂无可用的测试</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="completed">
            {filteredCompletedTests.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {filteredCompletedTests.map((test) => (
                  <Card
                    key={test.id}
                    className="flex flex-col cursor-pointer hover:border-primary/50 transition-colors"
                    onClick={() => handleTestClick(test.id)}
                  >
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <CardTitle>{test.title}</CardTitle>
                        <TestTube className="h-5 w-5 text-primary" />
                      </div>
                      <CardDescription>{test.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium">得分:</span>
                          <span
                            className={`${
                              test.score >= 80 
                                ? "text-green-500" 
                                : test.score >= 60 
                                  ? "text-yellow-500" 
                                  : "text-red-500"
                            }`}
                          >
                            {test.score}%
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="h-4 w-4" />
                          <span>
                            {test.correctAnswers} / {test.totalQuestions} 正确
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>完成于: {test.completedDate}</span>
                        </div>
                        {test.tags && test.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {test.tags.map((tag: string) => (
                              <Badge key={tag} variant="secondary">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleResultsClick(test.id)
                        }}
                      >
                        查看结果
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">暂无已完成的测试</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
