"use client"

import { useEffect, useState } from "react"
import { Brain, ChevronRight, HelpCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Slider } from "@/components/ui/slider"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// 临时使用的用户ID，实际应用中应该从认证系统获取
const TEMP_USER_ID = 1

// 学习风格映射函数
const mapLearningStyle = (style: string): string => {
  const styleMap: Record<string, string> = {
    visual: "视觉学习者",
    auditory: "听觉学习者",
    kinesthetic: "动手学习者",
    reading: "阅读/写作学习者",
  }
  return styleMap[style.toLowerCase()] || style
}

interface Question {
  id: number
  text: string
  info?: string
}

interface AssessmentResult {
  primaryStyle: string
  secondaryStyle: string
  recommendations: string[]
}

export default function AssessmentPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [currentStep, setCurrentStep] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchQuestions = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await apiService.getAssessmentQuestions()
        if (!data || data.length === 0) {
          throw new Error("无法获取评估问题")
        }

        setQuestions(
          data.map((q: any) => ({
            id: q.id,
            text: q.text || q.question_text,
            info: q.info || "这有助于我们了解您的学习偏好。",
          })),
        )
      } catch (error) {
        console.error("Failed to fetch assessment questions:", error)
        setError("获取评估问题失败，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    fetchQuestions()
  }, [])

  const handleSliderChange = (questionId: number, value: number[]) => {
    setAnswers({
      ...answers,
      [questionId]: value[0],
    })
  }

  const isComplete = questions.length > 0 && Object.keys(answers).length === questions.length

  const getSliderLabel = (value: number) => {
    if (value <= 20) return "强烈不同意"
    if (value <= 40) return "不同意"
    if (value <= 60) return "中立"
    if (value <= 80) return "同意"
    return "强烈同意"
  }

  const handleSubmit = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // 将答案转换为API需要的格式
      const responses = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: Number.parseInt(questionId),
        response_value: answer,
        response_time: Math.floor(Math.random() * 5) + 1, // 随机响应时间（1-5秒）
      }))

      console.log("Submitting assessment with data:", { user_id: TEMP_USER_ID, responses })

      const assessmentResult = await apiService.submitAssessment(TEMP_USER_ID, responses)

      // 添加调试日志
      console.log("API Response:", assessmentResult)

      // 使用默认值处理API返回的结果
      const defaultRecommendations = [
        "使用视觉辅助工具如图表、思维导图和在笔记中使用颜色编码",
        "观看学习新概念时的视频演示",
        "融入动手实践和实验",
        "尝试向他人教授概念以加强理解",
        "在学习过程中定期休息以保持专注",
      ]

      try {
        const {
          dominant_style = "visual",
          secondary_style = "kinesthetic",
          recommended_content = [],
        } = assessmentResult || {}

        // 转换为前端显示格式
        setResult({
          primaryStyle: mapLearningStyle(dominant_style),
          secondaryStyle: mapLearningStyle(secondary_style),
          recommendations:
            Array.isArray(recommended_content) && recommended_content.length > 0
              ? recommended_content.map((rec: any) => {
                  if (typeof rec === "string") return rec
                  return rec?.title || rec?.content || String(rec)
                })
              : defaultRecommendations,
        })
      } catch (error) {
        console.error("Error processing assessment result:", error)
        // 使用默认值
        setResult({
          primaryStyle: "视觉学习者",
          secondaryStyle: "动手学习者",
          recommendations: defaultRecommendations,
        })
      }

      setCurrentStep(1)
    } catch (error) {
      console.error("Failed to submit assessment:", error)
      setError("提交评估失败，请稍后再试")

      // 即使出错，也显示一些结果，以便用户可以继续使用应用
      setResult({
        primaryStyle: "视觉学习者",
        secondaryStyle: "动手学习者",
        recommendations: [
          "使用视觉辅助工具如图表、思维导图和在笔记中使用颜色编码",
          "观看学习新概念时的视频演示",
          "融入动手实践和实验",
          "尝试向他人教授概念以加强理解",
          "在学习过程中定期休息以保持专注",
        ],
      })
      setCurrentStep(1)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container py-6">
      <div className="flex items-center gap-2 mb-6">
        <SidebarTrigger />
        <h1 className="text-3xl font-bold tracking-tight">学习风格评估</h1>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {currentStep === 0 ? (
        <Card className="max-w-3xl mx-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>评估您的学习风格</CardTitle>
              <Brain className="h-6 w-6 text-primary" />
            </div>
            <CardDescription>
              回答以下问题，帮助我们了解您的学习偏好。移动滑块表示您对每个陈述的同意或不同意程度。
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-8">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="space-y-4">
                    <div className="flex items-start gap-2">
                      <div className="flex-1">
                        <Skeleton className="h-5 w-full" />
                      </div>
                      <Skeleton className="h-6 w-6 rounded-full" />
                    </div>
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-full" />
                      <div className="flex justify-between">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                      <Skeleton className="h-4 w-32 mx-auto" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-8">
                {questions.map((question) => (
                  <div key={question.id} className="space-y-4">
                    <div className="flex items-start gap-2">
                      <div className="flex-1">
                        <h3 className="text-base font-medium">{question.text}</h3>
                      </div>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                              <HelpCircle className="h-4 w-4" />
                              <span className="sr-only">信息</span>
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{question.info}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    <div className="space-y-2">
                      <Slider
                        defaultValue={[50]}
                        max={100}
                        step={1}
                        value={[answers[question.id] || 50]}
                        onValueChange={(value) => handleSliderChange(question.id, value)}
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>强烈不同意</span>
                        <span>中立</span>
                        <span>强烈同意</span>
                      </div>
                      <div className="text-center text-sm font-medium">
                        {getSliderLabel(answers[question.id] || 50)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button className="w-full" disabled={!isComplete || isLoading} onClick={handleSubmit}>
              {isLoading ? "提交中..." : "提交评估"}
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <Card className="max-w-3xl mx-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>您的学习风格结果</CardTitle>
              <Brain className="h-6 w-6 text-primary" />
            </div>
            <CardDescription>基于您的回答，我们分析了您的学习风格偏好。</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="rounded-lg border p-4">
                <h3 className="text-lg font-medium mb-2">主要学习风格: {result?.primaryStyle}</h3>
                <p className="text-muted-foreground">
                  您倾向于通过视觉材料如图表、图表和书面信息来学习。视觉学习者受益于以视觉格式呈现的信息。
                </p>
              </div>

              <div className="rounded-lg border p-4">
                <h3 className="text-lg font-medium mb-2">次要学习风格: {result?.secondaryStyle}</h3>
                <p className="text-muted-foreground">
                  您也表现出对动手学习和实践练习的强烈偏好。动手学习者受益于积极参与和与材料的物理接触。
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="text-lg font-medium">建议:</h3>
                <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                  {result?.recommendations.map((recommendation, index) => (
                    <li key={index}>{recommendation}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-2 sm:flex-row">
            <Button variant="outline" className="w-full sm:w-auto" onClick={() => setCurrentStep(0)}>
              重新评估
            </Button>
            <Button className="w-full sm:w-auto" asChild>
              <a href="/learning-paths">
                查看推荐学习路径
                <ChevronRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
