"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"
import {
  Activity,
  Users,
  Package,
  TrendingUp,
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Leaf,
  BarChart3,
  Download,
} from "lucide-react"
import Link from "next/link"
import { HerbTraceDB } from "@/lib/database"
import type { HerbBatch, CollectionEvent, User } from "@/lib/types"
import { BlockchainStatus } from "@/components/blockchain-status"

interface DashboardStats {
  totalBatches: number
  totalCollections: number
  totalProcessingEvents: number
  totalUsers: number
  verifiedBatches: number
  sustainabilityAverage: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalBatches: 0,
    totalCollections: 0,
    totalProcessingEvents: 0,
    totalUsers: 0,
    verifiedBatches: 0,
    sustainabilityAverage: 0,
  })
  const [batches, setBatches] = useState<HerbBatch[]>([])
  const [collections, setCollections] = useState<CollectionEvent[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [batchesData, collectionsData, usersData] = await Promise.all([
          HerbTraceDB.getAllBatches(),
          HerbTraceDB.getCollectionEvents(),
          HerbTraceDB.getUsers(),
        ])

        setBatches(batchesData)
        setCollections(collectionsData)
        setUsers(usersData)

        // Calculate stats
        const verifiedCount = batchesData.filter((batch) => batch.traceabilityComplete).length
        const avgSustainability =
          batchesData.reduce((sum, batch) => sum + batch.sustainabilityScore, 0) / batchesData.length || 0

        setStats({
          totalBatches: batchesData.length,
          totalCollections: collectionsData.length,
          totalProcessingEvents: batchesData.reduce((sum, batch) => sum + batch.processingEvents.length, 0),
          totalUsers: usersData.length,
          verifiedBatches: verifiedCount,
          sustainabilityAverage: Math.round(avgSustainability),
        })
      } catch (error) {
        console.error("Error loading dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  // Mock data for charts
  const collectionVolumeData = [
    { month: "Jan", volume: 45 },
    { month: "Feb", volume: 52 },
    { month: "Mar", volume: 48 },
    { month: "Apr", volume: 61 },
    { month: "May", volume: 55 },
    { month: "Jun", volume: 67 },
  ]

  const speciesDistribution = [
    { name: "Turmeric", value: 35, color: "#d97706" },
    { name: "Ashwagandha", value: 25, color: "#f97316" },
    { name: "Neem", value: 20, color: "#65a30d" },
    { name: "Others", value: 20, color: "#6b7280" },
  ]

  const sustainabilityTrend = [
    { month: "Jan", score: 78 },
    { month: "Feb", score: 82 },
    { month: "Mar", score: 79 },
    { month: "Apr", score: 85 },
    { month: "May", score: 83 },
    { month: "Jun", score: 87 },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-pulse text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
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
          <div className="flex items-center gap-4">
            <Badge variant="outline">Admin Dashboard</Badge>
            <Button variant="outline" size="sm" className="bg-transparent">
              <Download className="h-4 w-4 mr-2" />
              Export Data
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto p-4 space-y-6">
        {/* Page Title */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">System Dashboard</h1>
            <p className="text-muted-foreground">Monitor and manage your HerbTrace network</p>
          </div>
          <div className="flex gap-2">
            <Button asChild>
              <Link href="/collect">Add Collection</Link>
            </Button>
          </div>
        </div>

        <BlockchainStatus showNetworkStats={true} />

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Batches</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalBatches}</div>
              <p className="text-xs text-muted-foreground">
                {stats.verifiedBatches} verified ({Math.round((stats.verifiedBatches / stats.totalBatches) * 100)}%)
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Collection Events</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalCollections}</div>
              <p className="text-xs text-muted-foreground">Across all regions</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground">Collectors and processors</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Sustainability</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.sustainabilityAverage}/100</div>
              <p className="text-xs text-muted-foreground">
                {stats.sustainabilityAverage >= 80 ? "Excellent" : stats.sustainabilityAverage >= 60 ? "Good" : "Fair"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="batches">Batches</TabsTrigger>
            <TabsTrigger value="collections">Collections</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Collection Volume Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Collection Volume Trend
                  </CardTitle>
                  <CardDescription>Monthly collection volumes (kg)</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={collectionVolumeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="volume" fill="hsl(var(--primary))" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Species Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Leaf className="h-5 w-5 text-primary" />
                    Species Distribution
                  </CardTitle>
                  <CardDescription>Breakdown by herb species</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={speciesDistribution}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {speciesDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Sustainability Trend */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Sustainability Score Trend
                  </CardTitle>
                  <CardDescription>Average sustainability scores over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={sustainabilityTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Batches Tab */}
          <TabsContent value="batches" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Batches</CardTitle>
                <CardDescription>Latest herb batches in the system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {batches.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No batches found. Start by recording a collection event.</p>
                      <Button asChild className="mt-4">
                        <Link href="/collect">Record Collection</Link>
                      </Button>
                    </div>
                  ) : (
                    batches.map((batch) => (
                      <div key={batch.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium">{batch.species.name}</h4>
                            <Badge variant={batch.traceabilityComplete ? "default" : "secondary"}>
                              {batch.currentStatus}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Batch #{batch.id.slice(-8)} • Collected by {batch.collectionEvent.collectorName}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {batch.collectionEvent.timestamp.toLocaleDateString()} •{" "}
                            {batch.collectionEvent.location.region}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">Sustainability: {batch.sustainabilityScore}/100</div>
                          <div className="flex items-center gap-2 mt-1">
                            {batch.traceabilityComplete ? (
                              <CheckCircle2 className="h-4 w-4 text-green-500" />
                            ) : (
                              <Clock className="h-4 w-4 text-yellow-500" />
                            )}
                            <Button variant="outline" size="sm" asChild className="bg-transparent">
                              <Link href={`/verify/${batch.id}`}>View Details</Link>
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Collections Tab */}
          <TabsContent value="collections" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Collection Events</CardTitle>
                <CardDescription>Recent herb collection activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {collections.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <MapPin className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No collection events recorded yet.</p>
                    </div>
                  ) : (
                    collections.map((collection) => (
                      <div key={collection.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium">{collection.species.name}</h4>
                            <Badge variant={collection.verified ? "default" : "secondary"}>
                              {collection.verified ? "Verified" : "Pending"}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {collection.quantity} {collection.unit} • {collection.collectorName}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {collection.timestamp.toLocaleDateString()} • {collection.location.region}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium capitalize">{collection.harvestMethod}</div>
                          <div className="flex items-center gap-2 mt-1">
                            {collection.verified ? (
                              <CheckCircle2 className="h-4 w-4 text-green-500" />
                            ) : (
                              <AlertTriangle className="h-4 w-4 text-yellow-500" />
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>System Users</CardTitle>
                <CardDescription>Collectors, processors, and administrators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{user.name}</h4>
                          <Badge variant={user.verified ? "default" : "secondary"}>{user.role}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                        {user.organization && <p className="text-xs text-muted-foreground">{user.organization}</p>}
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{user.location?.region || "Location not set"}</div>
                        <div className="flex items-center gap-2 mt-1">
                          {user.verified ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          )}
                          <span className="text-xs text-muted-foreground">
                            {user.certifications.length} cert{user.certifications.length !== 1 ? "s" : ""}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
