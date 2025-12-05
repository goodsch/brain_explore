/**
 * IES Block Schema Types
 *
 * Merged architecture combining:
 * - IES Architecture Package (Quick Capture system, Seedling types, block schemas)
 * - Current ADHD-friendly structure (resonance signals, energy levels, backend linking)
 *
 * Two Status Systems:
 * - capture_status: AI processing state (raw → classified → processed)
 * - status: User engagement state (captured → exploring → anchored)
 */

// === Status Types ===

/** AI processing state for captures */
export type CaptureStatus = 'raw' | 'classified' | 'processed';

/** User engagement state for personal knowledge */
export type UserStatus = 'captured' | 'exploring' | 'anchored';

// === ADHD Extensions ===

/** Emotional retrieval cues supporting ADHD memory patterns */
export enum ResonanceSignal {
    Spark = 'spark',
    Curiosity = 'curiosity',
    Delight = 'delight',
    Concern = 'concern',
    Tension = 'tension',
    Dread = 'dread',
    Clarity = 'clarity',
    Stuck = 'stuck',
}

/** Energy-based navigation for mood-appropriate access */
export enum EnergyLevel {
    Low = 'low',
    Medium = 'medium',
    High = 'high',
}

// === Seedling Types ===

/** Atomic idea types from Architecture Package */
export type IdeaType =
    | 'question'
    | 'insight'
    | 'observation'
    | 'moment'
    | 'schema'
    | 'contradiction'
    | 'what_if'
    | 'other';

/** Clarity level for fuzzy-to-clear progression */
export type ClarityLevel = 'fuzzy' | 'partial' | 'clear';

/** Confidence level for idea strength */
export type ConfidenceLevel = 'low' | 'medium' | 'high';

// === Capture Channels ===

/** How content was captured */
export type CaptureChannel = 'phone' | 'readest' | 'web' | 'voice' | 'other';

/** Source of the capture */
export type CaptureSource =
    | 'ios_shortcut'
    | 'readest'
    | 'browser_extension'
    | 'mcp_tool'
    | 'manual'
    | 'other';

// === Block Types ===

/** Six formal block types from Architecture Package */
export type BlockType =
    | 'seed'
    | 'shaping'
    | 'map'
    | 'concept'
    | 'decision'
    | 'log_entry';

// === Base Metadata ===

/** Common fields shared by all block types */
export interface BaseMeta {
    block_type?: BlockType;
    be_id?: string | null;
    be_type?: string | null;
    resonance_signal?: ResonanceSignal | null;
    energy_level?: EnergyLevel | null;
    exploration_visits?: number;
    status?: UserStatus;
    created_at?: string;
    last_touched_at?: string;
}

// === Quick Capture Metadata ===

/** Metadata for raw captures before classification */
export interface QuickCaptureMeta extends BaseMeta {
    quick_capture: boolean;
    capture_channel: CaptureChannel;
    capture_source: CaptureSource;
    capture_time: string;
    capture_status: CaptureStatus;

    // AI-populated fields (after classification)
    auto_summary?: string | null;
    auto_labels?: string[];
    linked_concepts?: string[];

    // Optional book metadata (from Readest captures)
    book_title?: string;
    book_author?: string;
    location?: string;
    highlight_id?: string;
    entities?: string[];

    // Backlink to source (if promoted)
    source_capture_id?: string;
}

// === Seed Block Metadata ===

/** Metadata for atomic ideas (seedlings) */
export interface SeedBlockMeta extends BaseMeta {
    block_type: 'seed';
    idea_type: IdeaType;
    domain?: string;
    source?: 'inbox' | 'dialogue' | 'project' | 'external' | string;
    clarity?: ClarityLevel;
    confidence?: ConfidenceLevel;
    related_concepts?: string[];
    related_seedlings?: string[];
    tags?: string[];
    source_capture_id?: string;
}

// === Shaping Block Metadata ===

/** Metadata for dialogue segments during structured thinking */
export interface ShapingBlockMeta extends BaseMeta {
    block_type: 'shaping';
    session_id: string;
    speaker: 'user' | 'ai';
    phase: 'exploration' | 'challenge' | 'synthesis' | 'meta';
    related_seedlings?: string[];
}

// === Map Block Metadata ===

/** Metadata for visual maps and concept clusters */
export interface MapBlockMeta extends BaseMeta {
    block_type: 'map';
    map_type:
        | 'concept_cluster'
        | 'timeline'
        | 'system'
        | 'schema'
        | 'perspective'
        | 'other';
    focus?: string;
    related_concepts?: string[];
    related_seedlings?: string[];
    entry_points?: string[];
}

// === Concept Block Metadata ===

/** Metadata for canonical concepts in the knowledge graph */
export interface ConceptBlockMeta extends BaseMeta {
    block_type: 'concept';
    concept_id: string;
    concept_name: string;
    domain?: string;
    concept_status?: 'active' | 'draft' | 'deprecated';
    version?: string | number;
}

// === Decision Block Metadata ===

/** Metadata for project decisions */
export interface DecisionBlockMeta extends BaseMeta {
    block_type: 'decision';
    project_id: string;
    decision_status: 'pending' | 'accepted' | 'rejected' | 'revisited';
    rationale?: string;
    decided_at?: string;
    related_maps?: string[];
    related_concepts?: string[];
}

// === Log Entry Metadata ===

/** Metadata for activity log entries */
export interface LogEntryMeta extends BaseMeta {
    block_type: 'log_entry';
    context: 'project' | 'system' | 'personal' | string;
    project_id?: string;
    timestamp: string;
    summary: string;
    related_blocks?: string[];
}

// === Union Type ===

/** All possible block metadata types */
export type BlockMeta =
    | QuickCaptureMeta
    | SeedBlockMeta
    | ShapingBlockMeta
    | MapBlockMeta
    | ConceptBlockMeta
    | DecisionBlockMeta
    | LogEntryMeta;

// === Helper Constants ===

/** Human-readable labels for idea types */
export const IDEA_TYPE_LABELS: Record<IdeaType, string> = {
    question: 'Question',
    insight: 'Insight',
    observation: 'Observation',
    moment: 'Moment',
    schema: 'Schema',
    contradiction: 'Contradiction',
    what_if: 'What If',
    other: 'Other',
};

/** Emoji icons for idea types */
export const IDEA_TYPE_ICONS: Record<IdeaType, string> = {
    question: '❓',
    insight: '💡',
    observation: '👁️',
    moment: '⏱️',
    schema: '🏗️',
    contradiction: '⚡',
    what_if: '🔮',
    other: '📝',
};

/** Human-readable labels for capture status */
export const CAPTURE_STATUS_LABELS: Record<CaptureStatus, string> = {
    raw: 'Raw',
    classified: 'Classified',
    processed: 'Processed',
};

/** Human-readable labels for user status */
export const USER_STATUS_LABELS: Record<UserStatus, string> = {
    captured: 'Captured',
    exploring: 'Exploring',
    anchored: 'Anchored',
};

/** Folder paths for seedling types */
export const SEEDLING_FOLDER_MAP: Record<IdeaType, string> = {
    question: 'Seedlings/Questions',
    insight: 'Seedlings/Insights',
    observation: 'Seedlings/Observations',
    moment: 'Seedlings/Moments',
    schema: 'Seedlings/Schemas',
    contradiction: 'Seedlings/Contradictions',
    what_if: 'Seedlings/What_Ifs',
    other: 'Seedlings',
};
