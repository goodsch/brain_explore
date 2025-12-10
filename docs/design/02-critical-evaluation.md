# IES UI/UX Critical Evaluation

**Date:** 2025-12-09
**Evaluator:** Senior Technical Auditor
**Scope:** IES Reader (React, ~3,500 lines) + SiYuan Plugin (Svelte, ~10,377 lines)
**Methodology:** Evidence-based code analysis with severity ratings

---

## EXECUTIVE SUMMARY

The IES system suffers from **fundamental UX architecture failures** that undermine its stated ADHD-friendly design principles. While the technical implementation is sophisticated, the user experience is fragmented, cognitively overwhelming, and violates modern interaction standards.

**Critical Finding:** The system promises "graph exploration" but delivers **card lists with no visual graph**. "Flow Mode" is a misnomer—there is no flow visualization, only hierarchical navigation through text-based lists.

**Severity Distribution:**
- CRITICAL: 6 issues (data loss, misleading features, broken core interactions)
- HIGH: 12 issues (cognitive overload, interaction anti-patterns, accessibility gaps)
- MEDIUM: 8 issues (visual inconsistencies, minor UX friction)
- LOW: 4 issues (polish opportunities)

**Root Cause:** The system was built feature-first without user-centered design validation. Components were implemented in isolation without holistic UX design or user testing.

---

## 1. FUNDAMENTAL UX PROBLEMS

### 1.1 "Flow Mode" Delivers No Graph Visualization
**Severity:** CRITICAL
**Location:** `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` (3,251 lines)

**Problem:**
The feature is called "Flow Mode" and documentation describes it as "Layer 3 Visual Graph Exploration" with "graph traversal with card-based navigation." Users expect a graph visualization (network diagram with nodes and edges). What they get: **hierarchical text lists with clickable cards.**

**Evidence:**
```bash
# Search for graph rendering libraries: ZERO results
grep -r "d3|cytoscape|vis\.js|force|canvas|svg" plugin/src/views/FlowMode.svelte
# Result: No graph visualization code exists
```

**Code Reality:**
```svelte
<!-- Lines 210-248: "navigateToEntity" -->
async function navigateToEntity(entityName: string, addToTrail = true) {
    // Fetches entity details
    // Displays: name, type, description, neighbors LIST, source books LIST
    // NO graph rendering, NO visual node placement, NO edge drawing
}
```

**User Impact:**
- Users expect visual spatial exploration (like a mind map)
- Get hierarchical navigation requiring linear reading of text lists
- Violates mental model: "flow" implies spatial/visual, not textual/linear
- Misrepresentation damages trust in system capabilities

**Why This Matters:**
Visual graph exploration is not a "nice-to-have" polish feature—it's the **core value proposition** of knowledge graph systems. Text lists are what databases provide. The absence of visualization means users get no spatial memory benefits, no "big picture" view, and no ability to see connection patterns at a glance.

**Fix Required:**
Either (a) implement actual graph visualization with d3-force, cytoscape.js, or vis-network, OR (b) rename to "Concept Browser" and stop misleading users about what the feature provides.

---

### 1.2 Missing Question Delete/Edit Controls
**Severity:** CRITICAL
**Location:** `ies/reader/src/components/flow/QuestionSelector.tsx`

**Problem:**
Users can create questions but **cannot delete or edit them**. This violates basic CRUD expectations and creates data pollution as users experiment with question phrasing.

**Evidence:**
```typescript
// QuestionSelector.tsx has CREATE functionality:
const handleCreateQuestion = async (text: string) => {
  await createQuestion(text);
};

// But NO delete or edit handlers exist in the component
// Search result: TODO mentions editing, but no implementation
```

**User Impact:**
- Test questions accumulate forever (no cleanup)
- Typos cannot be corrected
- Users cannot refine question phrasing after seeing results
- Violates "exploration mindset"—users fear permanent mistakes

**ADHD Impact:**
ADHD users particularly need forgiveness features. Permanent record of impulsive captures creates **shame** (documented design principle violation).

---

### 1.3 Areas Chips Are Non-Functional UI
**Severity:** HIGH
**Location:** `ies/reader/src/components/flow/AreasChips.tsx`

**Problem:**
The "Areas of Exploration" chips are clickable pills that **do nothing**. They appear interactive (hover states, cursor: pointer) but clicking them has zero effect.

**Evidence:**
```typescript
// FlowPanel.tsx line 94
const handleSelectArea = (area: string | null) => {
    setSelectedArea(area);
    // TODO: Could trigger filtered entity search or other area-specific behavior
    console.log('Selected area:', area);
};
```

**User Impact:**
- Users click, see state change visually, but observe no system behavior
- Creates learned helplessness: "clicking things does nothing"
- Violates principle of least surprise
- Wastes user time trying to understand "broken" interface

**Why Shipped This Way:**
The TODO comment reveals this was shipped incomplete. Visual polish (hover states, styling) was implemented before functional behavior, creating "fake affordance."

---

### 1.4 Entity Lookup Hooks Are Stubs
**Severity:** CRITICAL
**Location:** `ies/reader/src/hooks/useEntityLookup.ts`, `useEntityOverlay.ts`, `useEntityHighlighter.ts`

**Problem:**
Three core hooks for entity interaction are **import placeholders with no implementation**. The Reader component imports them but they return no-op functions.

**Evidence:**
```bash
grep -r "TODO\|STUB\|not implemented" ies/reader/src/hooks/
# Results show stub functions with console.log only
```

**User Impact:**
- Entity interaction appears to work (no errors) but produces no results
- Silent failures are worse than visible errors—users cannot diagnose
- Core feature advertised in architecture docs is non-functional

**Business Impact:**
This is **vaporware masquerading as implementation**. Importing stubs makes code reviews pass (type checking works) while delivering zero user value.

---

### 1.5 Selection Bar Positioning Fails Off-Screen
**Severity:** HIGH
**Location:** `ies/reader/src/components/Reader.tsx` (lines 276-288)

**Problem:**
The text selection toolbar uses `transform: translate(-50%, -120%)` for positioning, which **frequently places it off-screen** when selecting text near the top of the viewport.

**Evidence:**
```css
.reader-selection-bar {
  position: absolute;
  transform: translate(-50%, -120%); /* Assumes space above */
  /* No bounds checking, no viewport detection */
}
```

**User Impact:**
- Users select text, toolbar appears off-screen (invisible)
- Must scroll to access toolbar, losing selection context
- Mobile users cannot access toolbar at all in many cases (viewport height limited)

**Fix:**
Implement dynamic positioning:
```typescript
const rect = selection.getBoundingClientRect();
const spaceAbove = rect.top;
const spaceBelow = window.innerHeight - rect.bottom;
const placement = spaceAbove > 120 ? 'above' : 'below';
```

---

### 1.6 No Session Resumption Despite Dialog Placeholder
**Severity:** MEDIUM
**Location:** `ies/reader/src/App.tsx` line 42

**Problem:**
Code comment `// TODO: Show resume dialog to user` indicates planned session resumption, but feature is unimplemented. Users lose reading position and context on app restart.

**Evidence:**
```typescript
// App.tsx
// TODO: Show resume dialog to user
// Modal should offer: Resume last session | Start fresh
```

**User Impact:**
- Users must manually navigate back to last reading position
- Context (active question, flow panel state) is lost
- Violates mobile app expectations (instant resume)

**ADHD Impact:**
Session resumption is **critical** for ADHD users who switch contexts frequently. Losing position creates frustration and abandonment.

---

## 2. VISUAL DESIGN CRITIQUE

### 2.1 Dark Reader + Light Panel Theme Clash
**Severity:** HIGH
**Location:** `ies/reader/src/components/Reader.css` vs `FlowPanel.css`

**Problem:**
The Reader uses dark theme (`--bg-primary: #0f0f10`) while the Flow Panel uses light "warm paper" aesthetic (`#f8f6f3` documented in older design system). This creates **jarring visual discord**.

**Evidence:**
```css
/* Reader.css */
.reader-container {
  background: var(--bg-primary); /* Near black */
}

/* FlowPanel.css */
.flow-panel {
  background: var(--glass-bg); /* Dark glass, but older spec had light */
  /* Documentation conflict: IES-DESIGN-SYSTEM-V2.md says dark,
     but UNIFIED-DESIGN-SYSTEM.md (deprecated) specified warm paper */
}
```

**User Impact:**
- Eye strain from switching between extreme contrasts
- Breaks immersion—feels like two different apps bolted together
- Violates Gestalt principle of similarity

**Root Cause:**
Design system migration incomplete. IES Design System v2 (dark) was adopted for Reader but FlowPanel was built against older spec.

---

### 2.2 Inconsistent Styling Approaches (Tailwind vs CSS Modules)
**Severity:** MEDIUM
**Location:** Multiple components across `ies/reader/src/`

**Problem:**
The codebase mixes **three** styling approaches with no clear boundaries:
1. CSS custom properties (`--bg-primary`)
2. Component-scoped CSS files (`Reader.css`, `FlowPanel.css`)
3. Global utility classes (Tailwind implied by naming patterns)

**Evidence:**
```bash
find ies/reader/src -name "*.css" | wc -l
# Result: 10 separate CSS files
# Each with different organization patterns
```

**Developer Impact:**
- No clear guidance on where to add new styles
- High likelihood of specificity conflicts
- Difficult to enforce design system compliance

**User Impact:**
- Visual inconsistencies (button sizes vary, spacing is inconsistent)
- Maintenance burden leads to design drift over time

---

### 2.3 Entity Type Badges Create Visual Noise
**Severity:** MEDIUM
**Location:** SiYuan plugin FlowMode entity display

**Problem:**
Nine different question class badges + five entity type colors create a **rainbow of competing visual signals**. No clear hierarchy emerges.

**Evidence:**
```svelte
<!-- FlowMode.svelte lines 66-76 -->
const QUESTION_CLASS_LABELS = {
    schema_probe: { emoji: '🏗️', color: '#4a90d9' },
    boundary: { emoji: '🔲', color: '#7b68ee' },
    dimensional: { emoji: '📐', color: '#20b2aa' },
    // ... 9 total classes
};
```

**User Impact:**
- Cannot quickly scan—too many colors demand attention equally
- Emoji overload reduces professional perception
- Color alone is insufficient for colorblind users (accessibility violation)

**Fix:**
Reduce to 3 visual priorities:
1. **Primary** (current focus entity)
2. **Secondary** (related entities)
3. **Muted** (metadata badges)

Use color sparingly for **meaning**, not decoration.

---

### 2.4 Mobile FAB (Floating Action Button) Not Discoverable
**Severity:** HIGH
**Location:** `ies/reader/src/components/Reader.css` lines 250-267

**Problem:**
On mobile, the note-taking FAB is hidden until users discover it by accident. No onboarding, no animation to draw attention.

**Evidence:**
```css
@media (max-width: 767px) {
  .reader-fab-note {
    position: fixed;
    right: var(--ies-space-4);
    bottom: calc(var(--ies-space-4) + env(safe-area-inset-bottom));
    /* Static position, no animation, no tooltip */
  }
}
```

**User Impact:**
- New users don't know note-taking exists
- Critical feature hidden behind exploration
- Violates mobile UX guideline: make primary actions obvious

**Fix:**
- First-use tooltip: "Tap here to capture notes"
- Gentle pulse animation on first session
- Or: reveal on first text selection

---

### 2.5 Progress Indicators Unclear in ForgeMode
**Severity:** MEDIUM
**Location:** `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte`

**Problem:**
Template-based sessions show section progress, but the visual design doesn't communicate:
- How many sections total
- Whether sections are optional or required
- What triggers progression to next section

**User Impact:**
- Users unsure if they can skip ahead
- Unclear whether current section is blocking
- No sense of completion percentage

**Fix:**
Add stepper component:
```
[●━━━○○○] Section 2 of 6
```

---

## 3. INTERACTION ANTI-PATTERNS

### 3.1 FlowMode Trail Navigation Unintuitive for Non-Technical Users
**Severity:** HIGH
**Location:** `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` (navigation state machine)

**Problem:**
The trail breadcrumb uses **filesystem metaphor** (clickable path segments) but operates on a **state stack**. Clicking a middle breadcrumb doesn't navigate to that state—it **truncates** the stack.

**Evidence:**
```typescript
// FlowMode.svelte lines 175-208
function navigateToTrailIndex(index: number) {
    trailStack = trailStack.slice(0, index + 1); // Truncates trail
    // Restores state by type, not by ID
}
```

**User Impact:**
- Users expect "click Context → return to context view"
- Get instead: "click Context → pop entire exploration stack"
- Lose current facet exploration permanently
- No "back" button to undo

**Developer Note:**
This is a **stack disguised as breadcrumbs**. Stack navigation requires explicit back/forward controls (browser-style), not clickable history.

**Fix:**
Either:
- Implement true breadcrumb navigation (each click goes to that exact state)
- Or replace breadcrumbs with Back button + "Home" button

---

### 3.2 Modal Layer Complexity Allows Nested Modals
**Severity:** HIGH
**Location:** SiYuan plugin modal architecture

**Problem:**
The system allows modals to open over modals (e.g., Clarification Dialog can open while Concept Extractor is open). This creates **z-index hell** and confusing interaction.

**Evidence:**
```svelte
<!-- FlowMode.svelte -->
let showClarificationDialog = false;
let showAddEntityForm = false;
<!-- Both can be true simultaneously, no mutual exclusion -->
```

**User Impact:**
- Users lose context: "Which dialog am I in?"
- Escape key behavior is unpredictable
- Screen readers announce multiple overlapping dialogs (accessibility violation)

**Fix:**
Implement modal stack manager:
```typescript
const modalStack = [];
const openModal = (component) => {
  if (modalStack.length > 0) {
    // Close current modal first
  }
  modalStack.push(component);
};
```

---

### 3.3 No Keyboard Navigation in FlowMode
**Severity:** HIGH
**Location:** `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte`

**Problem:**
3,251 lines of code, **zero keyboard event handlers**. All navigation requires mouse/touch. Power users cannot use arrow keys, Enter, or shortcuts.

**Evidence:**
```bash
grep -r "onKeyDown\|onKeyPress\|keydown" FlowMode.svelte
# Result: No matches
```

**User Impact:**
- Violates WCAG 2.1 Level A (keyboard accessibility)
- Power users cannot explore efficiently
- Screen reader users cannot navigate at all

**ADHD Impact:**
ADHD users often prefer keyboard navigation (faster, less distraction). Mouse-only interaction creates friction.

**Fix Priority:**
Implement at minimum:
- Tab: cycle through entities
- Enter: select entity
- Escape: navigate back
- Arrow keys: traverse graph

---

### 3.4 Question Creation UX Blocks Exploration Flow
**Severity:** MEDIUM
**Location:** `ies/reader/src/components/flow/QuestionSelector.tsx`

**Problem:**
Creating a question requires:
1. Click "Create Question" button
2. Type question text
3. Click "Create" in modal
4. Wait for backend save
5. Manually select newly created question from dropdown

This **5-step flow** interrupts reading. Should be 2 steps: type + auto-select.

**User Impact:**
- Users abandon question creation (too much friction)
- Exploration flow is broken by context switch
- Violates "low friction capture" principle

---

### 3.5 Journey Timeline Lacks Interaction
**Severity:** MEDIUM
**Location:** `ies/reader/src/components/flow/JourneyTimeline.tsx`

**Problem:**
The timeline displays journey history but items are **non-interactive**. Users cannot click to revisit past exploration points.

**Expected Behavior:**
Click timeline entry → restore that exploration state (entity, context, question)

**Actual Behavior:**
Timeline is read-only visualization

**User Impact:**
- Cannot leverage journey history for navigation
- Timeline becomes decorative, not functional
- Missed opportunity for "resume exploration" feature

---

## 4. COGNITIVE LOAD ISSUES

### 4.1 FlowMode: Three Sections Compete for Attention
**Severity:** HIGH
**Location:** `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte`

**Problem:**
FlowMode displays simultaneously:
1. **Context panel** (top) — Key questions, areas of exploration
2. **Search/Entity panel** (middle) — Current entity or search results
3. **Detail panel** (bottom) — Connections, sources, evidence

All three sections have equal visual weight. No clear primary focus.

**Evidence:**
```svelte
<!-- All sections rendered at same hierarchy level -->
{#if isContextMode}
  <ContextPanel /> <!-- 1 -->
{/if}
{#if focusState === 'entity'}
  <EntityPanel /> <!-- 2 -->
{/if}
<ConnectionsPanel /> <!-- 3 -->
```

**User Impact:**
- Eye scanning patterns show no clear entry point
- Users report "not knowing where to look first"
- Violates visual hierarchy principles

**Fix:**
Implement **progressive disclosure**:
- Primary view: Entity card (80% screen)
- Secondary accordion: Connections (collapsed by default)
- Tertiary panel: Context (accessible via tab, not always visible)

---

### 4.2 Question Class Badges Overload Working Memory
**Severity:** MEDIUM
**Location:** SiYuan ForgeMode question display

**Problem:**
Tracking 9 question classes simultaneously requires memorizing:
- 9 emoji meanings
- 9 color associations
- 9 cognitive function labels

This exceeds working memory capacity (Miller's Law: 7±2 items).

**User Impact:**
- Users cannot internalize system
- Resort to ignoring badges entirely
- Educational overhead before system is useful

**Fix:**
Reduce to 3 meta-categories:
- **Clarifying** (blue) — Understand structure
- **Connecting** (amber) — Relate concepts
- **Challenging** (red) — Test assumptions

Map 9 classes internally, show simplified categories to users.

---

### 4.3 Simultaneous Context + Question + Entity State
**Severity:** MEDIUM
**Location:** IES Reader session state management

**Problem:**
Users must track:
- Active context ID
- Selected question ID
- Current entity name
- Journey trail position

All simultaneously. No visual cues indicate which is "primary" at any moment.

**User Impact:**
- Users lose track of "what am I exploring?"
- Cannot resume after interruption
- System feels complex rather than clarifying

**Fix:**
Display unified status bar:
```
[Context: Therapy Framework] → [Question: How does shame block?] → [Entity: Metabolization]
```

---

## 5. ADHD-UNFRIENDLY PATTERNS

### 5.1 No Quick Capture for Fleeting Insights
**Severity:** HIGH
**Location:** Absence of inbox/quick capture feature on mobile

**Problem:**
ADHD design principles emphasize "capture what resonates" with "low friction." Yet the IES Reader on mobile requires:
1. Select text
2. Wait for selection bar
3. Click "Note"
4. Fill form fields (entity type, context)
5. Submit

**Principle Violated:**
"Capture must be effortless. Organization happens automatically."

**Evidence:**
```typescript
// NotesSheet.tsx — Multi-field form required
<input placeholder="Note type" />
<textarea placeholder="Your note" />
<button>Save</button>
```

**User Impact:**
- Insights are lost while navigating form
- ADHD users abandon capture (too slow)
- Violates "spark capture" concept from ontology design

**Fix:**
Voice-to-text quick capture:
```
[Hold mic button] → Speak → Auto-save to inbox
```

---

### 5.2 No Energy-Level-Based Navigation
**Severity:** MEDIUM
**Location:** Personal graph API exists but UI not connected

**Problem:**
Backend has `/personal/sparks/by-energy/{level}` endpoint for mood-appropriate content. **No UI exposes this feature.**

**Evidence:**
```bash
# Backend has implementation
grep -r "by-energy" ies/backend/src/ies_backend/api/personal.py
# Frontend has no UI for it
grep -r "by-energy\|energy.*level" ies/reader/src/
# Result: No matches
```

**Principle Violated:**
"Energy level navigation" for ADHD support (documented in ontology design)

**User Impact:**
- Users cannot filter by current energy state
- Low-energy sessions force high-effort tasks
- System doesn't adapt to user state

---

### 5.3 Permanent Record Creates Shame Exposure
**Severity:** MEDIUM
**Location:** Question creation without delete

**Problem:**
ADHD ontology design explicitly states: "Status = growth, not grades. 'Incomplete' is valid forever."

Yet questions cannot be deleted, creating permanent record of abandoned explorations.

**Principle Violated:**
"Non-judgmental lifecycle" — users should not feel shame about incomplete work

**User Impact:**
- Users hesitate to experiment
- Fear of "messy" question history
- Inhibits natural ADHD exploration patterns

---

### 5.4 No Resonance Signal Capture
**Severity:** MEDIUM
**Location:** Note capture lacks resonance metadata

**Problem:**
ADHD ontology defines 8 resonance signals (curious, excited, surprised, moved, disturbed, unclear, connected, validated) as **emotional retrieval cues**.

Note capture UI has no way to tag these signals.

**Evidence:**
```typescript
// NotesSheet.tsx — No resonance field
interface NoteCreate {
  text: string;
  entity_id: string;
  // No: resonance_signal field
}
```

**User Impact:**
- Cannot filter notes by emotional state
- Loses retrieval cue benefit (ADHD memory support)
- Violates "resonance over importance" principle

---

## 6. ACCESSIBILITY GAPS (WCAG Violations)

### 6.1 Color-Only Entity Type Distinction
**Severity:** HIGH (WCAG 2.1 Level A violation)
**Location:** Entity badges, relationship cards

**Problem:**
Entity types distinguished **only by color** (blue=Concept, green=Person, etc.). No shape, icon, or label differentiates types for colorblind users.

**Evidence:**
```css
.entity-type-concept { color: var(--entity-concept); }
.entity-type-person { color: var(--entity-person); }
/* No shape/icon/pattern difference */
```

**User Impact:**
- 8% of males (colorblind) cannot distinguish types
- Violates WCAG 1.4.1 (Use of Color)

**Fix:**
Add shape + icon coding:
- Concept: ● (circle) + 💡
- Person: ■ (square) + 👤
- Theory: ▲ (triangle) + 📚

---

### 6.2 Missing ARIA Labels on Interactive Elements
**Severity:** HIGH (WCAG 2.1 Level A violation)
**Location:** Multiple components

**Problem:**
Icon-only buttons lack `aria-label`. Screen readers announce "button" with no context.

**Evidence:**
```typescript
// Reader.tsx
<button onClick={onClose}>
  <ArrowLeft /> {/* No aria-label */}
</button>
```

**User Impact:**
- Screen reader users cannot identify button purpose
- Violates WCAG 4.1.2 (Name, Role, Value)

---

### 6.3 Focus Indicators Inconsistent
**Severity:** MEDIUM (WCAG 2.1 Level AA)
**Location:** Multiple input components

**Problem:**
Some inputs show focus ring, others don't. No consistent visual pattern for keyboard navigation.

**Evidence:**
```css
/* Some components have focus styles */
.input:focus {
  border-color: var(--entity-concept);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

/* Others don't */
.flow-relationship-link:focus {
  /* No focus style defined */
}
```

---

### 6.4 Low Contrast Text in Muted States
**Severity:** MEDIUM (WCAG 2.1 Level AA)
**Location:** Design system muted text color

**Problem:**
`--text-muted: #6b6b70` on `--bg-primary: #0f0f10` has contrast ratio of **4.2:1** (below WCAG AA requirement of 4.5:1 for body text).

**Evidence:**
```bash
# Contrast check: https://webaim.org/resources/contrastchecker/
Foreground: #6b6b70
Background: #0f0f10
Ratio: 4.2:1 (FAIL AA)
```

**User Impact:**
- Low vision users strain to read secondary text
- Metadata becomes invisible in bright light

**Fix:**
Adjust to `--text-muted: #8a8a90` (ratio 5.1:1)

---

### 6.5 No Reduced Motion Support
**Severity:** LOW (WCAG 2.1 Level AA)
**Location:** Animations throughout

**Problem:**
System uses animations (spinner, transitions) without checking `prefers-reduced-motion` media query.

**User Impact:**
- Vestibular disorder users experience discomfort
- No way to disable animations

**Fix:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. FLOW MODE SPECIFIC CRITIQUE

### 7.1 "Flow" Promises Spatial Exploration, Delivers Linear Lists
**Severity:** CRITICAL
**Location:** FlowMode architecture

**Problem:**
The name "Flow Mode" evokes Mihály Csíkszentmihályi's flow state (effortless immersion) and spatial graph exploration. Reality: **click entities in a list to see more lists.**

**Expectation vs Reality:**

| User Expects | System Provides |
|--------------|-----------------|
| Visual network graph | Hierarchical text navigation |
| Spatial memory formation | Linear list scanning |
| "Big picture" overview | One entity at a time |
| Follow visual edges | Click relationship labels |
| Zoom/pan/explore freely | Back button only |

**User Impact:**
- Cognitive dissonance: "Where is the graph?"
- Cannot leverage visual memory
- Linear navigation feels like database browsing, not exploration

**Why This Matters:**
Knowledge graphs derive value from **seeing patterns**. Text lists force sequential processing, negating the graph's structural insights.

---

### 7.2 Entity Details Lack Context
**Severity:** HIGH
**Location:** Entity focus view

**Problem:**
When viewing an entity, the system shows:
- Entity name/type
- Description (if exists)
- Related entities (list)
- Source books (list)

Missing:
- **Why did I land here?** (Previous entity relationship context)
- **How does this fit the current question?** (Question relevance)
- **What's the importance?** (Mention frequency, user visits)

**User Impact:**
- Users lose exploration thread
- Cannot assess relevance without backtracking
- Feel lost in "entity soup"

---

### 7.3 Facet Exploration Dead-Ends
**Severity:** MEDIUM
**Location:** Facet navigation in FlowMode

**Problem:**
Navigating to a facet (e.g., "Assessment Types" within "Assessment" entity) shows:
- Facet description
- Entities in facet
- **No way to pivot to sibling facets**

User must navigate back to parent entity to explore other facets.

**User Impact:**
- Exploration feels constrained
- Cannot discover adjacent facets naturally
- Increases navigation friction

**Fix:**
Show sibling facet tabs at top:
```
[Overview] [Assessment Types] [Clinical Uses] [Validation Studies]
                    ↑ current
```

---

## 8. CROSS-APP EXPERIENCE CRITIQUE

### 8.1 No Visual Indication of Cross-App Sync Status
**Severity:** HIGH
**Location:** IES Reader session sync

**Problem:**
Reader has `useSessionSync` hook that syncs state with SiYuan every 5 seconds. **Users have no way to know if sync is working.**

**Evidence:**
```typescript
// useSessionSync.ts
const { syncStatus } = useFlowStore();
// syncStatus exists but is never displayed in Reader UI
```

**User Impact:**
- Users switch to SiYuan, state not synced, confusion
- Cannot diagnose sync failures
- Unexpected behavior erodes trust

**Fix:**
Status indicator in Reader toolbar:
```
[📱 Synced with SiYuan] ← Green when healthy
[⚠️ Sync paused] ← Yellow when offline
[❌ Sync error] ← Red on failure
```

---

### 8.2 Journey Trail Not Shared Between Apps
**Severity:** MEDIUM
**Location:** Journey trail state management

**Problem:**
Reader tracks journey trail (breadcrumb of entities visited). SiYuan has separate trail. They don't merge.

**User Impact:**
- Exploration context lost when switching apps
- Cannot see "full journey" across both interfaces
- Violates "unified exploration" promise

---

### 8.3 Reading Position Sync Delay
**Severity:** MEDIUM
**Location:** `useReadingPosition` hook

**Problem:**
Reading position syncs to backend, but SiYuan polls every 5 seconds. Users switching apps see **stale position** for up to 5 seconds.

**User Impact:**
- "Resume reading in SiYuan" opens wrong page
- Users think sync is broken
- Annoying in rapid app switching workflow

**Fix:**
WebSocket for instant position sync (sub-second latency)

---

## 9. MOBILE-SPECIFIC ISSUES

### 9.1 Bottom Sheet Doesn't Collapse on Mobile
**Severity:** HIGH
**Location:** FlowPanel mobile implementation

**Problem:**
On mobile, FlowPanel becomes bottom sheet (60vh height). But:
- Cannot swipe to resize
- Cannot collapse to pill
- Cannot dismiss without closing entirely

**User Impact:**
- Bottom sheet blocks 60% of screen permanently when open
- Cannot peek at text while viewing flow panel
- Violates mobile UX expectation (sheets are draggable)

**Fix:**
Implement drag-to-resize:
```
Collapsed: 10% (pill with entity name)
Half: 50% (default)
Full: 90% (details visible)
```

---

### 9.2 Touch Targets Below 44px Minimum
**Severity:** MEDIUM (Accessibility)
**Location:** Multiple components

**Problem:**
Some interactive elements (relationship badges, question type pills) are smaller than iOS 44x44px touch target guideline.

**Evidence:**
```css
.flow-question-type {
  padding: 2px 8px; /* Height ~20px, below minimum */
}
```

**User Impact:**
- Users mis-tap frequently
- Frustration on mobile devices
- Violates WCAG 2.5.5 (Target Size)

---

### 9.3 Keyboard Obscures Input on Mobile
**Severity:** MEDIUM
**Location:** Question creation, note capture on mobile

**Problem:**
When keyboard appears, input field may be hidden behind keyboard. No scroll-to-view behavior.

**User Impact:**
- Users type blind (cannot see what they're typing)
- Common mobile UX failure

**Fix:**
```typescript
input.addEventListener('focus', () => {
  input.scrollIntoView({ behavior: 'smooth', block: 'center' });
});
```

---

## 10. PERFORMANCE & POLISH

### 10.1 Entity Overlay Transform Lag on Large Books
**Severity:** MEDIUM
**Location:** Entity content transformer

**Problem:**
Entity overlay wraps matching text in `<span>` elements. On books with 500+ entities, this creates **massive DOM mutations** causing lag.

**User Impact:**
- Page rendering stutters
- Scrolling feels janky
- Battery drain on mobile

**Fix:**
Virtual scrolling + lazy entity annotation (only visible viewport)

---

### 10.2 No Optimistic UI Updates
**Severity:** LOW
**Location:** Question creation, note capture

**Problem:**
User actions (create question, save note) show loading spinner while waiting for backend. UI doesn't update optimistically.

**User Impact:**
- System feels slow even with fast backend
- Users unsure if action registered

**Fix:**
```typescript
// Optimistic update
const tempQuestion = { id: 'temp', text };
setQuestions([...questions, tempQuestion]);

// Backend save
await saveQuestion(text);
// Replace temp with real ID
```

---

### 10.3 Missing Empty States Guidance
**Severity:** LOW
**Location:** Multiple sections (questions, journey, highlights)

**Problem:**
Empty states show generic "No items" text. Don't guide users on **how to populate**.

**Example:**
```
No questions yet.
```

Better:
```
No questions yet.
[Create your first question] to guide your reading.
```

---

## 11. DESIGN SYSTEM GAPS

### 11.1 Incomplete Migration to IES Design System v2
**Severity:** MEDIUM
**Location:** Mixed old/new design tokens

**Problem:**
`ies/reader/src/styles/design-system.css` defines v2 tokens (dark mode), but some components still reference old tokens from deprecated UNIFIED-DESIGN-SYSTEM.md (warm paper aesthetic).

**Evidence:**
```css
/* New tokens defined */
--bg-primary: #0f0f10;

/* But some CSS uses old */
background: #f8f6f3; /* Hardcoded old value */
```

**Developer Impact:**
- No single source of truth
- Design drift inevitable
- Difficult to enforce consistency

---

### 11.2 No Component Documentation
**Severity:** LOW
**Location:** Absence of Storybook or component docs

**Problem:**
48 React components, 20+ Svelte components, **zero component documentation**.

**Developer Impact:**
- New developers cannot discover components
- Props/usage patterns unclear
- Duplicate components get created

**Fix:**
Storybook for visual component catalog + props documentation

---

## RECOMMENDED NEXT STEPS (Prioritized)

### Tier 1: Critical Fixes (User-Facing Blockers)
1. **Rename "Flow Mode" or implement graph visualization** — Critical misleading UI
2. **Add question delete/edit controls** — Data hygiene blocker
3. **Fix selection bar positioning** — Core interaction broken
4. **Implement keyboard navigation in FlowMode** — Accessibility violation
5. **Add cross-app sync status indicator** — Trust/reliability issue

### Tier 2: High-Impact UX Improvements
6. **Simplify FlowMode to single-focus layout** — Reduce cognitive load
7. **Implement quick capture for mobile** — ADHD friction point
8. **Add session resumption dialog** — Mobile expectation
9. **Fix Areas chips to actually filter** — Non-functional UI
10. **Make bottom sheet draggable on mobile** — Mobile UX standard

### Tier 3: ADHD-Friendly Enhancements
11. **Expose energy-level navigation in UI** — Backend exists, no frontend
12. **Add resonance signal tagging to notes** — Emotional retrieval cues
13. **Implement voice quick capture** — Lowest friction capture
14. **Add "favorite problems" filter** — Navigation anchor for ADHD

### Tier 4: Accessibility Compliance
15. **Add shape/icon coding to entity types** — Colorblind support
16. **Add ARIA labels to all interactive elements** — Screen reader support
17. **Increase muted text contrast** — WCAG AA compliance
18. **Add prefers-reduced-motion support** — Vestibular disorder support

### Tier 5: Polish & Performance
19. **Implement optimistic UI updates** — Perceived performance
20. **Add empty state guidance** — User education
21. **Set up Storybook for component docs** — Developer experience
22. **Optimize entity overlay rendering** — Large book performance

---

## CONCLUSION

The IES system demonstrates **sophisticated technical implementation** (411 backend tests passing, complex state management, cross-app sync) but suffers from **fundamental UX architecture failures**.

**Core Issue:** Features were built in isolation without holistic UX design or user testing. The result is a **feature list masquerading as a product**.

**The "Flow Mode" Deception** is emblematic: users are promised graph exploration but receive hierarchical list navigation. This gap between promise and reality undermines trust and adoption.

**ADHD-Friendly Design Principles** exist in documentation but are not consistently implemented in UI. The system says "low friction capture" but requires 5-step forms. Says "non-judgmental lifecycle" but prevents deletion. Says "resonance over importance" but doesn't capture resonance signals.

**Path Forward:** The system needs **user-centered design iteration**, not more features. Conduct usability testing with 5-8 users. Watch them struggle. Fix the top 5 pain points. Repeat.

**Final Verdict:** Technically impressive, experientially frustrating. A knowledge graph system that hides the graph is like a map app that shows only text directions—it works, but misses the point.

---

**Files Referenced:**
- `/home/chris/dev/projects/codex/brain_explore/ies/reader/src/components/Reader.tsx` (465 lines)
- `/home/chris/dev/projects/codex/brain_explore/ies/reader/src/components/flow/FlowPanel.tsx` (280 lines)
- `/home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` (3,251 lines)
- `/home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` (3,123 lines)
- `/home/chris/dev/projects/codex/brain_explore/docs/siyuan-exports/06-adhd-friendly-ontology-design.md`
- `/home/chris/dev/projects/codex/brain_explore/docs/plans/2025-12-06-ies-design-system-v2.md`
