"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, BookOpen, Clock, Tag } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { apiService } from "@/lib/api-service"

// 临时使用的默认内容数据
const DEFAULT_CONTENT = {
  id: 0,
  title: "内容不可用",
  description: "无法加载请求的内容",
  content_type: "未知",
  subject: "未知",
  content_data: {
    text: "抱歉，内容不可用。可能是服务器错误或者内容不存在。",
  },
  read_time: "未知",
  tags: [],
}

export default function ContentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [content, setContent] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchContent = async () => {
      if (!params.id) return

      setIsLoading(true)
      try {
        const contentId = Number(params.id)
        console.log(`Fetching content with ID: ${contentId}`)

        const data = await apiService.getContent(contentId)
        if (data) {
          console.log("Content data received:", data)
          setContent(data)
        } else {
          console.warn(`Content with ID ${contentId} not found, using default content`)
          setContent(DEFAULT_CONTENT)
          setError("找不到请求的内容，显示默认内容")
        }
      } catch (err) {
        console.error("Error fetching content:", err)
        setContent(DEFAULT_CONTENT)
        setError("加载内容时发生错误，请稍后再试")
      } finally {
        setIsLoading(false)
      }
    }

    fetchContent()
  }, [params.id])

  // 格式化内容数据
  const formatContent = (contentData: any) => {
    if (!contentData) return <p className="text-muted-foreground">无内容数据</p>

    // 如果是纯文本
    if (typeof contentData === "string") {
      return <p className="whitespace-pre-wrap">{contentData}</p>
    }

    // 如果有text属性
    if (contentData.text) {
      return <p className="whitespace-pre-wrap">{contentData.text}</p>
    }

    // 如果有HTML内容
    if (contentData.html) {
      return <div dangerouslySetInnerHTML={{ __html: contentData.html }} />
    }

    // 处理其他类型的内容
    if (contentData.video_url) {
      return (
        <div className="aspect-video">
          <iframe
            className="w-full h-full rounded-md"
            src={contentData.video_url}
            title={content?.title || "视频内容"}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
      )
    }

    // 如果是复杂对象，显示为JSON
    return <pre className="p-4 bg-muted rounded-md overflow-auto">{JSON.stringify(contentData, null, 2)}</pre>
  }

  return (
    <div className="container py-6">
      <div className="flex items-center gap-2 mb-6">
        <SidebarTrigger />
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="mr-2">
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">内容详情</h1>
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
          <Skeleton className="h-4 w-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-24 rounded-full" />
          </div>
        </div>
      ) : (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl">{content?.title}</CardTitle>
                <CardDescription className="mt-1">{content?.description}</CardDescription>
              </div>
              <BookOpen className="h-6 w-6 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="rounded-lg border p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Tag className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">类型</span>
                  </div>
                  <span>{content?.content_type || "未知"}</span>
                </div>
                <div className="rounded-lg border p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <BookOpen className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">主题</span>
                  </div>
                  <span>{content?.subject || "未知"}</span>
                </div>
                <div className="rounded-lg border p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">阅读时间</span>
                  </div>
                  <span>{content?.read_time || content?.estimated_time || "未知"}</span>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">内容</h3>
                <div className="prose max-w-none dark:prose-invert">{formatContent(content?.content_data)}</div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">标签</h3>
                <div className="flex flex-wrap gap-2">
                  {content?.tags && content.tags.length > 0 ? (
                    content.tags.map((tag: string, index: number) => (
                      <Badge key={tag || index} variant="secondary">
                        {tag}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-muted-foreground">无标签</span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={() => router.push("/content")}>
              返回内容列表
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
