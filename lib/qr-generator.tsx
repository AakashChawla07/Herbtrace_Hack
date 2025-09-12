export function generateBatchQRCode(batchId: string): string {
  // In a real implementation, this would generate an actual QR code
  // For MVP, we'll return a mock QR code URL
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "https://herbtrace.vercel.app"
  return `${baseUrl}/verify/${batchId}`
}

export function generateQRCodeSVG(data: string): string {
  // Mock QR code SVG for development
  // In production, this would use a proper QR code library
  return `data:image/svg+xml;base64,${btoa(`
    <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <rect width="200" height="200" fill="white"/>
      <rect x="20" y="20" width="160" height="160" fill="black"/>
      <rect x="40" y="40" width="120" height="120" fill="white"/>
      <text x="100" y="105" text-anchor="middle" font-family="monospace" font-size="8" fill="black">
        QR: ${data.slice(-8)}
      </text>
    </svg>
  `)}`
}

export function calculateSustainabilityScore(
  species: { sustainabilityStatus: string },
  harvestMethod: string,
  location: { region: string },
): number {
  let score = 50 // Base score

  // Species sustainability impact
  switch (species.sustainabilityStatus) {
    case "abundant":
      score += 30
      break
    case "moderate":
      score += 15
      break
    case "vulnerable":
      score -= 10
      break
    case "endangered":
      score -= 30
      break
  }

  // Harvest method impact
  switch (harvestMethod) {
    case "hand-picked":
      score += 20
      break
    case "tool-assisted":
      score += 10
      break
    case "mechanical":
      score -= 5
      break
  }

  // Regional bonus for traditional growing areas
  if (location.region.includes("Kerala") || location.region.includes("Karnataka")) {
    score += 10
  }

  return Math.max(0, Math.min(100, score))
}
