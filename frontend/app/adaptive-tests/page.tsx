"use client"

import { useState } from "react"
import { Brain, CheckCircle, ChevronRight, Clock, Search, TestTube } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useRouter } from "next/navigation"

// Mock data - would be replaced with actual API calls
const mockAvailableTests = [
  {
    id: 1,
    title: "Python Basics",
    description: "Test your knowledge of Python fundamentals",
    estimatedTime: "30 minutes",
    difficulty: "Beginner",
    questions: 15,
    tags: ["Python", "Programming"],
  },
  {
    id: 2,
    title: "Web Development Concepts",
    description: "Test your understanding of web development principles",
    estimatedTime: "45 minutes",
    difficulty: "Intermediate",
    questions: 20,
    tags: ["Web", "HTML", "CSS", "JavaScript"],
  },
  {
    id: 3,
    title: "Data Science Fundamentals",
    description: "Evaluate your data science knowledge",
    estimatedTime: "60 minutes",
    difficulty: "Advanced",
    questions: 25,
    tags: ["Data Science", "Statistics", "Python"],
  },
]

const mockCompletedTests = [
  {
    id: 4,
    title: "JavaScript Basics",
    description: "Test your knowledge of JavaScript fundamentals",
    completedDate: "2023-04-10",
    score: 85,
    questions: 15,
    correctAnswers: 13,
    tags: ["JavaScript", "Web"],
  },
  {
    id: 5,
    title: "HTML and CSS",
    description: "Test your understanding of HTML and CSS",
    completedDate: "2023-04-05",
    score: 90,
    questions: 20,
    correctAnswers: 18,
    tags: ["HTML", "CSS", "Web"],
  },
]

export default function AdaptiveTestsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [difficultyFilter, setDifficultyFilter] = useState("all")

  const filteredAvailableTests = mockAvailableTests.filter((test) => {
    const matchesSearch =
      test.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesDifficulty =
      difficultyFilter === "all" || test.difficulty.toLowerCase() === difficultyFilter.toLowerCase()

    return matchesSearch && matchesDifficulty
  })

  const filteredCompletedTests = mockCompletedTests.filter(
    (test) =>
      test.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleTestClick = (testId: number) => {
    router.push(`/adaptive-tests/${testId}`)
  }

  const handleResultsClick = (testId: number) => {
    router.push(`/adaptive-tests/${testId}/results`)
  }

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SidebarTrigger />
          <h1 className="text-3xl font-bold tracking-tight">Adaptive Tests</h1>
        </div>
        <div className="flex gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tests..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by difficulty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Difficulties</SelectItem>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Tabs defaultValue="available" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="available">Available Tests</TabsTrigger>
          <TabsTrigger value="completed">Completed Tests</TabsTrigger>
        </TabsList>

        <TabsContent value="available">
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
                      <span>Estimated time: {test.estimatedTime}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Brain className="h-4 w-4" />
                      <span>Difficulty: {test.difficulty}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <CheckCircle className="h-4 w-4" />
                      <span>{test.questions} questions</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {test.tags.map((tag) => (
                        <Badge key={tag} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
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
                    Start Test
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="completed">
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
                      <span className="font-medium">Score:</span>
                      <span
                        className={`${test.score >= 80 ? "text-green-500" : test.score >= 60 ? "text-yellow-500" : "text-red-500"}`}
                      >
                        {test.score}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <CheckCircle className="h-4 w-4" />
                      <span>
                        {test.correctAnswers} of {test.questions} correct
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span>Completed on: {test.completedDate}</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {test.tags.map((tag) => (
                        <Badge key={tag} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
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
                    View Results
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
