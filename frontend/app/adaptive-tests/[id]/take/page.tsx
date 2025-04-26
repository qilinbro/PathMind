"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, ArrowRight, Clock, HelpCircle } from "lucide-react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

// 模拟测试问题数据 - 实际应用中应该从API获取
const mockQuestions = [
  {
    id: 1,
    text: "在Python中，哪个关键字用于定义函数？",
    options: [
      { id: "a", text: "function" },
      { id: "b", text: "def" },
      { id: "c", text: "define" },
      { id: "d", text: "func" },
    ],
    explanation: "在Python中，'def'关键字用于定义函数。",
  },
  {
    id: 2,
    text: "以下哪个不是Python的内置数据类型？",
    options: [
      { id: "a", text: "list" },
      { id: "b", text: "dictionary" },
      { id: "c", text: "array" },
      { id: "d", text: "tuple" },
    ],
    explanation: "在Python中，'array'不是内置数据类型，而是需要通过导入array模块才能使用。",
  },
  {
    id: 3,
    text: "在Python中，如何获取字符串的长度？",
    options: [
      { id: "a", text: "str.length()" },
      { id: "b", text: "length(str)" },
      { id: "c", text: "len(str)" },
      { id: "d", text: "str.size()" },
    ],
    explanation: "在Python中，使用len()函数来获取字符串的长度。",
  },
]

export default function TakeTestPage() {
  const params = useParams()
  const router = useRouter()
  const [questions, setQuestions] = useState<any[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [timeLeft, setTimeLeft] = useState(1800) // 30分钟 = 1800秒
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showExplanation, setShowExplanation] = useState(false)

  useEffect(() => {
    const fetchQuestions = async () => {
      setIsLoading(true)
      setError(null)
      try {
        // 在实际应用中，这里应该从API获取测试问题
        // const data = await apiService.getTestQuestions(params.id)

        // 模拟API调用延迟
        await new Promise((resolve) => setTimeout(resolve, 500))

        // 使用模拟数据
        setQuestions(mockQuestions)
      } catch (error) {
        console.error("Failed to fetch test questions:", error)
        setError("获取测试问题失败，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    if (params.id) {
      fetchQuestions()
    }
  }, [params.id])

  // 计时器
  useEffect(() => {
    if (isLoading || questions.length === 0) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          // 时间到，自动提交
          handleSubmitTest()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isLoading, questions])

  const handleAnswerChange = (questionId: number, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }))
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1)
      setShowExplanation(false)
    }
  }

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1)
      setShowExplanation(false)
    }
  }

  const handleSubmitTest = () => {
    // 在实际应用中，这里应该提交测试答案到API
    // await apiService.submitTestAnswers(params.id, answers)

    // 导航到结果页面
    router.push(`/adaptive-tests/${params.id}/results`)
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`
  }

  const currentQuestion = questions[currentQuestionIndex]
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0

  return (
    <div className="container py-6 max-w-3xl">
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-8 w-20" />
          </div>
          <Skeleton className="h-4 w-full" />
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-full" />
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex items-start space-x-2">
                    <Skeleton className="h-4 w-4 mt-1" />
                    <Skeleton className="h-6 w-full" />
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <div className="flex justify-between w-full">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-24" />
              </div>
            </CardFooter>
          </Card>
        </div>
      ) : questions.length > 0 ? (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => router.push(`/adaptive-tests/${params.id}`)}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                退出测试
              </Button>
              <span className="text-sm text-muted-foreground">
                问题 {currentQuestionIndex + 1} / {questions.length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className={`font-mono ${timeLeft < 300 ? "text-red-500" : ""}`}>{formatTime(timeLeft)}</span>
            </div>
          </div>

          <Progress value={progress} className="h-2" />

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">{currentQuestion.text}</CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={answers[currentQuestion.id] || ""}
                onValueChange={(value) => handleAnswerChange(currentQuestion.id, value)}
              >
                <div className="space-y-4">
                  {currentQuestion.options.map((option: any) => (
                    <div key={option.id} className="flex items-center space-x-2">
                      <RadioGroupItem value={option.id} id={`option-${option.id}`} />
                      <Label htmlFor={`option-${option.id}`} className="text-base">
                        {option.text}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>

              {showExplanation && (
                <div className="mt-6 p-4 bg-muted rounded-md">
                  <h4 className="font-medium mb-1">解释：</h4>
                  <p className="text-muted-foreground">{currentQuestion.explanation}</p>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <div className="flex justify-between w-full">
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handlePrevQuestion} disabled={currentQuestionIndex === 0}>
                    上一题
                  </Button>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" onClick={() => setShowExplanation(!showExplanation)}>
                          <HelpCircle className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>显示/隐藏解释</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                {currentQuestionIndex < questions.length - 1 ? (
                  <Button onClick={handleNextQuestion}>
                    下一题
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                ) : (
                  <Button onClick={handleSubmitTest}>提交测试</Button>
                )}
              </div>
            </CardFooter>
          </Card>
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">未找到测试问题</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push("/adaptive-tests")}>
            返回测试列表
          </Button>
        </div>
      )}
    </div>
  )
}
