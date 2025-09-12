import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, Leaf, Award } from "lucide-react"
import type { HerbSpecies } from "@/lib/types"

interface SustainabilityScoreProps {
  score: number
  species: HerbSpecies
}

export function SustainabilityScore({ score, species }: SustainabilityScoreProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent"
    if (score >= 60) return "Good"
    if (score >= 40) return "Fair"
    return "Needs Improvement"
  }

  const getSustainabilityBadge = (status: string) => {
    switch (status) {
      case "abundant":
        return (
          <Badge variant="default" className="bg-green-500">
            Abundant
          </Badge>
        )
      case "moderate":
        return <Badge variant="secondary">Moderate</Badge>
      case "vulnerable":
        return (
          <Badge variant="destructive" className="bg-yellow-500">
            Vulnerable
          </Badge>
        )
      case "endangered":
        return <Badge variant="destructive">Endangered</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary" />
          Sustainability Score
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className={`text-3xl font-bold ${getScoreColor(score)}`}>{score}/100</div>
            <div className="text-sm text-muted-foreground">{getScoreLabel(score)}</div>
          </div>
          <Award className={`h-12 w-12 ${getScoreColor(score)}`} />
        </div>

        <Progress value={score} className="h-2" />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Species Status:</span>
              {getSustainabilityBadge(species.sustainabilityStatus)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Harvest Season:</span>
              <span>{species.harvestSeason.join(", ")}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Leaf className="h-4 w-4 text-green-500" />
              <span className="text-sm">Sustainably harvested</span>
            </div>
            <div className="flex items-center gap-2">
              <Award className="h-4 w-4 text-primary" />
              <span className="text-sm">Quality verified</span>
            </div>
          </div>
        </div>

        <div className="text-xs text-muted-foreground">
          <p>
            Sustainability score is calculated based on species conservation status, harvest methods, seasonal timing,
            and regional growing conditions.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
