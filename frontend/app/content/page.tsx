"use client"

import { useEffect, useState } from "react"
import { BookOpen, ChevronRight, Clock, Filter, Search, Tag } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { apiService } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"

interface ContentItem {
  id: number
  title: string
  description: string
  type: string
  readTime: string
  tags: string[]
}

export default function ContentPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [allTags, setAllTags] = useState<string[]>([])
  const [contentTypes, setContentTypes] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchContent = async () => {
      setIsLoading(true)
      try {
        const data = await apiService.getAllContent()

        // 假设API返回的数据需要转换为前端需要的格式
        const formattedContent = data.map((item: any) => ({
          id: item.id,
          title: item.title,
          description: item.description,
          type: item.type || "文章",
          readTime: item.read_time || "10 分钟",
          tags: item.tags || [],
        }))

        setContentItems(formattedContent)

        // 提取所有标签和内容类型
        const tags = Array.from(new Set(formattedContent.flatMap((item) => item.tags)))
        const types = Array.from(new Set(formattedContent.map((item) => item.type)))

        setAllTags(tags)
        setContentTypes(types)
      } catch (error) {
        console.error("Failed to fetch content:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchContent()
  }, [])

  const filteredContent = contentItems.filter((content) => {
    const matchesSearch =
      content.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      content.description.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesTags = selectedTags.length === 0 || selectedTags.some((tag) => content.tags.includes(tag))

    const matchesTypes = selectedTypes.length === 0 || selectedTypes.includes(content.type)

    return matchesSearch && matchesTags && matchesTypes
  })

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]))
  }

  const toggleType = (type: string) => {
    setSelectedTypes((prev) => (prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]))
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">内容库</h1>
        </div>
        <div className="flex gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索内容..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>筛选内容</SheetTitle>
                <SheetDescription>按标签和类型筛选内容</SheetDescription>
              </SheetHeader>
              <div className="py-4">
                <h3 className="mb-2 text-sm font-medium">内容类型</h3>
                <div className="space-y-2">
                  {isLoading
                    ? Array(3)
                        .fill(0)
                        .map((_, i) => (
                          <div key={i} className="flex items-center space-x-2">
                            <Skeleton className="h-4 w-4 rounded" />
                            <Skeleton className="h-4 w-24" />
                          </div>
                        ))
                    : contentTypes.map((type) => (
                        <div key={type} className="flex items-center space-x-2">
                          <Checkbox
                            id={`type-${type}`}
                            checked={selectedTypes.includes(type)}
                            onCheckedChange={() => toggleType(type)}
                          />
                          <label
                            htmlFor={`type-${type}`}
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                          >
                            {type}
                          </label>
                        </div>
                      ))}
                </div>

                <Separator className="my-4" />

                <h3 className="mb-2 text-sm font-medium">标签</h3>
                {isLoading ? (
                  <div className="flex flex-wrap gap-2">
                    {Array(5)
                      .fill(0)
                      .map((_, i) => (
                        <Skeleton key={i} className="h-6 w-16 rounded-full" />
                      ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {allTags.map((tag) => (
                      <Badge
                        key={tag}
                        variant={selectedTags.includes(tag) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => toggleTag(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="mt-4 flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedTags([])
                      setSelectedTypes([])
                    }}
                  >
                    重置
                  </Button>
                  <SheetTrigger asChild>
                    <Button>应用筛选</Button>
                  </SheetTrigger>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          // 加载状态的骨架屏
          Array(6)
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
                    <Skeleton className="h-4 w-1/3" />
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
        ) : filteredContent.length > 0 ? (
          filteredContent.map((content) => (
            <Card key={content.id} className="flex flex-col">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle>{content.title}</CardTitle>
                  <BookOpen className="h-5 w-5 text-primary" />
                </div>
                <CardDescription>{content.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>{content.readTime} 阅读</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Tag className="h-4 w-4" />
                    <span>类型: {content.type}</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {content.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full" asChild>
                  <a href={`/content/${content.id}`}>
                    查看内容
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </a>
                </Button>
              </CardFooter>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-muted-foreground">没有找到匹配的内容</p>
            <Button
              className="mt-4"
              variant="outline"
              onClick={() => {
                setSearchQuery("")
                setSelectedTags([])
                setSelectedTypes([])
              }}
            >
              清除筛选条件
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
