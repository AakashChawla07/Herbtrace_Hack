export interface HerbSpecies {
  id: string
  name: string
  scientificName: string
  category: "root" | "leaf" | "flower" | "seed" | "bark" | "fruit"
  harvestSeason: string[]
  sustainabilityStatus: "abundant" | "moderate" | "vulnerable" | "endangered"
}

export interface Location {
  latitude: number
  longitude: number
  address?: string
  region: string
  altitude?: number
}

export interface CollectionEvent {
  id: string
  batchId: string
  species: HerbSpecies
  collectorId: string
  collectorName: string
  location: Location
  timestamp: Date
  quantity: number
  unit: "kg" | "grams" | "bundles"
  qualityNotes?: string
  photos: string[]
  weatherConditions?: string
  harvestMethod: "hand-picked" | "tool-assisted" | "mechanical"
  blockchainTxId?: string
  verified: boolean
}

export interface ProcessingEvent {
  id: string
  batchId: string
  processorId: string
  processorName: string
  facilityLocation: Location
  timestamp: Date
  processType: "cleaning" | "drying" | "grinding" | "extraction" | "packaging"
  inputQuantity: number
  outputQuantity: number
  qualityTests?: QualityTest[]
  certifications: string[]
  blockchainTxId?: string
  verified: boolean
}

export interface QualityTest {
  id: string
  testType: "purity" | "potency" | "contamination" | "moisture" | "heavy-metals"
  result: string
  passed: boolean
  testDate: Date
  labName: string
  certificateUrl?: string
}

export interface HerbBatch {
  id: string
  qrCode: string
  species: HerbSpecies
  currentStatus: "collected" | "processing" | "tested" | "packaged" | "distributed" | "sold"
  collectionEvent: CollectionEvent
  processingEvents: ProcessingEvent[]
  finalProduct?: {
    productName: string
    manufacturer: string
    expiryDate: Date
    batchSize: number
  }
  sustainabilityScore: number
  traceabilityComplete: boolean
  createdAt: Date
  updatedAt: Date
}

export interface User {
  id: string
  name: string
  email: string
  role: "collector" | "processor" | "admin" | "consumer"
  organization?: string
  location?: Location
  certifications: string[]
  verified: boolean
  createdAt: Date
}

export interface BlockchainTransaction {
  id: string
  txHash: string
  eventType: "collection" | "processing" | "quality-test" | "transfer"
  batchId: string
  userId: string
  timestamp: Date
  data: Record<string, any>
  gasUsed?: number
  confirmed: boolean
}
