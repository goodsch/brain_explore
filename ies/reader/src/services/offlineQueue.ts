/**
 * Offline Queue Service for IES Reader
 *
 * Handles queueing and retry logic for backend operations when offline.
 * Stores operations in localStorage and processes them when backend becomes available.
 */

const STORAGE_KEY = 'ies-reader-offline-queue';
const MAX_QUEUE_SIZE = 50;
const MAX_RETRIES = 3;
const RETRY_DELAYS = [5000, 30000, 120000]; // 5s, 30s, 2min

export interface NotePayload {
  title: string;
  content: string;
  resonance_signal: string;
  energy_level: string;
  source_id?: string;
}

export interface JourneyEntryPoint {
  type: string;
  reference: string;
}

export interface JourneyPathStep {
  entity_id: string;
  entity_name: string;
  timestamp: string;
  source_passage: string | null;
  dwell_time_seconds: number;
}

export interface JourneyPayload {
  user_id: string;
  entry_point: JourneyEntryPoint;
  path: JourneyPathStep[];
  marks: [];
  thinking_partner_exchanges: [];
  title: string | null;
  tags: string[];
  notes: string | null;
}

export type OperationPayload = NotePayload | JourneyPayload | unknown;

export interface QueuedOperation {
  id: string;
  userId: string;
  operationType: 'journey' | 'profile' | 'feedback' | 'note';
  payload: OperationPayload;
  endpoint: string;
  timestamp: string;
  retryCount: number;
  lastError?: string;
}

export interface OfflineQueueState {
  version: string;
  operations: QueuedOperation[];
  failed: QueuedOperation[];
  lastProcessedAt: string | null;
}

class OfflineQueue {
  private processingTimeout: number | null = null;

  /**
   * Generate unique operation ID
   */
  private generateOperationId(): string {
    return `op-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Load queue state from localStorage
   */
  private loadState(): OfflineQueueState {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) {
        return this.createEmptyState();
      }

      const state = JSON.parse(data) as OfflineQueueState;

      // Handle version migrations if needed
      if (!state.version) {
        return this.createEmptyState();
      }

      return state;
    } catch (error) {
      console.error('Failed to load offline queue:', error);
      return this.createEmptyState();
    }
  }

  /**
   * Save queue state to localStorage
   */
  private saveState(state: OfflineQueueState): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save offline queue:', error);
      // If localStorage is full, try clearing old failed operations
      if (error instanceof Error && error.name === 'QuotaExceededError') {
        state.failed = [];
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (retryError) {
          console.error('Failed to save even after clearing failed queue:', retryError);
        }
      }
    }
  }

  /**
   * Create empty queue state
   */
  private createEmptyState(): OfflineQueueState {
    return {
      version: '1.0',
      operations: [],
      failed: [],
      lastProcessedAt: null,
    };
  }

  /**
   * Add operation to queue
   */
  enqueue(operation: Omit<QueuedOperation, 'id' | 'timestamp' | 'retryCount'>): string {
    const state = this.loadState();

    const queuedOp: QueuedOperation = {
      ...operation,
      id: this.generateOperationId(),
      timestamp: new Date().toISOString(),
      retryCount: 0,
    };

    // Add to front of queue (newest first)
    state.operations.unshift(queuedOp);

    // Enforce max queue size (remove oldest)
    if (state.operations.length > MAX_QUEUE_SIZE) {
      const discarded = state.operations.splice(MAX_QUEUE_SIZE);
      console.warn(`Queue full: discarded ${discarded.length} oldest operations`);
    }

    this.saveState(state);

    // Schedule processing
    this.scheduleProcessing(0);

    return queuedOp.id;
  }

  /**
   * Get current queue status
   */
  getStatus(): { queuedCount: number; failedCount: number; lastProcessedAt: string | null } {
    const state = this.loadState();
    return {
      queuedCount: state.operations.length,
      failedCount: state.failed.length,
      lastProcessedAt: state.lastProcessedAt,
    };
  }

  /**
   * Get all queued operations (for debugging/UI display)
   */
  getQueuedOperations(): QueuedOperation[] {
    const state = this.loadState();
    return [...state.operations];
  }

  /**
   * Get all failed operations (for debugging/UI display)
   */
  getFailedOperations(): QueuedOperation[] {
    const state = this.loadState();
    return [...state.failed];
  }

  /**
   * Schedule queue processing with delay
   */
  private scheduleProcessing(delayMs: number): void {
    if (this.processingTimeout !== null) {
      clearTimeout(this.processingTimeout);
    }

    this.processingTimeout = window.setTimeout(() => {
      this.processQueue().catch((error) => {
        console.error('Queue processing failed:', error);
      });
    }, delayMs);
  }

  /**
   * Process all operations in queue
   */
  async processQueue(): Promise<{ succeeded: number; failed: number }> {
    const state = this.loadState();

    if (state.operations.length === 0) {
      return { succeeded: 0, failed: 0 };
    }

    let succeeded = 0;
    let failed = 0;

    // Process operations oldest first (reverse order)
    const operations = [...state.operations].reverse();

    for (const op of operations) {
      try {
        await this.executeOperation(op);

        // Success: remove from queue
        this.removeOperation(op.id);
        succeeded++;

      } catch (error) {
        failed++;

        // Increment retry count
        op.retryCount++;
        op.lastError = error instanceof Error ? error.message : 'Unknown error';

        if (op.retryCount >= MAX_RETRIES) {
          // Max retries reached: move to failed queue
          this.moveToFailed(op);
          console.error(`Operation ${op.id} failed after ${MAX_RETRIES} attempts:`, op.lastError);
        } else {
          // Schedule retry with exponential backoff
          this.updateOperation(op);
          const delay = RETRY_DELAYS[op.retryCount - 1] || RETRY_DELAYS[RETRY_DELAYS.length - 1];
          console.warn(`Operation ${op.id} failed (attempt ${op.retryCount}), retrying in ${delay}ms`);
          this.scheduleProcessing(delay);
        }
      }
    }

    // Update last processed timestamp
    const updatedState = this.loadState();
    updatedState.lastProcessedAt = new Date().toISOString();
    this.saveState(updatedState);

    return { succeeded, failed };
  }

  /**
   * Execute a single operation by making the HTTP request
   */
  private async executeOperation(op: QueuedOperation): Promise<void> {
    const API_BASE = 'http://localhost:8081';

    const response = await fetch(`${API_BASE}${op.endpoint}`, {
      method: 'POST', // Most operations are POST
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(op.payload),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    // Parse response to validate JSON (will throw if invalid)
    await response.json();
  }

  /**
   * Remove operation from queue
   */
  private removeOperation(operationId: string): void {
    const state = this.loadState();
    state.operations = state.operations.filter(op => op.id !== operationId);
    this.saveState(state);
  }

  /**
   * Update operation in queue (after failed retry)
   */
  private updateOperation(operation: QueuedOperation): void {
    const state = this.loadState();
    const index = state.operations.findIndex(op => op.id === operation.id);

    if (index !== -1) {
      state.operations[index] = operation;
      this.saveState(state);
    }
  }

  /**
   * Move operation to failed queue
   */
  private moveToFailed(operation: QueuedOperation): void {
    const state = this.loadState();

    // Remove from operations queue
    state.operations = state.operations.filter(op => op.id !== operation.id);

    // Add to failed queue
    state.failed.push(operation);

    this.saveState(state);
  }

  /**
   * Retry a failed operation (move it back to operations queue)
   */
  retryFailed(operationId: string): boolean {
    const state = this.loadState();
    const index = state.failed.findIndex(op => op.id === operationId);

    if (index === -1) {
      return false;
    }

    const operation = state.failed[index];

    // Reset retry count
    operation.retryCount = 0;
    delete operation.lastError;

    // Move back to operations queue
    state.failed.splice(index, 1);
    state.operations.unshift(operation);

    this.saveState(state);

    // Trigger processing
    this.scheduleProcessing(0);

    return true;
  }

  /**
   * Clear all failed operations
   */
  clearFailed(): void {
    const state = this.loadState();
    state.failed = [];
    this.saveState(state);
  }

  /**
   * Clear entire queue (for testing/reset)
   */
  clearAll(): void {
    localStorage.removeItem(STORAGE_KEY);
  }
}

// Export singleton instance
export const offlineQueue = new OfflineQueue();
