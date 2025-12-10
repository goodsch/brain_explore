# SiYuan Folder Structure - Source of Truth

**Last Updated:** December 9, 2025
**Implementation:** `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`

> **This document is the official specification.** The code in `siyuan-structure.ts` implements this structure.

## Folder Hierarchy

```
IES/                          # Notebook (preferred names: IES, Personal, Knowledge, Notes)
├── Daily/                    # Daily notes (YYYY-MM-DD format)
│
├── Seedlings/                # Captured thoughts before they mature
│   ├── Questions/            # Open questions worth exploring
│   ├── Observations/         # Things noticed, no conclusions yet
│   ├── Moments/              # Specific experiences or events
│   ├── Schemas/              # Mental models being developed
│   ├── Contradictions/       # Conflicting ideas to reconcile
│   ├── What_Ifs/             # Hypotheticals and thought experiments
│   └── Insights/             # Emerging connections
│
├── Sessions/                 # Thinking mode sessions (ForgeMode)
│   ├── Learning/             # Deep understanding sessions
│   ├── Articulating/         # Communication clarity sessions
│   ├── Planning/             # Strategic thinking sessions
│   ├── Ideating/             # Creative exploration sessions
│   └── Reflecting/           # Meta-cognitive sessions
│
├── Flow_Maps/                # Entity relationship visualizations
├── Concepts/                 # Developed concept notes
├── Insights/                 # Matured insights (promoted from Seedlings)
├── Favorite_Problems/        # Long-term questions to hold
├── Projects/                 # Active project workspaces
├── Archive/                  # Completed/dormant items
│
└── System/                   # Plugin infrastructure
    ├── Templates/            # Note templates for each type
    └── Example_Notes/        # Reference examples
```

## Folder Purposes

### Daily/
**Pattern:** `Daily/YYYY-MM-DD`
- Auto-created daily notes
- Captures highlights, sessions, sparks from the day
- Links to other notes created that day

### Seedlings/
Low-commitment capture zones for ADHD-friendly quick entry:

| Subfolder | Purpose | Example |
|-----------|---------|---------|
| Questions | Curiosities to explore | "Why does X work this way?" |
| Observations | Raw noticing | "Noticed pattern in behavior" |
| Moments | Specific events | "Conversation with Y about Z" |
| Schemas | Mental model drafts | "Framework for thinking about..." |
| Contradictions | Tensions to hold | "A says X but B says Y" |
| What_Ifs | Hypotheticals | "What if we approached it as..." |
| Insights | Emerging connections | "Maybe X relates to Y because..." |

### Sessions/
ForgeMode thinking sessions, organized by mode:

| Mode | Purpose | Output |
|------|---------|--------|
| Learning | Deep understanding | Concept maps, summaries |
| Articulating | Clear communication | Drafts, explanations |
| Planning | Strategic thinking | Plans, timelines |
| Ideating | Creative exploration | Ideas, possibilities |
| Reflecting | Meta-cognition | Insights, lessons |

### Core Folders

| Folder | Purpose |
|--------|---------|
| Flow_Maps | Visual relationship maps from FlowMode |
| Concepts | Developed concept notes (entities from graph) |
| Insights | Matured insights promoted from Seedlings |
| Favorite_Problems | Long-term guiding questions |
| Projects | Active project workspaces |
| Archive | Completed or dormant items |

### System/
Plugin infrastructure:

| Subfolder | Contents |
|-----------|----------|
| Templates | Note templates for each seedling type, session mode |
| Example_Notes | Reference examples showing good note structure |

## Block Attributes

Notes link to backend via custom attributes:

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `custom-be-type` | Backend entity type | `concept`, `spark`, `insight` |
| `custom-be-id` | Backend entity ID | `uuid-string` |
| `custom-status` | Note lifecycle | `active`, `archived`, `promoted` |

## Implementation Details

### Notebook Resolution
The plugin finds the target notebook in this priority order:
1. Notebook named "IES"
2. Notebook named "Personal"
3. Notebook named "Knowledge"
4. Notebook named "Notes"
5. First open notebook

### Folder Creation
`ensureNotebookStructure()` in `siyuan-structure.ts`:
- Called on plugin initialization
- Creates missing folders (idempotent)
- Does not delete extra folders

### Path Format
- Use underscores for multi-word folders: `What_Ifs`, `Flow_Maps`
- No spaces in paths
- Titles can have spaces: "What Ifs", "Flow Maps"

## Migration Notes

### From Old Schema (2025-12-08)
The old schema in `docs/plans/2025-12-08-siyuan-note-schema.md` is **deprecated**. Key changes:
- Removed `Life/`, `Mind/*` hierarchy
- Flattened to single-level top folders
- Added explicit Seedlings subcategories
- Sessions organized by thinking mode

### Known Issues (Dec 9, 2025)
1. **Duplicate folders** - Some folders created twice with different IDs
2. **Extra folders** - `/Contexts/`, `/System/Dashboard/` not in spec

## Related Files

| File | Purpose |
|------|---------|
| `siyuan-structure.ts` | Implementation (source of truth) |
| `siyuan-api.ts` | Low-level SiYuan API calls |
| `IES-SYSTEM-DESIGN.md` | Why this structure exists (cognitive model) |
