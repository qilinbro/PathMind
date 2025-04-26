import Link from "next/link"
import { Brain } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="flex items-center gap-2 mr-4">
            <Brain className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">PathMind</span>
          </div>
          <nav className="flex flex-1 items-center justify-between">
            <div className="flex gap-6 text-sm">
              <Link href="/dashboard" className="transition-colors hover:text-foreground/80">
                Dashboard
              </Link>
              <Link href="/learning-paths" className="transition-colors hover:text-foreground/80">
                Learning Paths
              </Link>
              <Link href="/assessment" className="transition-colors hover:text-foreground/80">
                Assessment
              </Link>
              <Link href="/analytics" className="transition-colors hover:text-foreground/80">
                Analytics
              </Link>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" asChild>
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Sign Up</Link>
              </Button>
            </div>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 xl:grid-cols-2">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                    Personalized Learning Paths for Everyone
                  </h1>
                  <p className="max-w-[600px] text-muted-foreground md:text-xl">
                    PathMind uses AI to create personalized learning experiences based on your unique learning style and
                    goals.
                  </p>
                </div>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Button size="lg" asChild>
                    <Link href="/dashboard">Get Started</Link>
                  </Button>
                  <Button size="lg" variant="outline" asChild>
                    <Link href="/assessment">Take Assessment</Link>
                  </Button>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <img
                  src="/placeholder.svg?height=550&width=550"
                  width={550}
                  height={550}
                  alt="Hero Image"
                  className="rounded-lg object-cover"
                />
              </div>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Key Features</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Discover how PathMind helps you learn more effectively
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-2 lg:grid-cols-3">
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-6">
                <div className="rounded-full bg-primary/10 p-2">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Learning Style Assessment</h3>
                <p className="text-center text-muted-foreground">
                  Discover your unique learning style and get personalized recommendations.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-6">
                <div className="rounded-full bg-primary/10 p-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6 text-primary"
                  >
                    <path d="M18 6H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h13l4-3.5L18 6Z" />
                    <path d="M12 13v8" />
                    <path d="M5 13v6a2 2 0 0 0 2 2h8" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">Adaptive Learning Paths</h3>
                <p className="text-center text-muted-foreground">
                  Follow customized learning paths that adapt to your progress and preferences.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-6">
                <div className="rounded-full bg-primary/10 p-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6 text-primary"
                  >
                    <path d="M2 12h10" />
                    <path d="M9 4v16" />
                    <path d="M14 9h8" />
                    <path d="M18 5v8" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">Personalized Testing</h3>
                <p className="text-center text-muted-foreground">
                  Take adaptive tests that focus on your areas for improvement.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t py-6">
        <div className="container flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
              © 2023 PathMind. All rights reserved.
            </p>
          </div>
          <nav className="flex gap-4 text-sm">
            <Link href="#" className="text-muted-foreground underline underline-offset-4">
              Terms
            </Link>
            <Link href="#" className="text-muted-foreground underline underline-offset-4">
              Privacy
            </Link>
            <Link href="#" className="text-muted-foreground underline underline-offset-4">
              Contact
            </Link>
          </nav>
        </div>
      </footer>
    </div>
  )
}
