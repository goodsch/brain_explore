# Framework Project Progress

*Implementation instance of IES for therapy worldview development*

**Current Status:** Infrastructure in place, Configuration system not yet implemented

| Component | Status | What It Does |
|-----------|--------|--------------|
| IES Backend | ✅ Using | Port 8081, entity extraction, chat, Neo4j storage |
| IES Plugin | ✅ Using | SiYuan sidebar UI for sessions |
| User Config | 🔲 Planned | User profiles, personalization |
| Domain Config | 🔲 Planned | Therapy-specific settings |

---

## What This Layer Does

The Framework Project sits between generic IES and domain-specific Therapy. It:
- **Configures IES** for this specific implementation
- **Bridges** between tool layer (IES) and content layer (Therapy)
- **Manages** user profiles and deployment settings
- **Will contain** configuration files currently hardcoded in IES

---

## What We're Actually Using (Status Report)

### Backend API (Working)
- Running on port 8081
- All 16 endpoints tested and functional
- Handling entity extraction via Claude API
- Storing to Neo4j, linking to Qdrant
- User profile (chris) stored and loaded correctly

### Plugin (Working)
- Sidebar UI in SiYuan
- Works on iPad (via forwardProxy)
- Works on Desktop (Docker SiYuan)
- Session start/chat/end flow complete

### User Profile
- 6-dimension cognitive model for chris
- Profile characteristics:
  - Processing: Detail-first → framework
  - Attention: Problem-solving triggers hyperfocus
  - Danger zones: Rabbit holes, scope creep
  - Session rhythm: Persistent until forced stop
  - Communication: High verbal fluency, prefers pushback
  - Executive: High initiation friction
  - Working memory: Context-dependent (strong in therapist mode)

### Knowledge Base
- 63 therapy/psychology books loaded
- Neo4j: 48,987 nodes
- Qdrant: 27,523 chunks indexed
- Literature linking working (score threshold: 0.45)

---

## What Needs Implementation

### Immediate (Phase 6 - Config System)

#### 1. User Profile Configuration
```
framework/config/
├── chris_profile.json           # User profile (currently in Neo4j backend)
└── profile_schema.json          # Schema for new users
```

Currently hardcoded in: `ies/backend/config.py`

#### 2. Domain Configuration
```
framework/config/
├── domain.json                  # Therapy-specific settings
│   ├── entity_domain
│   ├── default_notebook_id
│   ├── extraction_prompt_template
│   └── approach_definitions
└── domain_schema.json
```

Currently hardcoded in: `ies/backend/schemas/entity.py`

#### 3. Deployment Configuration
```
framework/.env.local            # Environment overrides per deployment
```

Currently requires manual editing of `.env` at project root

#### 4. Plugin Configuration
```
framework/plugin/
├── settings.json                # Plugin-specific overrides
└── ...
```

Currently hardcoded in: `ies/plugin/src/ies-sidebar-simple.svelte`

### Timeline

**Phase 6 (Next):**
1. Extract user profile to JSON config
2. Extract domain config from IES backend
3. Create configuration loading system
4. Update plugin to read backend settings

**Phase 7+ (Future):**
1. Multi-user support
2. Multiple domain support
3. Deployment templating
4. Configuration UI

---

## Session Log

### 2025-12-02: Documentation Cleanup & Clarification

**Accomplished:**
- Clarified that Framework layer is not yet implemented
- Updated progress to honest status
- Created cleanup plan for all documentation
- Identified configuration extraction as Phase 6 work

**Key Insight:**
This is OK — system works well as therapy-focused monolith. Generalization is incremental future work.

---

### 2025-12-01: Entity Page-Data Endpoint & Architecture Decision

**Accomplished:**
- Backend provides `/session/entities/{user_id}/{entity_name}/page-data` endpoint
- Architecture decision: Option C (hybrid) — backend provides data, plugin/Claude creates SiYuan pages
- Score threshold for literature linking tuned from 0.7 → 0.45
- Verified 8 entities → 40 literature links working

---

### 2025-12-01: Profile Onboarding Complete

**Accomplished:**
- Completed `/onboard-profile` session for chris
- 6-dimension profile stored in Neo4j
- Profile characteristics identified (see above)
- Ready for content exploration

---

## Next Session Priorities

### High Priority
1. [ ] Extract USER_ID from plugin (currently hardcoded "chris")
2. [ ] Extract BACKEND_HOST from plugin (currently hardcoded IP)
3. [ ] Create configuration loading in backend
4. [ ] Create .env.local template

### Medium Priority
1. [ ] Create user profile JSON schema
2. [ ] Create domain configuration schema
3. [ ] Document configuration system design

### Documentation
1. [ ] Update SiYuan notebook with progress
2. [ ] Document configuration extraction steps
3. [ ] Create "how to create a Framework instance" guide

---

## Resources

- **Backend:** `/home/chris/dev/projects/codex/brain_explore/ies/backend/`
- **Plugin:** `/home/chris/dev/projects/codex/brain_explore/ies/plugin/`
- **Design Docs:** `/home/chris/dev/projects/codex/brain_explore/docs/plans/`
- **SiYuan Notebook:** "Framework Project"

---

## Known Issues & Blockers

### Hardcoded Values (Won't block usage, but need configuration)
- ❌ USER_ID hardcoded in plugin ("chris")
- ❌ BACKEND_HOST hardcoded in plugin ("192.168.86.60")
- ❌ DEFAULT_NOTEBOOK hardcoded in backend ("20251201113102-ctr4bco")
- ❌ EntityDomain enum hardcodes "therapy"
- ❌ Extraction prompts reference therapy concepts

### Why They're OK Right Now
- ✅ System works perfectly for this implementation
- ✅ Not blocking content development
- ✅ Clear path to extraction (Phase 6)
- ✅ Won't require major refactoring

### How We'll Fix Them
1. Create configuration system in Framework layer
2. Move hardcoded values to config files
3. Update IES to read from configuration
4. Plugin reads backend settings endpoint

---

## Architecture Vision

### Current (Monolith)
```
chris + therapy → IES Backend (hardcoded values) + Plugin
```

### Target (Configurable)
```
Framework Config ─┐
                  ├─ IES Backend (reads config) + Plugin (reads settings)
Therapy Content ─┘
```

### Ultimate (Generic)
```
Config Layer A ─┐
                ├─ Generic IES Backend
Config Layer B ─┘
```

We're moving left → right, one step at a time.
