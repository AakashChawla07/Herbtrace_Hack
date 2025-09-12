"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { MapPin, Calendar, User, Package, Leaf, Shield, Clock, CheckCircle2, AlertTriangle, Share2 } from "lucide-react"
import Link from "next/link"
import { HerbTraceDB } from "@/lib/database"
import type { HerbBatch } from "@/lib/types"
import { TraceabilityTimeline } from "@/components/traceability-timeline"
import { SustainabilityScore } from "@/components/sustainability-score"
import { LocationMap } from "@/components/location-map"
import { BlockchainStatus } from "@/components/blockchain-status"

interface VerifyProductPageProps {
  params: {
    batchId: string
  }
}

export default function VerifyProductPage({ params }: VerifyProductPageProps) {
  const [batch, setBatch] = useState<HerbBatch | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>("")

  useEffect(() => {
    const loadBatch = async () => {
      try {
        // Try to find by batch ID first
        let foundBatch = await HerbTraceDB.getBatchById(params.batchId)

        // If not found, try demo data
        if (!foundBatch && params.batchId === "batch-demo-001") {
          // Create demo batch for demonstration
          const demoSpecies = (await HerbTraceDB.getHerbSpecies())[0]
          const demoUsers = await HerbTraceDB.getUsers()

          const demoCollectionEvent = await HerbTraceDB.createCollectionEvent({
            batchId: "batch-demo-001",
            species: demoSpecies,
            collectorId: demoUsers[0].id,
            collectorName: demoUsers[0].name,
            location: {
              latitude: 10.8505,
              longitude: 76.2711,
              region: "Kerala, India",
              address: "Organic Farm, Wayanad District",
            },
            timestamp: new Date("2024-01-15T08:30:00Z"),
            quantity: 2.5,
            unit: "kg",
            qualityNotes: "Premium quality roots, harvested at optimal maturity",
            photos: [],
            weatherConditions: "Sunny, 28°C, Light breeze",
            harvestMethod: "hand-picked",
            verified: true,
            blockchainTxId: "demo-tx-id-001", // Added blockchainTxId for demo
          })

          const demoProcessingEvent = await HerbTraceDB.createProcessingEvent({
            batchId: "batch-demo-001",
            processorId: demoUsers[1].id,
            processorName: demoUsers[1].name,
            facilityLocation: {
              latitude: 28.6139,
              longitude: 77.209,
              region: "Delhi, India",
              address: "Ayur Processing Facility, Gurgaon",
            },
            timestamp: new Date("2024-01-18T14:20:00Z"),
            processType: "cleaning",
            inputQuantity: 2.5,
            outputQuantity: 2.3,
            qualityTests: [
              {
                id: "test-001",
                testType: "purity",
                result: "99.2% pure",
                passed: true,
                testDate: new Date("2024-01-18"),
                labName: "Ayur Quality Labs",
              },
            ],
            certifications: ["Organic Certified", "GMP Compliant"],
            verified: true,
          })

          foundBatch = await HerbTraceDB.createBatch({
            qrCode: `https://herbtrace.app/verify/batch-demo-001`,
            species: demoSpecies,
            currentStatus: "packaged",
            collectionEvent: demoCollectionEvent,
            processingEvents: [demoProcessingEvent],
            finalProduct: {
              productName: "Premium Turmeric Powder",
              manufacturer: "Ayur Processing Ltd",
              expiryDate: new Date("2025-01-18"),
              batchSize: 100,
            },
            sustainabilityScore: 85,
            traceabilityComplete: true,
          })
        }

        if (foundBatch) {
          setBatch(foundBatch)
        } else {
          setError("Product not found. Please check the batch ID and try again.")
        }
      } catch (err) {
        setError("Failed to load product information. Please try again.")
        console.error("Error loading batch:", err)
      } finally {
        setLoading(false)
      }
    }

    loadBatch()
  }, [params.batchId])

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Verified ${batch?.species.name} - HerbTrace`,
          text: `Check out this verified Ayurvedic product with complete traceability!`,
          url: window.location.href,
        })
      } catch (err) {
        console.log("Error sharing:", err)
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Clock className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading product information...</p>
        </div>
      </div>
    )
  }

  if (error || !batch) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b border-border bg-card/50 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <Link href="/" className="flex items-center gap-2">
              <Leaf className="h-6 w-6 text-primary" />
              <span className="font-semibold text-foreground">HerbTrace</span>
            </Link>
          </div>
        </header>
        <div className="container mx-auto max-w-md p-4 pt-20">
          <Card className="border-destructive/20 bg-destructive/5">
            <CardHeader className="text-center">
              <AlertTriangle className="h-16 w-16 text-destructive mx-auto mb-4" />
              <CardTitle className="text-destructive">Product Not Found</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button asChild className="w-full">
                <Link href="/verify">Try Another Product</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="font-semibold text-foreground">HerbTrace</span>
          </Link>
          <Button variant="outline" size="sm" onClick={handleShare} className="bg-transparent">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </header>

      <div className="container mx-auto max-w-2xl p-4 space-y-6">
        {/* Product Header */}
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="h-6 w-6 text-primary" />
                  <Badge variant="default" className="bg-primary">
                    Verified Authentic
                  </Badge>
                  {batch.collectionEvent.blockchainTxId && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      Blockchain Verified
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-2xl text-primary">
                  {batch.finalProduct?.productName || batch.species.name}
                </CardTitle>
                <CardDescription className="text-lg">
                  {batch.species.scientificName} • Batch #{batch.id.slice(-8)}
                </CardDescription>
              </div>
              <Leaf className="h-12 w-12 text-primary/60" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Status:</span>
                <Badge variant="secondary" className="ml-2">
                  {batch.currentStatus}
                </Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Category:</span>
                <span className="ml-2 capitalize">{batch.species.category}</span>
              </div>
              {batch.finalProduct && (
                <>
                  <div>
                    <span className="text-muted-foreground">Manufacturer:</span>
                    <span className="ml-2">{batch.finalProduct.manufacturer}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Expires:</span>
                    <span className="ml-2">{batch.finalProduct.expiryDate.toLocaleDateString()}</span>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Blockchain Status */}
        <BlockchainStatus batchId={batch.id} />

        {/* Sustainability Score */}
        <SustainabilityScore score={batch.sustainabilityScore} species={batch.species} />

        {/* Collection Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              Collection Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="text-muted-foreground">Collector:</span> {batch.collectionEvent.collectorName}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="text-muted-foreground">Harvested:</span>{" "}
                    {batch.collectionEvent.timestamp.toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="text-muted-foreground">Quantity:</span> {batch.collectionEvent.quantity}{" "}
                    {batch.collectionEvent.unit}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Leaf className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    <span className="text-muted-foreground">Method:</span>{" "}
                    <span className="capitalize">{batch.collectionEvent.harvestMethod}</span>
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-muted-foreground">Location:</span>
                  <p className="text-sm">{batch.collectionEvent.location.region}</p>
                  {batch.collectionEvent.location.address && (
                    <p className="text-xs text-muted-foreground">{batch.collectionEvent.location.address}</p>
                  )}
                </div>
                {batch.collectionEvent.weatherConditions && (
                  <div>
                    <span className="text-sm text-muted-foreground">Weather:</span>
                    <p className="text-sm">{batch.collectionEvent.weatherConditions}</p>
                  </div>
                )}
                {batch.collectionEvent.blockchainTxId && (
                  <div>
                    <span className="text-sm text-muted-foreground">Blockchain TX:</span>
                    <p className="text-xs font-mono bg-muted p-1 rounded mt-1 break-all">
                      {batch.collectionEvent.blockchainTxId}
                    </p>
                  </div>
                )}
              </div>
            </div>
            {batch.collectionEvent.qualityNotes && (
              <>
                <Separator />
                <div>
                  <span className="text-sm text-muted-foreground">Quality Notes:</span>
                  <p className="text-sm mt-1">{batch.collectionEvent.qualityNotes}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Location Map */}
        <LocationMap location={batch.collectionEvent.location} />

        {/* Traceability Timeline */}
        <TraceabilityTimeline batch={batch} />

        {/* Quality Tests */}
        {batch.processingEvents.some((event) => event.qualityTests && event.qualityTests.length > 0) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Quality Certifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              {batch.processingEvents.map((event) =>
                event.qualityTests?.map((test) => (
                  <div key={test.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg mb-2">
                    <div>
                      <div className="font-medium capitalize">{test.testType.replace("-", " ")} Test</div>
                      <div className="text-sm text-muted-foreground">
                        {test.labName} • {test.testDate.toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{test.result}</div>
                      <Badge variant={test.passed ? "default" : "destructive"} className="text-xs">
                        {test.passed ? "Passed" : "Failed"}
                      </Badge>
                    </div>
                  </div>
                )),
              )}
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <Button asChild variant="outline" className="flex-1 bg-transparent">
            <Link href="/verify">Verify Another Product</Link>
          </Button>
          <Button onClick={handleShare} variant="outline" className="bg-transparent">
            <Share2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
