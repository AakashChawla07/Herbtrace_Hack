import type { CollectionEvent, ProcessingEvent, BlockchainTransaction } from "./types"

// Simulated blockchain network for MVP
class HerbTraceBlockchain {
  private static transactions: BlockchainTransaction[] = []
  private static networkDelay = 1000 // Simulate network delay

  // Simulate blockchain transaction creation
  static async recordCollectionEvent(event: CollectionEvent): Promise<BlockchainTransaction> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, this.networkDelay))

    const transaction: BlockchainTransaction = {
      id: `tx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      txHash: this.generateTxHash(),
      eventType: "collection",
      batchId: event.batchId,
      userId: event.collectorId,
      timestamp: new Date(),
      data: {
        species: event.species.name,
        location: event.location,
        quantity: event.quantity,
        unit: event.unit,
        harvestMethod: event.harvestMethod,
        qualityNotes: event.qualityNotes,
        weatherConditions: event.weatherConditions,
      },
      gasUsed: Math.floor(Math.random() * 50000) + 21000, // Simulate gas usage
      confirmed: true,
    }

    this.transactions.push(transaction)
    return transaction
  }

  static async recordProcessingEvent(event: ProcessingEvent): Promise<BlockchainTransaction> {
    await new Promise((resolve) => setTimeout(resolve, this.networkDelay))

    const transaction: BlockchainTransaction = {
      id: `tx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      txHash: this.generateTxHash(),
      eventType: "processing",
      batchId: event.batchId,
      userId: event.processorId,
      timestamp: new Date(),
      data: {
        processType: event.processType,
        facilityLocation: event.facilityLocation,
        inputQuantity: event.inputQuantity,
        outputQuantity: event.outputQuantity,
        qualityTests: event.qualityTests,
        certifications: event.certifications,
      },
      gasUsed: Math.floor(Math.random() * 75000) + 30000,
      confirmed: true,
    }

    this.transactions.push(transaction)
    return transaction
  }

  static async recordQualityTest(batchId: string, testData: any): Promise<BlockchainTransaction> {
    await new Promise((resolve) => setTimeout(resolve, this.networkDelay))

    const transaction: BlockchainTransaction = {
      id: `tx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      txHash: this.generateTxHash(),
      eventType: "quality-test",
      batchId,
      userId: "system",
      timestamp: new Date(),
      data: testData,
      gasUsed: Math.floor(Math.random() * 40000) + 25000,
      confirmed: true,
    }

    this.transactions.push(transaction)
    return transaction
  }

  static async recordTransfer(batchId: string, fromUserId: string, toUserId: string): Promise<BlockchainTransaction> {
    await new Promise((resolve) => setTimeout(resolve, this.networkDelay))

    const transaction: BlockchainTransaction = {
      id: `tx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      txHash: this.generateTxHash(),
      eventType: "transfer",
      batchId,
      userId: fromUserId,
      timestamp: new Date(),
      data: {
        fromUserId,
        toUserId,
        transferType: "custody-change",
      },
      gasUsed: Math.floor(Math.random() * 35000) + 20000,
      confirmed: true,
    }

    this.transactions.push(transaction)
    return transaction
  }

  // Get all transactions for a specific batch
  static async getBatchTransactions(batchId: string): Promise<BlockchainTransaction[]> {
    return this.transactions
      .filter((tx) => tx.batchId === batchId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  }

  // Get all transactions
  static async getAllTransactions(): Promise<BlockchainTransaction[]> {
    return [...this.transactions].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }

  // Verify transaction integrity
  static async verifyTransaction(txHash: string): Promise<boolean> {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const transaction = this.transactions.find((tx) => tx.txHash === txHash)
    return transaction ? transaction.confirmed : false
  }


  static getDistanceFromLatLonInKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // Distance in km
  }
  // Smart contract validation
  // Smart contract validation
static validateCollectionEvent(event: CollectionEvent): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // Basic validation rules...
  if (!event.species || !event.species.name) {
    errors.push("Species information is required")
  }
  if (!event.location || !event.location.latitude || !event.location.longitude) {
    errors.push("Valid GPS coordinates are required")
  }
  if (!event.quantity || event.quantity <= 0) {
    errors.push("Quantity must be greater than zero")
  }
  if (!event.collectorName || event.collectorName.trim().length === 0) {
    errors.push("Collector name is required")
  }

  // ✅ Geo-fencing check for Patiala
  const AUTH_LAT = 30.3507
  const AUTH_LON = 76.3595
  const MAX_RADIUS_KM = 10

  if (event.location) {
    const distance = HerbTraceBlockchain.getDistanceFromLatLonInKm(
      event.location.latitude,
      event.location.longitude,
      AUTH_LAT,
      AUTH_LON
    )
    if (distance > MAX_RADIUS_KM) {
      errors.push(`Collection location is outside authorized 10 km radius (distance: ${distance.toFixed(2)} km)`)
    }
  }

  // Seasonal + sustainability validations (your existing code)...

  return {
    valid: errors.length === 0,
    errors,
  }
}


  static validateProcessingEvent(event: ProcessingEvent): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!event.processType) {
      errors.push("Process type is required")
    }

    if (!event.inputQuantity || event.inputQuantity <= 0) {
      errors.push("Input quantity must be greater than zero")
    }

    if (!event.outputQuantity || event.outputQuantity <= 0) {
      errors.push("Output quantity must be greater than zero")
    }

    if (event.outputQuantity > event.inputQuantity) {
      errors.push("Output quantity cannot exceed input quantity")
    }

    // Processing efficiency check
    const efficiency = (event.outputQuantity / event.inputQuantity) * 100
    if (efficiency < 50) {
      errors.push("Processing efficiency is unusually low (< 50%)")
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  // Generate mock transaction hash
  private static generateTxHash(): string {
    const chars = "0123456789abcdef"
    let hash = "0x"
    for (let i = 0; i < 64; i++) {
      hash += chars[Math.floor(Math.random() * chars.length)]
    }
    return hash
  }

  // Get network statistics
  static async getNetworkStats(): Promise<{
    totalTransactions: number
    totalBatches: number
    averageGasUsed: number
    networkHealth: "healthy" | "congested" | "offline"
  }> {
    const totalTransactions = this.transactions.length
    const uniqueBatches = new Set(this.transactions.map((tx) => tx.batchId)).size
    const averageGasUsed =
      totalTransactions > 0 ? this.transactions.reduce((sum, tx) => sum + (tx.gasUsed || 0), 0) / totalTransactions : 0

    return {
      totalTransactions,
      totalBatches: uniqueBatches,
      averageGasUsed: Math.round(averageGasUsed),
      networkHealth: "healthy", // Simulated
    }
  }
}

export { HerbTraceBlockchain }

// Blockchain integration hooks for React components
export function useBlockchainTransaction() {
  const recordCollection = async (event: CollectionEvent) => {
    const validation = HerbTraceBlockchain.validateCollectionEvent(event)
    if (!validation.valid) {
      throw new Error(`Validation failed: ${validation.errors.join(", ")}`)
    }
    return await HerbTraceBlockchain.recordCollectionEvent(event)
  }

  const recordProcessing = async (event: ProcessingEvent) => {
    const validation = HerbTraceBlockchain.validateProcessingEvent(event)
    if (!validation.valid) {
      throw new Error(`Validation failed: ${validation.errors.join(", ")}`)
    }
    return await HerbTraceBlockchain.recordProcessingEvent(event)
  }

  const getBatchHistory = async (batchId: string) => {
    return await HerbTraceBlockchain.getBatchTransactions(batchId)
  }

  const verifyTransaction = async (txHash: string) => {
    return await HerbTraceBlockchain.verifyTransaction(txHash)
  }

  return {
    recordCollection,
    recordProcessing,
    getBatchHistory,
    verifyTransaction,
  }
}
