# SiYuan Plugin Settings Panel Design

**Date:** 2025-12-05
**Status:** Ready for implementation

## Overview

Add a configuration panel to the IES SiYuan plugin with:
- Ollama integration for local AI (chat + embeddings)
- Cloud API provider selection (OpenAI, Anthropic)
- Connection management (backend URL, Ollama URL)
- Notebook and display preferences

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Location | Gear icon in Dashboard header → modal | Settings are "set and forget", shouldn't clutter main UI |
| Ollama models | Auto-discover via API | Zero friction, accurate to installed models |
| Cloud providers | API key + model selection | Flexibility without complexity |
| Storage | SiYuan plugin data (`settings.json`) | Persists with workspace, API keys stay local |
| AI routing | Plugin calls Ollama directly, backend unchanged | Keeps backend stateless regarding user prefs |

## Settings Schema

```typescript
interface IESSettings {
  // Connections
  backendUrl: string;           // default: "http://192.168.86.60:8081"
  ollamaUrl: string;            // default: "http://localhost:11434"

  // AI Provider Selection
  chatProvider: 'ollama' | 'openai' | 'anthropic';
  chatModel: string;            // e.g., "llama3.2" or "gpt-4o"

  embeddingProvider: 'ollama' | 'openai';
  embeddingModel: string;       // e.g., "nomic-embed-text" or "text-embedding-3-small"

  // Cloud API Keys (stored locally, never sent to backend)
  openaiApiKey: string;
  anthropicApiKey: string;

  // Notebook Preferences
  preferredNotebooks: string[]; // default: ["Personal", "Knowledge", "Notes"]

  // User & Display
  userId: string;               // default: "chris"
  showQuestionBadges: boolean;  // default: true
  autoSaveSessions: boolean;    // default: true
}
```

## UI Layout

```
┌─────────────────────────────────────────┐
│ Settings                            ✕  │
├─────────────────────────────────────────┤
│ ▼ Connections                           │
│   IES Backend URL: [http://192.168...] │
│   Status: ● Connected                   │
│                                         │
│   Ollama URL: [http://localhost:11434] │
│   Status: ● Connected (4 models)        │
├─────────────────────────────────────────┤
│ ▼ AI Providers                          │
│   Chat/Generation:  [Ollama ▼]          │
│   Model:            [llama3.2 ▼]        │
│                                         │
│   Embeddings:       [OpenAI ▼]          │
│   Model:            [text-embedding-3.. │
├─────────────────────────────────────────┤
│ ▶ Cloud API Keys (collapsed)            │
├─────────────────────────────────────────┤
│ ▶ Notebook Preferences (collapsed)      │
├─────────────────────────────────────────┤
│ ▶ User & Display (collapsed)            │
└─────────────────────────────────────────┘
```

## Model Lists

**Ollama (auto-discovered):**
- Chat: All models from `GET {ollamaUrl}/api/tags`
- Embeddings: Filtered by name patterns (`embed`, `nomic`, `bge`, `e5`)

**OpenAI:**
- Chat: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `o1`, `o1-mini`
- Embeddings: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`

**Anthropic:**
- Chat: `claude-sonnet-4-20250514`, `claude-opus-4-0-20250514`, `claude-3-5-haiku-20241022`

## Integration Points

### 1. Plugin Load (`index.ts`)
- Load settings via `plugin.loadData(SETTINGS_FILE)`
- Merge with defaults for missing fields
- Initialize settings store

### 2. Settings Modal (`SettingsPanel.svelte`)
- On open: Load current settings, query Ollama for models
- On change: Auto-save via `plugin.saveData()`
- Connection status: Check on URL change (debounced 500ms)

### 3. Consumers
- `siyuan-structure.ts`: Read `backendUrl` from settings store
- `ForgeMode.svelte`: Use `chatProvider`/`chatModel` for question generation
- `QuickCapture.svelte`: Use `embeddingProvider`/`embeddingModel` for extraction

### 4. Backend
- No changes required
- Plugin makes direct calls to Ollama when selected
- Backend continues using its configured provider for graph operations

## Files to Create/Modify

```
.worktrees/siyuan/ies/plugin/src/
├── components/
│   └── SettingsPanel.svelte    # NEW - Settings modal UI (~200 lines)
├── stores/
│   └── settings.ts             # NEW - Svelte store + types (~80 lines)
├── utils/
│   ├── ollama.ts               # NEW - Ollama API client (~60 lines)
│   └── siyuan-structure.ts     # MODIFY - Use settings store
├── views/
│   └── Dashboard.svelte        # MODIFY - Add gear icon + modal
└── index.ts                    # MODIFY - Load/save settings lifecycle
```

## Implementation Order

1. **Settings store + schema** (`stores/settings.ts`)
   - Type definitions
   - Default values
   - Svelte writable store
   - Load/save helper functions

2. **Ollama client** (`utils/ollama.ts`)
   - `checkOllamaHealth(url)` → `{ ok, modelCount }`
   - `fetchOllamaModels(url)` → `Model[]`
   - Error handling for connection failures

3. **SettingsPanel component** (`components/SettingsPanel.svelte`)
   - Modal overlay with backdrop
   - Collapsible sections
   - Connection status indicators
   - Model dropdowns (reactive to provider selection)
   - Auto-save on change

4. **Dashboard integration** (`views/Dashboard.svelte`)
   - Gear icon in header (top-right)
   - `showSettings` state toggle
   - Mount SettingsPanel when open

5. **Wire up consumers**
   - Update `getConfiguredBackendUrl()` to use store
   - Update ForgeMode to check provider before AI calls
   - Update QuickCapture for embedding provider

## Success Criteria

- [ ] Settings persist across plugin reload
- [ ] Ollama models auto-populate when connected
- [ ] Connection status updates on URL change
- [ ] Cloud API keys masked in UI (password fields)
- [ ] Settings changes immediately affect AI operations
- [ ] Graceful fallback when Ollama unavailable

## Out of Scope

- Backend configuration changes
- Readest settings sync (future: could share via backend endpoint)
- Temperature/max tokens tuning (use sensible defaults)
- Multiple Ollama instances
