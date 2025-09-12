import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock, MapPin, Package, TestTube } from "lucide-react"
import type { HerbBatch } from "@/lib/types"

interface TraceabilityTimelineProps {
  batch: HerbBatch
}

export function TraceabilityTimeline({ batch }: TraceabilityTimelineProps) {
  const events = [
    {
      id: "collection",
      title: "Collection",
      timestamp: batch.collectionEvent.timestamp,
      location: batch.collectionEvent.location.region,
      details: `${batch.collectionEvent.quantity} ${batch.collectionEvent.unit} collected by ${batch.collectionEvent.collectorName}`,
      icon: Package,
      completed: true,
    },
    ...batch.processingEvents.map((event, index) => ({
      id: `processing-${index}`,
      title: `Processing: ${event.processType}`,
      timestamp: event.timestamp,
      location: event.facilityLocation.region,
      details: `${event.inputQuantity} ${batch.collectionEvent.unit} → ${event.outputQuantity} ${batch.collectionEvent.unit}`,
      icon: event.processType === "testing" ? TestTube : Package,
      completed: event.verified,
    })),
  ]

  // Add final status
  if (batch.currentStatus === "packaged" || batch.currentStatus === "distributed" || batch.currentStatus === "sold") {
    events.push({
      id: "final",
      title: "Ready for Consumer",
      timestamp: new Date(),
      location: "Distribution Network",
      details: batch.finalProduct
        ? `${batch.finalProduct.productName} - ${batch.finalProduct.batchSize} units`
        : "Final product ready",
      icon: CheckCircle2,
      completed: true,
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-primary" />
          Supply Chain Journey
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {events.map((event, index) => {
            const Icon = event.icon
            const isLast = index === events.length - 1

            return (
              <div key={event.id} className="flex gap-4">
                {/* Timeline indicator */}
                <div className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      event.completed ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  {!isLast && <div className={`w-0.5 h-8 mt-2 ${event.completed ? "bg-primary" : "bg-border"}`} />}
                </div>

                {/* Event details */}
                <div className="flex-1 pb-8">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{event.title}</h4>
                    <Badge variant={event.completed ? "default" : "secondary"}>
                      {event.completed ? "Verified" : "Pending"}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{event.details}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {event.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {event.timestamp.toLocaleDateString()}{" "}
                      {event.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
