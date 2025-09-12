"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Shield, Activity, Clock, CheckCircle2, Zap } from "lucide-react"
import { HerbTraceBlockchain } from "@/lib/blockchain"

interface BlockchainStatusProps {
  batchId?: string
  showNetworkStats?: boolean
}

export function BlockchainStatus({ batchId, showNetworkStats = false }: BlockchainStatusProps) {
  const [networkStats, setNetworkStats] = useState<{
    totalTransactions: number
    totalBatches: number
    averageGasUsed: number
    networkHealth: "healthy" | "congested" | "offline"
  } | null>(null)
  const [batchTransactions, setBatchTransactions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        if (showNetworkStats) {
          const stats = await HerbTraceBlockchain.getNetworkStats()
          setNetworkStats(stats)
        }

        if (batchId) {
          const transactions = await HerbTraceBlockchain.getBatchTransactions(batchId)
          setBatchTransactions(transactions)
        }
      } catch (error) {
        console.error("Error loading blockchain data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [batchId, showNetworkStats])

  const getHealthColor = (health: string) => {
    switch (health) {
      case "healthy":
        return "text-green-500"
      case "congested":
        return "text-yellow-500"
      case "offline":
        return "text-red-500"
      default:
        return "text-muted-foreground"
    }
  }

  const getHealthBadge = (health: string) => {
    switch (health) {
      case "healthy":
        return <Badge className="bg-green-500">Healthy</Badge>
      case "congested":
        return <Badge className="bg-yellow-500">Congested</Badge>
      case "offline":
        return <Badge variant="destructive">Offline</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Activity className="h-6 w-6 animate-pulse text-primary" />
          <span className="ml-2 text-muted-foreground">Loading blockchain status...</span>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Network Status */}
      {showNetworkStats && networkStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Blockchain Network Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Network Health</span>
              {getHealthBadge(networkStats.networkHealth)}
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Total Transactions:</span>
                <span className="ml-2 font-medium">{networkStats.totalTransactions}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Tracked Batches:</span>
                <span className="ml-2 font-medium">{networkStats.totalBatches}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Avg Gas Used:</span>
                <span className="ml-2 font-medium">{networkStats.averageGasUsed.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Block Time:</span>
                <span className="ml-2 font-medium">~2s</span>
              </div>
            </div>

            <div className="pt-2">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Network Activity</span>
                <span className="text-sm text-muted-foreground">95% uptime</span>
              </div>
              <Progress value={95} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Batch Transactions */}
      {batchId && batchTransactions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Blockchain Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {batchTransactions.map((tx) => (
                <div key={tx.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="flex items-center gap-1">
                        {tx.confirmed ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <Clock className="h-4 w-4 text-yellow-500" />
                        )}
                        <span className="font-medium capitalize">{tx.eventType.replace("-", " ")}</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {tx.confirmed ? "Confirmed" : "Pending"}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      <div>
                        TX: {tx.txHash.slice(0, 10)}...{tx.txHash.slice(-8)}
                      </div>
                      <div>{tx.timestamp.toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="text-right text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Zap className="h-3 w-3" />
                      {tx.gasUsed?.toLocaleString()} gas
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Transactions */}
      {batchId && batchTransactions.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">No blockchain transactions found for this batch.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
