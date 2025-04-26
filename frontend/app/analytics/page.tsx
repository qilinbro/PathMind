"use client"

import { useEffect, useState } from "react"
import { Activity, Brain, Calendar, Clock } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Line,
  LineChart,
  Bar,
  BarChart,
  Pie,
  PieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"

// 临时使用的用户ID，实际应用中应该从认证系统获取
const TEMP_USER_ID = 1

const COLORS = ["#8b5cf6", "#14b8a6", "#f59e0b", "#ef4444", "#3b82f6"]

interface AnalyticsData {
  totalStudyTime: number
  averageScore: number
  completedTests: number
  studySessions: number
  activityData: Array<{ date: string; minutes: number }>
  performanceData: Array<{ subject: string; score: number }>
  learningStyleData: Array<{ name: string; value: number }>
  strengths: Array<{ title: string; description: string }>
  improvements: Array<{ title: string; description: string }>
  behaviorAnalysis: {
    consistency: { description: string; recommendation: string }
    duration: { description: string; recommendation: string }
    engagement: { description: string; recommendation: string }
  }
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("week")
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true)
      try {
        const data = await apiService.getUserAnalytics(TEMP_USER_ID)

        // 假设API返回的数据需要转换为前端需要的格式
        // 实际情况下，这里的转换逻辑应该根据API的实际返回格式调整
        setAnalyticsData({
          totalStudyTime: data.total_study_time || 465,
          averageScore: data.average_score || 76,
          completedTests: data.completed_tests || 8,
          studySessions: data.study_sessions || 12,
          activityData: data.activity_data || [
            { date: "周一", minutes: 45 },
            { date: "周二", minutes: 60 },
            { date: "周三", minutes: 30 },
            { date: "周四", minutes: 90 },
            { date: "周五", minutes: 75 },
            { date: "周六", minutes: 120 },
            { date: "周日", minutes: 45 },
          ],
          performanceData: data.performance_data || [
            { subject: "Python", score: 85 },
            { subject: "Web开发", score: 70 },
            { subject: "数据科学", score: 60 },
            { subject: "算法", score: 75 },
            { subject: "数据库", score: 90 },
          ],
          learningStyleData: data.learning_style_data || [
            { name: "视觉", value: 60 },
            { name: "听觉", value: 20 },
            { name: "动手", value: 20 },
          ],
          strengths: data.strengths || [
            {
              title: "数据库",
              description: "您在数据库概念和SQL查询方面的得分始终很高。",
            },
            {
              title: "Python编程",
              description: "您的Python技能很强，特别是在数据结构方面。",
            },
          ],
          improvements: data.improvements || [
            {
              title: "数据科学",
              description: "专注于统计概念和数据可视化技术。",
            },
            {
              title: "Web开发",
              description: "加强JavaScript框架和响应式设计原则。",
            },
          ],
          behaviorAnalysis: data.behavior_analysis || {
            consistency: {
              description: "您倾向于在工作日更加一致地学习，周二和周四达到高峰。周末学习不太一致。",
              recommendation: "尝试建立更一致的周末学习习惯，以保持动力。",
            },
            duration: {
              description: "您的平均学习时间为45分钟，略低于最佳学习保留的推荐时间。",
              recommendation: "争取60-90分钟的专注学习时间，中间短暂休息。",
            },
            engagement: {
              description: "您最喜欢互动内容和视频教程，但花在基于文本的材料上的时间较少。",
              recommendation: "平衡您的学习，增加更多基于文本的资源，以提高阅读理解能力。",
            },
          },
        })
      } catch (error) {
        console.error("Failed to fetch analytics data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalytics()
  }, [timeRange]) // 当时间范围改变时重新获取数据

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">学习分析</h1>
        </div>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="选择时间范围" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="week">最近一周</SelectItem>
            <SelectItem value="month">最近一个月</SelectItem>
            <SelectItem value="year">最近一年</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="overview">概览</TabsTrigger>
          <TabsTrigger value="performance">表现</TabsTrigger>
          <TabsTrigger value="behavior">学习行为</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">总学习时间</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{analyticsData?.totalStudyTime} 分钟</div>
                    <p className="text-xs text-muted-foreground">较上周 +12%</p>
                  </>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">平均分数</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{analyticsData?.averageScore}%</div>
                    <p className="text-xs text-muted-foreground">较上周 +5%</p>
                  </>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">已完成测试</CardTitle>
                <Brain className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-8" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{analyticsData?.completedTests}</div>
                    <p className="text-xs text-muted-foreground">较上周 +2</p>
                  </>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">学习会话</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-8" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{analyticsData?.studySessions}</div>
                    <p className="text-xs text-muted-foreground">较上周 +3</p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>每日学习时间</CardTitle>
                <CardDescription>每天花费在学习上的分钟数</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-[300px] w-full" />
                ) : (
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analyticsData?.activityData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="minutes" stroke="#8b5cf6" activeDot={{ r: 8 }} name="分钟" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>学习风格分布</CardTitle>
                <CardDescription>您的学习风格偏好</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-[300px] w-full" />
                ) : (
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analyticsData?.learningStyleData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {analyticsData?.learningStyleData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>学科表现</CardTitle>
                <CardDescription>您在不同学科的测试分数</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-[400px] w-full" />
                ) : (
                  <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData?.performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="subject" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="score" fill="#8b5cf6" name="分数" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>优势</CardTitle>
                  <CardDescription>您擅长的领域</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <div key={i} className="flex items-start gap-2">
                          <Skeleton className="h-6 w-6 rounded-full" />
                          <div className="flex-1">
                            <Skeleton className="h-5 w-24 mb-1" />
                            <Skeleton className="h-4 w-full" />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <ul className="space-y-4">
                      {analyticsData?.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="rounded-full bg-green-500/20 p-1">
                            <div className="h-2 w-2 rounded-full bg-green-500" />
                          </div>
                          <div>
                            <p className="font-medium">{strength.title}</p>
                            <p className="text-sm text-muted-foreground">{strength.description}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>需要改进的领域</CardTitle>
                  <CardDescription>需要关注的主题</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <div key={i} className="flex items-start gap-2">
                          <Skeleton className="h-6 w-6 rounded-full" />
                          <div className="flex-1">
                            <Skeleton className="h-5 w-24 mb-1" />
                            <Skeleton className="h-4 w-full" />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <ul className="space-y-4">
                      {analyticsData?.improvements.map((improvement, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="rounded-full bg-red-500/20 p-1">
                            <div className="h-2 w-2 rounded-full bg-red-500" />
                          </div>
                          <div>
                            <p className="font-medium">{improvement.title}</p>
                            <p className="text-sm text-muted-foreground">{improvement.description}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="behavior">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>学习行为分析</CardTitle>
                <CardDescription>对您学习模式的洞察</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-6">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="rounded-lg border p-4">
                        <Skeleton className="h-6 w-48 mb-2" />
                        <Skeleton className="h-4 w-full mb-4" />
                        <Skeleton className="h-5 w-32 mb-1" />
                        <Skeleton className="h-4 w-full" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="rounded-lg border p-4">
                      <h3 className="text-lg font-medium mb-2">学习一致性</h3>
                      <p className="text-muted-foreground mb-4">
                        {analyticsData?.behaviorAnalysis.consistency.description}
                      </p>
                      <div className="text-sm font-medium">建议:</div>
                      <p className="text-sm text-muted-foreground">
                        {analyticsData?.behaviorAnalysis.consistency.recommendation}
                      </p>
                    </div>

                    <div className="rounded-lg border p-4">
                      <h3 className="text-lg font-medium mb-2">学习时长</h3>
                      <p className="text-muted-foreground mb-4">
                        {analyticsData?.behaviorAnalysis.duration.description}
                      </p>
                      <div className="text-sm font-medium">建议:</div>
                      <p className="text-sm text-muted-foreground">
                        {analyticsData?.behaviorAnalysis.duration.recommendation}
                      </p>
                    </div>

                    <div className="rounded-lg border p-4">
                      <h3 className="text-lg font-medium mb-2">内容参与度</h3>
                      <p className="text-muted-foreground mb-4">
                        {analyticsData?.behaviorAnalysis.engagement.description}
                      </p>
                      <div className="text-sm font-medium">建议:</div>
                      <p className="text-sm text-muted-foreground">
                        {analyticsData?.behaviorAnalysis.engagement.recommendation}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
