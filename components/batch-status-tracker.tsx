import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { CheckCircle2, Clock, Package } from "lucide-react"
import type { HerbBatch } from "@/lib/types"

interface BatchStatusTrackerProps {
  batches: HerbBatch[]
}

export function BatchStatusTracker({ batches }: BatchStatusTrackerProps) {
  const statusCounts = batches.reduce(
    (acc, batch) => {
      acc[batch.currentStatus] = (acc[batch.currentStatus] || 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  const statusConfig = {
    collected: { label: "Collected", color: "bg-blue-500", icon: Package },
    processing: { label: "Processing", color: "bg-yellow-500", icon: Clock },
    tested: { label: "Tested", color: "bg-purple-500", icon: CheckCircle2 },
    packaged: { label: "Packaged", color: "bg-green-500", icon: CheckCircle2 },
    distributed: { label: "Distributed", color: "bg-primary", icon: CheckCircle2 },
    sold: { label: "Sold", color: "bg-gray-500", icon: CheckCircle2 },
  }

  const totalBatches = batches.length
  const completedBatches = batches.filter((batch) => batch.traceabilityComplete).length
  const completionRate = totalBatches > 0 ? (completedBatches / totalBatches) * 100 : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          Batch Status Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Completion Rate */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Traceability Completion</span>
            <span className="text-sm text-muted-foreground">{Math.round(completionRate)}%</span>
          </div>
          <Progress value={completionRate} className="h-2" />
        </div>

        {/* Status Breakdown */}
        <div className="space-y-2">
          {Object.entries(statusConfig).map(([status, config]) => {
            const count = statusCounts[status] || 0
            const percentage = totalBatches > 0 ? (count / totalBatches) * 100 : 0
            const Icon = config.icon

            return (
              <div key={status} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${config.color}`} />
                  <span className="text-sm">{config.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{count}</span>
                  <span className="text-xs text-muted-foreground">({percentage.toFixed(0)}%)</span>
                </div>
              </div>
            )
          })}
        </div>

        {/* Summary Stats */}
        <div className="pt-4 border-t">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Total Batches:</span>
              <span className="ml-2 font-medium">{totalBatches}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Completed:</span>
              <span className="ml-2 font-medium">{completedBatches}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
