import type { HerbBatch, CollectionEvent, ProcessingEvent, HerbSpecies, User } from "./types"

// Mock data for development
const mockHerbSpecies: HerbSpecies[] = [
  {
    id: "turmeric-001",
    name: "Turmeric",
    scientificName: "Curcuma longa",
    category: "root",
    harvestSeason: ["October", "November", "December"],
    sustainabilityStatus: "abundant",
  },
  {
    id: "ashwagandha-001",
    name: "Ashwagandha",
    scientificName: "Withania somnifera",
    category: "root",
    harvestSeason: ["January", "February", "March"],
    sustainabilityStatus: "moderate",
  },
  {
    id: "neem-001",
    name: "Neem",
    scientificName: "Azadirachta indica",
    category: "leaf",
    harvestSeason: ["March", "April", "May"],
    sustainabilityStatus: "abundant",
  },
]

const mockUsers: User[] = [
  {
    id: "user-001",
    name: "Rajesh Kumar",
    email: "rajesh@herbtrace.com",
    role: "collector",
    organization: "Kerala Herb Collective",
    location: { latitude: 10.8505, longitude: 76.2711, region: "Kerala, India" },
    certifications: ["Organic Farming Certificate"],
    verified: true,
    createdAt: new Date("2024-01-15"),
  },
  {
    id: "user-002",
    name: "Priya Sharma",
    email: "priya@ayurprocessing.com",
    role: "processor",
    organization: "Ayur Processing Ltd",
    location: { latitude: 28.6139, longitude: 77.209, region: "Delhi, India" },
    certifications: ["GMP Certificate", "ISO 9001"],
    verified: true,
    createdAt: new Date("2024-01-20"),
  },
]

// Mock database operations
export class HerbTraceDB {
  private static batches: HerbBatch[] = []
  private static collectionEvents: CollectionEvent[] = []
  private static processingEvents: ProcessingEvent[] = []

  static async getHerbSpecies(): Promise<HerbSpecies[]> {
    return mockHerbSpecies
  }

  static async getUsers(): Promise<User[]> {
    return mockUsers
  }

  static async createCollectionEvent(event: Omit<CollectionEvent, "id">): Promise<CollectionEvent> {
    const newEvent: CollectionEvent = {
      ...event,
      id: `collection-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    }
    this.collectionEvents.push(newEvent)
    return newEvent
  }

  static async createProcessingEvent(event: Omit<ProcessingEvent, "id">): Promise<ProcessingEvent> {
    const newEvent: ProcessingEvent = {
      ...event,
      id: `processing-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    }
    this.processingEvents.push(newEvent)
    return newEvent
  }

  static async createBatch(batch: Omit<HerbBatch, "id" | "createdAt" | "updatedAt">): Promise<HerbBatch> {
    const newBatch: HerbBatch = {
      ...batch,
      id: `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    this.batches.push(newBatch)
    return newBatch
  }

  static async getBatchById(id: string): Promise<HerbBatch | null> {
    return this.batches.find((batch) => batch.id === id) || null
  }

  static async getBatchByQRCode(qrCode: string): Promise<HerbBatch | null> {
    return this.batches.find((batch) => batch.qrCode === qrCode) || null
  }

  static async getAllBatches(): Promise<HerbBatch[]> {
    return this.batches
  }

  static async getCollectionEvents(): Promise<CollectionEvent[]> {
    return this.collectionEvents
  }

  static async getProcessingEvents(): Promise<ProcessingEvent[]> {
    return this.processingEvents
  }

  static async updateBatchStatus(batchId: string, status: HerbBatch["currentStatus"]): Promise<void> {
    const batch = this.batches.find((b) => b.id === batchId)
    if (batch) {
      batch.currentStatus = status
      batch.updatedAt = new Date()
    }
  }
}
