"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { MapPin, Navigation, AlertCircle, CheckCircle2 } from "lucide-react"
import type { Location } from "@/lib/types"

interface LocationPickerProps {
  onLocationChange: (location: Location | null) => void
  location: Location | null
}

export function LocationPicker({ onLocationChange, location }: LocationPickerProps) {
  const [isGettingLocation, setIsGettingLocation] = useState(false)
  const [locationError, setLocationError] = useState<string>("")
  const [manualLocation, setManualLocation] = useState({
    latitude: "",
    longitude: "",
    address: "",
  })

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by this browser.")
      return
    }

    setIsGettingLocation(true)
    setLocationError("")

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLocation: Location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          region: "Current Location", // In real app, would reverse geocode
          altitude: position.coords.altitude || undefined,
        }
        onLocationChange(newLocation)
        setIsGettingLocation(false)
      },
      (error) => {
        setLocationError("Unable to retrieve your location. Please enter manually.")
        setIsGettingLocation(false)
        console.error("Geolocation error:", error)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      },
    )
  }

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const lat = Number.parseFloat(manualLocation.latitude)
    const lng = Number.parseFloat(manualLocation.longitude)

    if (isNaN(lat) || isNaN(lng)) {
      setLocationError("Please enter valid coordinates.")
      return
    }

    const newLocation: Location = {
      latitude: lat,
      longitude: lng,
      address: manualLocation.address || undefined,
      region: manualLocation.address || "Manual Entry",
    }

    onLocationChange(newLocation)
    setLocationError("")
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5 text-primary" />
          Collection Location
        </CardTitle>
        <CardDescription>Precise location data is required for blockchain verification.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Location Status */}
        {location && (
          <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-primary" />
              <span className="font-medium">Location Captured</span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
            </div>
            {location.address && <div className="text-xs text-muted-foreground">{location.address}</div>}
          </div>
        )}

        {/* Error Display */}
        {locationError && (
          <div className="p-3 bg-destructive/10 rounded-lg border border-destructive/20">
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span>{locationError}</span>
            </div>
          </div>
        )}

        {/* Auto Location Button */}
        <Button
          type="button"
          onClick={getCurrentLocation}
          disabled={isGettingLocation}
          className="w-full"
          variant={location ? "outline" : "default"}
        >
          {isGettingLocation ? (
            <>
              <Navigation className="h-4 w-4 mr-2 animate-spin" />
              Getting Location...
            </>
          ) : (
            <>
              <Navigation className="h-4 w-4 mr-2" />
              {location ? "Update Location" : "Get Current Location"}
            </>
          )}
        </Button>

        {/* Manual Location Entry */}
        <div className="border-t pt-4">
          <Label className="text-sm font-medium mb-3 block">Or Enter Manually</Label>
          <form onSubmit={handleManualSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="lat" className="text-xs">
                  Latitude
                </Label>
                <Input
                  id="lat"
                  type="number"
                  step="any"
                  value={manualLocation.latitude}
                  onChange={(e) => setManualLocation((prev) => ({ ...prev, latitude: e.target.value }))}
                  placeholder="0.000000"
                  className="text-sm"
                />
              </div>
              <div>
                <Label htmlFor="lng" className="text-xs">
                  Longitude
                </Label>
                <Input
                  id="lng"
                  type="number"
                  step="any"
                  value={manualLocation.longitude}
                  onChange={(e) => setManualLocation((prev) => ({ ...prev, longitude: e.target.value }))}
                  placeholder="0.000000"
                  className="text-sm"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="address" className="text-xs">
                Address (Optional)
              </Label>
              <Input
                id="address"
                value={manualLocation.address}
                onChange={(e) => setManualLocation((prev) => ({ ...prev, address: e.target.value }))}
                placeholder="Farm address or landmark"
                className="text-sm"
              />
            </div>
            <Button type="submit" variant="outline" size="sm" className="w-full bg-transparent">
              Set Manual Location
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}
