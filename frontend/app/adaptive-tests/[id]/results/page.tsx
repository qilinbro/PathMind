"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, CheckCircle, Home, XCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { apiService } from "@/lib/api-service"

// 临时使用的用户ID
const TEMP_USER_ID = 1

export default function TestResultsPage() {
  const params = useParams()
  const router = useRouter()
  const [results, setResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchResults = async () => {
      setIsLoading(true)
      setError(null)
      try {
        // 通过API获取测试结果
        const testId = typeof params.id === 'string' ? parseInt(params.id, 10) : Number(params.id);
        const data = await apiService.getTestResults(testId, TEMP_USER_ID);
        
        if (!data) {
          setError("未找到测试结果");
          return;
        }
        
        setResults(data);
      } catch (error) {
        console.error("Failed to fetch test results:", error)
        setError("获取测试结果失败，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    if (params.id) {
      fetchResults()
    }
  }, [params.id])

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500"
    if (score >= 60) return "text-yellow-500"
    return "text-red-500"
  }

  return (
    <div className="container py-6 max-w-3xl">
      <div className="flex items-center gap-2 mb-6">
        <Button variant="ghost" size="sm" onClick={() => router.push("/adaptive-tests")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回测试列表
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">测试结果</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="space-y-6">
          <Card>
            <CardHeader className="text-center">
              <Skeleton className="h-8 w-40 mx-auto" />
              <Skeleton className="h-24 w-24 rounded-full mx-auto my-4" />
              <Skeleton className="h-6 w-32 mx-auto" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-40" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </CardContent>
          </Card>
        </div>
      ) : results ? (
        <div className="space-y-6">
          <Card>
            <CardHeader className="text-center">
              <CardTitle>测试得分</CardTitle>
              <div className="relative w-24 h-24 mx-auto my-4">
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-3xl font-bold ${getScoreColor(results.score)}`}>{results.score}%</span>
                </div>
                <svg className="w-full h-full" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#eee"
                    strokeWidth="3"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke={results.score >= 80 ? "#10b981" : results.score >= 60 ? "#f59e0b" : "#ef4444"}
                    strokeWidth="3"
                    strokeDasharray={`${results.score}, 100`}
                  />
                </svg>
              </div>
              <CardDescription>
                {results.correctAnswers} / {results.totalQuestions} 正确答案 | 用时 {results.timeSpent || "未记录"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.strengths && results.strengths.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2">优势领域</h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {results.strengths.map((strength: string, index: number) => (
                        <li key={index} className="text-muted-foreground">
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {results.weaknesses && results.weaknesses.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2">需要改进的领域</h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {results.weaknesses.map((weakness: string, index: number) => (
                        <li key={index} className="text-muted-foreground">
                          {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {results.recommendations && results.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>学习建议</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  {results.recommendations.map((recommendation: string, index: number) => (
                    <li key={index} className="text-muted-foreground">
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <div className="flex flex-col sm:flex-row gap-2 w-full">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => router.push(`/adaptive-tests/${params.id}`)}
                  >
                    查看详情
                  </Button>
                  <Button className="w-full" onClick={() => router.push("/adaptive-tests")}>
                    <Home className="mr-2 h-4 w-4" />
                    返回测试列表
                  </Button>
                </div>
              </CardFooter>
            </Card>
          )}

          {results.questionAnalysis && results.questionAnalysis.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>问题分析</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.questionAnalysis.map((question: any) => (
                    <div key={question.id} className="flex items-start gap-3 p-3 rounded-lg border">
                      {question.correct ? (
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">问题 {question.id}</p>
                        <div className="flex gap-2 mt-1 text-sm text-muted-foreground">
                          <span>主题: {question.topic}</span>
                          <span>•</span>
                          <span>难度: {question.difficulty}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">未找到测试结果</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push("/adaptive-tests")}>
            返回测试列表
          </Button>
        </div>
      )}
    </div>
  )
}
