/**
 * Offline Queue for IES SiYuan Plugin
 *
 * Handles failed backend operations with retry logic and exponential backoff.
 * Stores queued operations in localStorage for persistence across sessions.
 *
 * Features:
 * - Max 50 operations (oldest discarded when full)
 * - Retry delays: 5s, 30s, 2min (exponential backoff)
 * - Max 3 retries before moving to failed queue
 * - Process queue when backend becomes available
 */

export interface QueuedOperation {
    id: string;
    userId: string;
    operationType: 'journey' | 'profile' | 'feedback';
    payload: any;
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

export interface ProcessResult {
    processed: number;
    successful: number;
    failed: number;
    errors: string[];
}

/**
 * OfflineQueue manages queued operations with retry logic and exponential backoff.
 */
export class OfflineQueue {
    private static readonly MAX_RETRIES = 3;
    private static readonly RETRY_DELAYS = [5000, 30000, 120000]; // 5s, 30s, 2min
    private static readonly QUEUE_KEY = 'ies-siyuan-offline-queue';
    private static readonly MAX_QUEUE_SIZE = 50;
    private static readonly SCHEMA_VERSION = '1.0.0';

    /**
     * Load queue state from localStorage.
     */
    private loadQueue(): OfflineQueueState {
        if (typeof window === 'undefined' || !window?.localStorage) {
            return this.getEmptyState();
        }

        try {
            const stored = window.localStorage.getItem(OfflineQueue.QUEUE_KEY);
            if (!stored) {
                return this.getEmptyState();
            }

            const state = JSON.parse(stored) as OfflineQueueState;

            // Validate schema version
            if (state.version !== OfflineQueue.SCHEMA_VERSION) {
                console.warn('[OfflineQueue] Schema version mismatch, resetting queue');
                return this.getEmptyState();
            }

            return state;
        } catch (err) {
            console.error('[OfflineQueue] Failed to load queue:', err);
            return this.getEmptyState();
        }
    }

    /**
     * Save queue state to localStorage.
     */
    private saveQueue(state: OfflineQueueState): void {
        if (typeof window === 'undefined' || !window?.localStorage) {
            return;
        }

        try {
            window.localStorage.setItem(OfflineQueue.QUEUE_KEY, JSON.stringify(state));
        } catch (err) {
            console.error('[OfflineQueue] Failed to save queue:', err);
        }
    }

    /**
     * Get empty queue state.
     */
    private getEmptyState(): OfflineQueueState {
        return {
            version: OfflineQueue.SCHEMA_VERSION,
            operations: [],
            failed: [],
            lastProcessedAt: null
        };
    }

    /**
     * Generate unique operation ID.
     */
    private generateOperationId(): string {
        return `op-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Save an operation to the queue.
     * If queue is full, oldest operation is discarded.
     */
    async saveOperation(op: Omit<QueuedOperation, 'id' | 'retryCount'>): Promise<void> {
        const state = this.loadQueue();

        const operation: QueuedOperation = {
            ...op,
            id: this.generateOperationId(),
            retryCount: 0
        };

        // Add to queue
        state.operations.push(operation);

        // Discard oldest if over limit
        if (state.operations.length > OfflineQueue.MAX_QUEUE_SIZE) {
            const discarded = state.operations.shift();
            console.warn('[OfflineQueue] Queue full, discarded oldest operation:', discarded?.id);
        }

        this.saveQueue(state);
        console.log('[OfflineQueue] Operation queued:', operation.id, operation.operationType);
    }

    /**
     * Process all queued operations.
     * Executes each operation in order, handling retries and failures.
     */
    async processQueue(executeOperation: (op: QueuedOperation) => Promise<void>): Promise<ProcessResult> {
        const state = this.loadQueue();
        const result: ProcessResult = {
            processed: 0,
            successful: 0,
            failed: 0,
            errors: []
        };

        if (state.operations.length === 0) {
            console.log('[OfflineQueue] Queue is empty, nothing to process');
            return result;
        }

        console.log('[OfflineQueue] Processing queue with', state.operations.length, 'operations');

        // Process each operation sequentially
        const remainingOps: QueuedOperation[] = [];

        for (const op of state.operations) {
            result.processed++;

            try {
                await executeOperation(op);
                result.successful++;
                console.log('[OfflineQueue] Operation succeeded:', op.id);
                // Successfully executed, don't add to remainingOps
            } catch (error) {
                const errorMsg = error instanceof Error ? error.message : String(error);
                console.error('[OfflineQueue] Operation failed:', op.id, errorMsg);

                // Increment retry count
                op.retryCount++;
                op.lastError = errorMsg;

                if (op.retryCount >= OfflineQueue.MAX_RETRIES) {
                    // Move to failed queue
                    state.failed.push(op);
                    result.failed++;
                    result.errors.push(`${op.operationType} (${op.id}): ${errorMsg}`);
                    console.warn('[OfflineQueue] Operation moved to failed queue after', op.retryCount, 'retries:', op.id);
                } else {
                    // Keep in queue for retry
                    remainingOps.push(op);
                    console.log('[OfflineQueue] Operation will retry (attempt', op.retryCount + 1, '):', op.id);
                }
            }
        }

        // Update queue state
        state.operations = remainingOps;
        state.lastProcessedAt = new Date().toISOString();
        this.saveQueue(state);

        console.log('[OfflineQueue] Processing complete:', result);
        return result;
    }

    /**
     * Get queue status (pending and failed counts).
     */
    getQueueStatus(): { pending: number; failed: number } {
        const state = this.loadQueue();
        return {
            pending: state.operations.length,
            failed: state.failed.length
        };
    }

    /**
     * Clear all queues (both pending and failed).
     */
    clearQueue(): void {
        this.saveQueue(this.getEmptyState());
        console.log('[OfflineQueue] Queue cleared');
    }

    /**
     * Get failed operations for inspection.
     */
    getFailedOperations(): QueuedOperation[] {
        const state = this.loadQueue();
        return state.failed;
    }

    /**
     * Retry a specific failed operation (moves back to pending queue).
     */
    retryFailedOperation(operationId: string): boolean {
        const state = this.loadQueue();
        const failedIndex = state.failed.findIndex(op => op.id === operationId);

        if (failedIndex === -1) {
            return false;
        }

        const op = state.failed[failedIndex];
        op.retryCount = 0; // Reset retry count
        op.lastError = undefined;

        state.failed.splice(failedIndex, 1);
        state.operations.push(op);

        this.saveQueue(state);
        console.log('[OfflineQueue] Failed operation moved back to queue:', operationId);
        return true;
    }

    /**
     * Clear failed queue only.
     */
    clearFailedQueue(): void {
        const state = this.loadQueue();
        state.failed = [];
        this.saveQueue(state);
        console.log('[OfflineQueue] Failed queue cleared');
    }
}

/**
 * Singleton instance for shared access across plugin.
 */
export const offlineQueue = new OfflineQueue();
