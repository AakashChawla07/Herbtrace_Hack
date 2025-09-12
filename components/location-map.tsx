"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Location } from "@/lib/types"

interface LocationMapProps {
  location: Location
}

export function LocationMap({ location }: LocationMapProps) {
  const openInMaps = () => {
    const url = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`
    window.open(url, "_blank")
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5 text-primary" />
          Collection Location
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mock map placeholder */}
        <div className="relative h-48 bg-muted rounded-lg overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900 dark:to-green-800">
            <div className="text-center">
              <MapPin className="h-8 w-8 text-primary mx-auto mb-2" />
              <div className="text-sm font-medium">{location.region}</div>
              <div className="text-xs text-muted-foreground">
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </div>
            </div>
          </div>
          {/* Mock map pin */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-6 h-6 bg-primary rounded-full border-2 border-white shadow-lg animate-pulse" />
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-sm">
            <span className="text-muted-foreground">Region:</span> {location.region}
          </div>
          {location.address && (
            <div className="text-sm">
              <span className="text-muted-foreground">Address:</span> {location.address}
            </div>
          )}
          <div className="text-sm">
            <span className="text-muted-foreground">Coordinates:</span> {location.latitude.toFixed(6)},{" "}
            {location.longitude.toFixed(6)}
          </div>
          {location.altitude && (
            <div className="text-sm">
              <span className="text-muted-foreground">Altitude:</span> {location.altitude}m
            </div>
          )}
        </div>

        <Button onClick={openInMaps} variant="outline" className="w-full bg-transparent">
          <ExternalLink className="h-4 w-4 mr-2" />
          View in Google Maps
        </Button>
      </CardContent>
    </Card>
  )
}
