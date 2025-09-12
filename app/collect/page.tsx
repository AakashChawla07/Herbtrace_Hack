"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import {
  MapPin,
  Camera,
  Leaf,
  Clock,
  User,
  Package,
  AlertCircle,
  CheckCircle2,
  Shield,
  QrCode,
  Download,
} from "lucide-react"
import Link from "next/link"
import { HerbTraceDB } from "@/lib/database"
import { generateBatchQRCode, calculateSustainabilityScore } from "@/lib/qr-generator"
import { useBlockchainTransaction } from "@/lib/blockchain"
import type { HerbSpecies, CollectionEvent, Location } from "@/lib/types"

export default function CollectPage() {
  const [species, setSpecies] = useState<HerbSpecies[]>([])
  const [selectedSpecies, setSelectedSpecies] = useState<HerbSpecies | null>(null)
  const [location, setLocation] = useState<Location | null>(null)
  const [locationError, setLocationError] = useState<string>("")
  const [showManualLocation, setShowManualLocation] = useState(false)
  const [manualLocation, setManualLocation] = useState({ latitude: "", longitude: "", region: "" })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [blockchainTx, setBlockchainTx] = useState<string>("")
  const [generatedQRCode, setGeneratedQRCode] = useState<string>("")
  const [batchId, setBatchId] = useState<string>("")
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [formData, setFormData] = useState({
    collectorName: "",
    quantity: "",
    unit: "kg" as const,
    harvestMethod: "hand-picked" as const,
    qualityNotes: "",
    weatherConditions: "",
  })

  const { recordCollection } = useBlockchainTransaction()

  useEffect(() => {
    HerbTraceDB.getHerbSpecies().then(setSpecies)

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            region: "Location detected",
            altitude: position.coords.altitude || undefined,
          })
        },
        (error) => {
          console.log("[v0] Geolocation error:", error.message)
          setLocationError("Location access denied. You can enter coordinates manually below.")
          setShowManualLocation(true)
        },
      )
    } else {
      setLocationError("Geolocation not supported. Please enter coordinates manually.")
      setShowManualLocation(true)
    }
  }, [])

  const handleManualLocation = () => {
    if (manualLocation.latitude && manualLocation.longitude) {
      setLocation({
        latitude: Number.parseFloat(manualLocation.latitude),
        longitude: Number.parseFloat(manualLocation.longitude),
        region: manualLocation.region || "Manual entry",
      })
      setLocationError("")
      setShowManualLocation(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedSpecies || !location || !formData.collectorName || !formData.quantity) {
      return
    }

    setIsSubmitting(true)
    setValidationErrors([])

    try {
      const newBatchId = `HT-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      setBatchId(newBatchId)

      const collectionEvent: Omit<CollectionEvent, "id"> = {
        batchId: newBatchId,
        species: selectedSpecies,
        collectorId: `collector-${Date.now()}`,
        collectorName: formData.collectorName,
        location,
        timestamp: new Date(),
        quantity: Number.parseFloat(formData.quantity),
        unit: formData.unit,
        qualityNotes: formData.qualityNotes,
        photos: [],
        weatherConditions: formData.weatherConditions,
        harvestMethod: formData.harvestMethod,
        verified: false,
      }

      const blockchainTransaction = await recordCollection(collectionEvent)

      const savedEvent = await HerbTraceDB.createCollectionEvent({
        ...collectionEvent,
        blockchainTxId: blockchainTransaction.txHash,
        verified: true,
      })

      const qrCode = generateBatchQRCode(newBatchId)
      setGeneratedQRCode(qrCode)

      await HerbTraceDB.createBatch({
        qrCode,
        species: selectedSpecies,
        currentStatus: "collected",
        collectionEvent: savedEvent,
        processingEvents: [],
        sustainabilityScore: calculateSustainabilityScore(selectedSpecies, formData.harvestMethod, location),
        traceabilityComplete: false,
      })

      setBlockchainTx(blockchainTransaction.txHash)
      setSubmitSuccess(true)

      setFormData({
        collectorName: "",
        quantity: "",
        unit: "kg",
        harvestMethod: "hand-picked",
        qualityNotes: "",
        weatherConditions: "",
      })
      setSelectedSpecies(null)
    } catch (error) {
      console.error("Error submitting collection:", error)
      if (error instanceof Error && error.message.includes("Validation failed")) {
        const errors = error.message.replace("Validation failed: ", "").split(", ")
        setValidationErrors(errors)
      } else {
        setValidationErrors(["Failed to record collection. Please try again."])
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const downloadQRCode = () => {
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = 200
    canvas.height = 200
    ctx.fillStyle = "#ffffff"
    ctx.fillRect(0, 0, 200, 200)
    ctx.fillStyle = "#000000"
    ctx.font = "12px monospace"
    ctx.textAlign = "center"
    ctx.fillText(batchId, 100, 100)

    const link = document.createElement("a")
    link.download = `herbtrace-qr-${batchId}.png`
    link.href = canvas.toDataURL()
    link.click()
  }

  if (submitSuccess) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="container mx-auto max-w-md">
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader className="text-center">
              <CheckCircle2 className="h-16 w-16 text-primary mx-auto mb-4" />
              <CardTitle className="text-primary">Collection Recorded!</CardTitle>
              <CardDescription>Your herb collection has been successfully recorded on the blockchain.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <Badge variant="secondary" className="mb-2">
                  Batch ID: {batchId}
                </Badge>
                <div className="bg-white p-4 rounded-lg border-2 border-primary/20 mb-4">
                  <div className="flex items-center justify-center mb-2">
                    <QrCode className="h-6 w-6 text-primary mr-2" />
                    <span className="font-semibold">Product QR Code</span>
                  </div>
                  <div className="bg-gray-100 p-4 rounded border-2 border-dashed border-gray-300 mb-2">
                    <div className="text-center text-xs font-mono break-all bg-white p-2 rounded">
                      {generatedQRCode}
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={downloadQRCode} className="w-full bg-transparent">
                    <Download className="h-4 w-4 mr-2" />
                    Download QR Code
                  </Button>
                </div>
                {blockchainTx && (
                  <div className="text-xs text-muted-foreground">
                    <div className="flex items-center justify-center gap-1 mb-2">
                      <Shield className="h-3 w-3" />
                      <span>Blockchain Verified</span>
                    </div>
                    <div className="font-mono bg-muted p-2 rounded text-xs break-all">TX: {blockchainTx}</div>
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    setSubmitSuccess(false)
                    setGeneratedQRCode("")
                    setBatchId("")
                  }}
                  className="flex-1"
                >
                  Record Another
                </Button>
                <Button variant="outline" asChild className="flex-1 bg-transparent">
                  <Link href="/dashboard">View Dashboard</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="font-semibold text-foreground">HerbTrace</span>
          </Link>
          <Badge variant="outline">Collection Mode</Badge>
        </div>
      </header>

      <div className="container mx-auto max-w-md p-4 space-y-6">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Location Status</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {location ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>
                  GPS coordinates captured ({location.latitude.toFixed(4)}, {location.longitude.toFixed(4)})
                </span>
              </div>
            ) : locationError ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span>{locationError}</span>
                </div>
                {showManualLocation && (
                  <div className="space-y-3 p-3 bg-muted/50 rounded-lg">
                    <Label className="text-sm font-medium">Enter Location Manually:</Label>
                    <div className="grid grid-cols-2 gap-2">
                      <Input
                        placeholder="Latitude"
                        value={manualLocation.latitude}
                        onChange={(e) => setManualLocation((prev) => ({ ...prev, latitude: e.target.value }))}
                        type="number"
                        step="any"
                      />
                      <Input
                        placeholder="Longitude"
                        value={manualLocation.longitude}
                        onChange={(e) => setManualLocation((prev) => ({ ...prev, longitude: e.target.value }))}
                        type="number"
                        step="any"
                      />
                    </div>
                    <Input
                      placeholder="Region/Area (optional)"
                      value={manualLocation.region}
                      onChange={(e) => setManualLocation((prev) => ({ ...prev, region: e.target.value }))}
                    />
                    <Button
                      onClick={handleManualLocation}
                      size="sm"
                      disabled={!manualLocation.latitude || !manualLocation.longitude}
                    >
                      Set Location
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4 animate-spin" />
                <span>Getting location...</span>
              </div>
            )}
          </CardContent>
        </Card>

        {validationErrors.length > 0 && (
          <Card className="border-destructive/20 bg-destructive/5">
            <CardHeader>
              <CardTitle className="text-destructive flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Validation Errors
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index} className="text-sm text-destructive flex items-start gap-2">
                    <span className="text-destructive">•</span>
                    <span>{error}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Leaf className="h-5 w-5 text-primary" />
              Record Collection
            </CardTitle>
            <CardDescription>
              Document your herb collection with precise details for blockchain verification.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="collector" className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Collector Name
                </Label>
                <Input
                  id="collector"
                  value={formData.collectorName}
                  onChange={(e) => setFormData((prev) => ({ ...prev, collectorName: e.target.value }))}
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Leaf className="h-4 w-4" />
                  Herb Species
                </Label>
                <Select
                  onValueChange={(value) => {
                    const speciesData = species.find((s) => s.id === value)
                    setSelectedSpecies(speciesData || null)
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select herb species" />
                  </SelectTrigger>
                  <SelectContent>
                    {species.map((herb) => (
                      <SelectItem key={herb.id} value={herb.id}>
                        <div className="flex flex-col">
                          <span>{herb.name}</span>
                          <span className="text-xs text-muted-foreground">{herb.scientificName}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedSpecies && (
                  <div className="flex gap-2 mt-2">
                    <Badge variant="secondary">{selectedSpecies.category}</Badge>
                    <Badge variant={selectedSpecies.sustainabilityStatus === "abundant" ? "default" : "destructive"}>
                      {selectedSpecies.sustainabilityStatus}
                    </Badge>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label htmlFor="quantity" className="flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Quantity
                  </Label>
                  <Input
                    id="quantity"
                    type="number"
                    step="0.1"
                    value={formData.quantity}
                    onChange={(e) => setFormData((prev) => ({ ...prev, quantity: e.target.value }))}
                    placeholder="0.0"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Unit</Label>
                  <Select
                    value={formData.unit}
                    onValueChange={(value: "kg" | "grams" | "bundles") =>
                      setFormData((prev) => ({ ...prev, unit: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="kg">Kilograms</SelectItem>
                      <SelectItem value="grams">Grams</SelectItem>
                      <SelectItem value="bundles">Bundles</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Harvest Method</Label>
                <Select
                  value={formData.harvestMethod}
                  onValueChange={(value: "hand-picked" | "tool-assisted" | "mechanical") =>
                    setFormData((prev) => ({ ...prev, harvestMethod: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hand-picked">Hand-picked</SelectItem>
                    <SelectItem value="tool-assisted">Tool-assisted</SelectItem>
                    <SelectItem value="mechanical">Mechanical</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="weather">Weather Conditions</Label>
                <Input
                  id="weather"
                  value={formData.weatherConditions}
                  onChange={(e) => setFormData((prev) => ({ ...prev, weatherConditions: e.target.value }))}
                  placeholder="e.g., Sunny, 25°C, Light breeze"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Quality Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.qualityNotes}
                  onChange={(e) => setFormData((prev) => ({ ...prev, qualityNotes: e.target.value }))}
                  placeholder="Any observations about herb quality, maturity, etc."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Camera className="h-4 w-4" />
                  Photos (Optional)
                </Label>
                <Button type="button" variant="outline" className="w-full bg-transparent" disabled>
                  <Camera className="h-4 w-4 mr-2" />
                  Capture Photos (Coming Soon)
                </Button>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={
                  !selectedSpecies || !location || !formData.collectorName || !formData.quantity || isSubmitting
                }
              >
                {isSubmitting ? (
                  <>
                    <Shield className="h-4 w-4 mr-2 animate-spin" />
                    Recording on Blockchain...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Record Collection
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
