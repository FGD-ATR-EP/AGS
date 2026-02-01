export interface SpatialMask {
    x_min: number;
    y_min: number;
    x_max: number;
    y_max: number;
}

export type CorrectionActionType = "move" | "erase" | "redraw" | "emphasize" | "lock";

export interface CorrectionEvent {
    event_id: string;
    session_id: string;
    timestamp: number;
    affected_region: SpatialMask;
    action_type: CorrectionActionType;
    intent_vector: number[]; // [dx, dy, strength, ...]
    mode: "short_decay" | "persistent";
}

export class CorrectionHandler {
    private sessionId: string;
    private pendingEvents: CorrectionEvent[] = [];
    private batchInterval: number = 32; // ~30fps sampling rate for network efficiency
    private batchTimer: any = null;

    constructor(sessionId: string) {
        this.sessionId = sessionId;
    }

    private generateUUID(): string {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    public handleGesture(
        actionType: CorrectionActionType,
        region: SpatialMask,
        vector: number[],
        mode: "short_decay" | "persistent" = "short_decay"
    ) {
        const event: CorrectionEvent = {
            event_id: this.generateUUID(),
            session_id: this.sessionId,
            timestamp: Date.now() / 1000.0,
            affected_region: region,
            action_type: actionType,
            intent_vector: vector,
            mode: mode
        };

        // Batch continuous gestures to avoid flooding the backend.
        // For discrete actions like 'lock', emit immediately.
        if (actionType === "move" || actionType === "erase") {
            this.pendingEvents.push(event);
            if (!this.batchTimer) {
                this.batchTimer = setTimeout(() => this.flushBatch(), this.batchInterval);
            }
        } else {
            this.emitCorrection(event);
        }
    }

    private flushBatch() {
        if (this.pendingEvents.length === 0) return;

        // "Last Write Wins" strategy for the batch window.
        // This effectively samples the continuous gesture into atomic correction events
        // that fit within the processing budget of the backend.
        const latestEvent = this.pendingEvents[this.pendingEvents.length - 1];
        this.emitCorrection(latestEvent);

        this.pendingEvents = [];
        this.batchTimer = null;
    }

    // In a real implementation, this would send data via WebSocket or HTTP POST
    private emitCorrection(event: CorrectionEvent) {
        // Placeholder for actual network call
        console.log("Emitting CorrectionEvent:", JSON.stringify(event));
    }
}
