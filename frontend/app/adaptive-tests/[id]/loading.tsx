import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="container py-6">
      <div className="flex items-center gap-2 mb-6">
        <Skeleton className="h-10 w-40" />
      </div>

      <div className="space-y-6">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-96 w-full" />
      </div>
    </div>
  )
}
