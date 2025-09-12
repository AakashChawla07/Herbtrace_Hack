"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { QrCode, Search, Leaf, AlertCircle } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function VerifyPage() {
  const [qrInput, setQrInput] = useState("")
  const [isScanning, setIsScanning] = useState(false)
  const router = useRouter()

  const handleQRSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!qrInput.trim()) return

    // Extract batch ID from QR code URL or use direct input
    let batchId = qrInput.trim()
    if (qrInput.includes("/verify/")) {
      batchId = qrInput.split("/verify/")[1]
    }

    router.push(`/verify/${batchId}`)
  }

  const handleScanQR = () => {
    setIsScanning(true)
    // In a real implementation, this would open camera for QR scanning
    // For MVP, we'll simulate with a timeout
    setTimeout(() => {
      setIsScanning(false)
      // Simulate successful scan with a demo batch ID
      router.push("/verify/batch-demo-001")
    }, 2000)
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
          <div className="flex items-center gap-2">
            <QrCode className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">Verify Product</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto max-w-md p-4 space-y-6">
        {/* Hero Section */}
        <div className="text-center py-8">
          <QrCode className="h-16 w-16 text-primary mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-foreground mb-2">Verify Your Product</h1>
          <p className="text-muted-foreground text-balance">
            Scan the QR code on your Ayurvedic product to view its complete journey from farm to your hands.
          </p>
        </div>

        {/* QR Scanner */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <QrCode className="h-5 w-5 text-primary" />
              Scan QR Code
            </CardTitle>
            <CardDescription>Use your camera to scan the QR code on the product packaging.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleScanQR} disabled={isScanning} className="w-full" size="lg">
              {isScanning ? (
                <>
                  <QrCode className="h-5 w-5 mr-2 animate-pulse" />
                  Scanning...
                </>
              ) : (
                <>
                  <QrCode className="h-5 w-5 mr-2" />
                  Open Camera Scanner
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Manual Entry */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              Manual Entry
            </CardTitle>
            <CardDescription>Enter the batch ID or QR code URL manually if scanning doesn't work.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleQRSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="qr-input">Batch ID or QR Code URL</Label>
                <Input
                  id="qr-input"
                  value={qrInput}
                  onChange={(e) => setQrInput(e.target.value)}
                  placeholder="batch-123456 or https://herbtrace.app/verify/batch-123456"
                />
              </div>
              <Button type="submit" variant="outline" className="w-full bg-transparent">
                <Search className="h-4 w-4 mr-2" />
                Verify Product
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Demo Section */}
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-primary">Try Demo</CardTitle>
            <CardDescription>Experience the verification process with our sample product.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/verify/batch-demo-001">View Demo Product</Link>
            </Button>
          </CardContent>
        </Card>

        {/* Info Section */}
        <div className="text-center text-sm text-muted-foreground space-y-2">
          <div className="flex items-center justify-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span>Look for the HerbTrace QR code on authentic products</span>
          </div>
          <p>Products without QR codes may not be verified through our system.</p>
        </div>
      </div>
    </div>
  )
}
