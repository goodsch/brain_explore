# SiYuan Architecture Merge Design

**Purpose:** Merge the IES SiYuan Architecture Package with current implementation
**Created:** December 5, 2025
**Status:** Design Complete, Ready for Implementation

---

## Design Decisions

These decisions were made through collaborative brainstorming:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Folder structure | **Merged (9 folders)** | Best of both: Package structure + ADHD scaffolds |
| Insights conflict | **Keep both** | Seedlings/Insights (raw) vs /Insights/ (promoted) |
| Metadata storage | **Both YAML + attrs** | YAML for readability, attrs for SQL queries |
| Status lifecycle | **Two separate fields** | `capture_status` (AI) vs `status` (user) |

---

## 1. Merged Folder Structure

```
IES SiYuan Structure (9 top-level folders)
├── Daily/                    # Quick captures (Package's 00_Inbox)
├── Seedlings/                # Atomic ideas (Package's 01_Seedlings)
│   ├── Questions/
│   ├── Observations/
│   ├── Moments/
│   ├── Schemas/
│   ├── Contradictions/
│   ├── What_Ifs/
│   └── Insights/             # Raw "aha" moments (not yet validated)
├── Sessions/                 # Mode-specific thinking (Package's 02_Shaping)
│   ├── Learning/
│   ├── Articulating/
│   ├── Planning/
│   ├── Ideating/
│   └── Reflecting/
├── Flow_Maps/                # Visual maps (Package's 03_Flow_Maps)
├── Concepts/                 # Canonical concepts (Package's 04_Concepts)
├── Insights/                 # Promoted/validated insights (current)
├── Favorite_Problems/        # ADHD anchor questions (current)
├── Projects/                 # Active work (Package's 05_Projects)
└── Archive/                  # Retired material (Package's 06_Archive)
```

### Implementation: STRUCTURE_FOLDERS

Replace current array in `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`:

```typescript
const STRUCTURE_FOLDERS = [
    // Daily quick captures
    { path: 'Daily', title: 'Daily' },

    // Seedlings (atomic ideas)
    { path: 'Seedlings', title: 'Seedlings' },
    { path: 'Seedlings/Questions', title: 'Seedlings – Questions' },
    { path: 'Seedlings/Observations', title: 'Seedlings – Observations' },
    { path: 'Seedlings/Moments', title: 'Seedlings – Moments' },
    { path: 'Seedlings/Schemas', title: 'Seedlings – Schemas' },
    { path: 'Seedlings/Contradictions', title: 'Seedlings – Contradictions' },
    { path: 'Seedlings/What_Ifs', title: 'Seedlings – What Ifs' },
    { path: 'Seedlings/Insights', title: 'Seedlings – Insights' },

    // Sessions by mode
    { path: 'Sessions', title: 'Sessions' },
    { path: 'Sessions/Learning', title: 'Learning Sessions' },
    { path: 'Sessions/Articulating', title: 'Articulating Sessions' },
    { path: 'Sessions/Planning', title: 'Planning Sessions' },
    { path: 'Sessions/Ideating', title: 'Ideating Sessions' },
    { path: 'Sessions/Reflecting', title: 'Reflecting Sessions' },

    // Maps, concepts, and promoted insights
    { path: 'Flow_Maps', title: 'Flow Maps' },
    { path: 'Concepts', title: 'Concepts' },
    { path: 'Insights', title: 'Insights' },

    // ADHD scaffolds and projects
    { path: 'Favorite_Problems', title: 'Favorite Problems' },
    { path: 'Projects', title: 'Projects' },

    // Archive
    { path: 'Archive', title: 'Archive' },
];
```

---

## 2. Merged Block Schema

### Two Status Fields

| Field | Values | Purpose |
|-------|--------|---------|
| `capture_status` | `raw` → `classified` → `processed` | AI processing state |
| `status` | `captured` → `exploring` → `anchored` | User engagement state |

### Complete Schema (YAML Frontmatter)

```yaml
# === Block Type ===
block_type: seed | shaping | map | concept | decision | log_entry

# === Package Seedling Fields ===
idea_type: question | insight | observation | moment | schema | contradiction | what_if
domain: ADHD | Therapy | Self | Systems | Cognition | ...
clarity: fuzzy | partial | clear
confidence: low | medium | high

# === Package Quick Capture Fields ===
quick_capture: true | false
capture_channel: phone | readest | web | voice | other
capture_source: ios_shortcut | readest | browser_extension | mcp_tool | manual
capture_time: 2025-12-05T10:00:00-05:00
capture_status: raw | classified | processed

# === ADHD Extensions ===
resonance_signal: curiosity | delight | concern | tension | dread | clarity | stuck | spark
energy_level: low | medium | high
status: captured | exploring | anchored
exploration_visits: 0

# === Backend Linking ===
be_id: spark_abc123
be_type: spark | insight | thread | favorite_problem

# === Timestamps ===
created_at: 2025-12-05T10:00:00-05:00
last_touched_at: 2025-12-05T10:00:00-05:00

# === Relationships ===
source_capture_id: qc_xyz789  # Backlink to originating quick capture
related_concepts: [concept_1, concept_2]
related_seedlings: [seed_1, seed_2]
```

---

## 3. TypeScript Types

Create new file: `.worktrees/siyuan/ies/plugin/src/types/blocks.ts`

```typescript
export type CaptureStatus = 'raw' | 'classified' | 'processed';
export type UserStatus = 'captured' | 'exploring' | 'anchored';

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

export enum EnergyLevel {
    Low = 'low',
    Medium = 'medium',
    High = 'high',
}

export interface BaseMeta {
    block_type?: string;
    be_id?: string | null;
    be_type?: string | null;
    resonance_signal?: ResonanceSignal | null;
    energy_level?: EnergyLevel | null;
    exploration_visits?: number;
    status?: UserStatus;
}

export interface QuickCaptureMeta extends BaseMeta {
    quick_capture: boolean;
    capture_channel: 'phone' | 'readest' | 'web' | 'voice' | 'other';
    capture_source: 'ios_shortcut' | 'readest' | 'browser_extension' | 'mcp_tool' | 'manual' | 'other';
    capture_time: string;
    capture_status: CaptureStatus;
    auto_summary?: string | null;
    auto_labels?: string[];
    linked_concepts?: string[];
    book_title?: string;
    book_author?: string;
    location?: string;
    highlight_id?: string;
    entities?: string[];
}

export interface SeedBlockMeta extends BaseMeta {
    block_type: 'seed';
    idea_type: 'question' | 'insight' | 'observation' | 'moment' | 'schema' | 'contradiction' | 'what_if' | 'other';
    domain?: string;
    source?: 'inbox' | 'dialogue' | 'project' | 'external' | string;
    clarity?: 'fuzzy' | 'partial' | 'clear';
    confidence?: 'low' | 'medium' | 'high';
    created_at?: string;
    last_touched_at?: string;
    related_concepts?: string[];
    tags?: string[];
    source_capture_id?: string;
}

export interface ShapingBlockMeta extends BaseMeta {
    block_type: 'shaping';
    session_id: string;
    speaker: 'chris' | 'ai';
    phase: 'exploration' | 'challenge' | 'synthesis' | 'meta';
    related_seedlings?: string[];
    created_at?: string;
    last_touched_at?: string;
}

export interface MapBlockMeta extends BaseMeta {
    block_type: 'map';
    map_type: 'concept_cluster' | 'timeline' | 'system' | 'schema' | 'perspective' | 'other';
    focus?: string;
    related_concepts?: string[];
    related_seedlings?: string[];
    entry_points?: string[];
    created_at?: string;
    last_touched_at?: string;
}

export interface ConceptBlockMeta extends BaseMeta {
    block_type: 'concept';
    concept_id: string;
    concept_name: string;
    domain?: string;
    concept_status?: 'active' | 'draft' | 'deprecated';
    created_at?: string;
    last_touched_at?: string;
    version?: string | number;
}

export interface DecisionBlockMeta extends BaseMeta {
    block_type: 'decision';
    project_id: string;
    decision_status: 'pending' | 'accepted' | 'rejected' | 'revisited';
    rationale?: string;
    created_at?: string;
    decided_at?: string;
    related_maps?: string[];
    related_concepts?: string[];
}

export interface LogEntryMeta extends BaseMeta {
    block_type: 'log_entry';
    context: 'project' | 'system' | 'personal' | string;
    project_id?: string;
    timestamp: string;
    summary: string;
    related_blocks?: string[];
}

export type BlockMeta =
    | QuickCaptureMeta
    | SeedBlockMeta
    | ShapingBlockMeta
    | MapBlockMeta
    | ConceptBlockMeta
    | DecisionBlockMeta
    | LogEntryMeta;
```

---

## 4. setBlockMeta Helper

Add to `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`:

```typescript
import { setBlockAttrs } from '../api';

/**
 * Sets block metadata in both YAML frontmatter format and SiYuan attributes.
 * Returns YAML string for insertion at top of block content.
 * Sets custom-* attributes for SQL querying.
 */
export async function setBlockMeta(
    blockId: string,
    meta: Record<string, any>
): Promise<string> {
    if (!blockId) {
        throw new Error('setBlockMeta requires a blockId');
    }

    // Build YAML frontmatter string
    const yaml = serializeFrontmatter(meta);
    const attrs: Record<string, string> = {};

    // Mirror all meta keys into SiYuan custom-* attrs for querying
    for (const [key, value] of Object.entries(meta)) {
        if (value === undefined) continue;
        const attrKey = `custom-${key}`;
        if (value === null) {
            attrs[attrKey] = '';
            continue;
        }
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
            attrs[attrKey] = String(value);
            continue;
        }
        // Arrays / objects → JSON string for lossless round-trip
        attrs[attrKey] = JSON.stringify(value);
    }

    await setBlockAttrs(blockId, attrs);
    return yaml;
}

/**
 * Updates capture_status and sets last_touched_at timestamp.
 */
export async function updateCaptureStatus(
    blockId: string,
    newStatus: 'raw' | 'classified' | 'processed'
): Promise<void> {
    const now = new Date().toISOString();
    await setBlockAttrs(blockId, {
        'custom-capture_status': newStatus,
        'custom-last_touched_at': now,
    });
}

/**
 * Updates user engagement status and increments exploration visits.
 */
export async function updateUserStatus(
    blockId: string,
    newStatus: 'captured' | 'exploring' | 'anchored',
    currentVisits: number = 0
): Promise<void> {
    const now = new Date().toISOString();
    await setBlockAttrs(blockId, {
        'custom-status': newStatus,
        'custom-exploration_visits': String(currentVisits + 1),
        'custom-last_touched_at': now,
    });
}
```

---

## 5. Quick Capture Flow

```
┌─────────────────────────────────────────────────────────────┐
│  CAPTURE (raw)                                               │
│  - HTTP POST, Shortcut, MCP, Readest highlight              │
│  - Write to Daily/QuickCapture_YYYY-MM-DD.md                │
│  - Set: quick_capture=true, capture_status=raw              │
│  - Optional: resonance_signal, energy_level                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CLASSIFY (background, AI)                                   │
│  - Compute auto_summary, auto_labels                        │
│  - Set linked_concepts (only if trivially obvious)          │
│  - Update: capture_status=classified                        │
│  - NO: moving, splitting, attaching to projects             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PROCESS (interactive, sidebar)                              │
│  - User triggers "Process this capture"                     │
│  - Options: Create Seedling(s), Link to Concept/Project     │
│  - Spawn seeds in Seedlings/<type> with source_capture_id   │
│  - Update: capture_status=processed                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PROMOTE (user decision)                                     │
│  - Seedling → /Insights/ (validated)                        │
│  - Update: status=anchored                                  │
│  - Backend sync: be_id, be_type                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Implementation Plan

### Phase 1: Foundation (siyuan worktree)

1. Update `STRUCTURE_FOLDERS` array
2. Create `types/blocks.ts` with all interfaces
3. Add `setBlockMeta` and status helper functions
4. Test folder creation with new structure

### Phase 2: Quick Capture Enhancement

1. Update Quick Capture UI to use new schema
2. Implement capture_status transitions
3. Add sidebar queue filtering by capture_status

### Phase 3: Seedling & Promotion

1. Implement "Process this capture" workflow
2. Add seedling type selection UI
3. Implement promotion flow (Seedlings/Insights → /Insights/)

### Phase 4: Integration

1. Update ForgeMode to use new session folders
2. Sync with backend Personal Graph API
3. Add health checks for orphan/stale content

---

## 7. Success Criteria

- [ ] All 9 top-level folders created on plugin init
- [ ] All 7 Seedling subfolders created
- [ ] Quick captures have YAML frontmatter AND custom-* attrs
- [ ] capture_status and status fields work independently
- [ ] Seedlings can be promoted to /Insights/
- [ ] Backend be_id/be_type sync works
- [ ] SiYuan SQL queries work on custom-* attrs

---

*Design by: Claude + Codex (gpt-5.1-codex-max, high reasoning)*
*Based on: IES_SiYuan_Architecture_Package_QuickCaptureUpdated*
