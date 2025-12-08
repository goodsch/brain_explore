# Flow Interface v2 — Design Brief

**Created:** 2025-12-08
**Status:** Design phase
**Location:** IES Reader (Readest fork)

---

## Vision

A **question-driven research interface** that transforms how users explore their knowledge library. Instead of passive reading, users engage in active exploration guided by questions, AI thinking partnership, and evidence from their book collection.

The interface works as both a **reader companion** (desktop side panel) and **standalone explorer** (mobile full-screen).

---

## Problem Statement

Current Flow panel is reactive — user selects text, sees related entities. But real research is proactive:
- Start with a question
- Explore related concepts
- Find evidence across sources
- Build understanding through connections
- Document discoveries

Users need a way to drive exploration from questions, not just react to text.

---

## Core Concepts

### Question-Driven Exploration

Users start with questions, not books. Questions come from:
- **SiYuan sync** — Favorite questions, projects, Feynman problems
- **Created in Reader** — New questions sparked during exploration
- **AI-suggested** — Thinking partner surfaces related questions

### Hierarchical Structure

```
Question: "How does ADHD affect time perception?"
├── Sub-question: "What role does dopamine play?"
│   ├── Concept: Dopamine
│   ├── Concept: Reward pathways
│   └── Evidence: [3 passages]
├── Sub-question: "What is time blindness?"
│   ├── Concept: Time blindness
│   └── Evidence: [5 passages]
└── Sub-question: "What coping strategies exist?"
    └── Evidence: [2 passages]
```

### Evidence-Centered

Every concept links to source evidence:
- Book title, chapter, page
- Passage text preview
- CFI location for jump-to-reader
- Confidence score

### AI Thinking Partner

Integrated chat that:
- Suggests clarifying questions
- Surfaces unexpected connections
- Tracks the exploration journey
- Documents discoveries

---

## Responsive Dual-Mode

### Desktop: Side Panel Mode

```
┌─────────────────────────────────┬──────────────────────┐
│                                 │                      │
│         READER VIEW             │     FLOW PANEL       │
│                                 │                      │
│   [Book content with            │  [Question tree]     │
│    entity highlights]           │  [Entity cards]      │
│                                 │  [Evidence list]     │
│                                 │  [AI chat]           │
│                                 │                      │
└─────────────────────────────────┴──────────────────────┘
```

- Panel width: 20-50% (resizable)
- Can be pinned or overlay
- Clicking evidence navigates reader to location
- Entity highlights in reader text link to Flow panel

### Mobile: Standalone Mode

```
┌──────────────────────┐
│  ← Back    Flow    ⋮ │
├──────────────────────┤
│                      │
│  [Full-screen        │
│   Flow interface]    │
│                      │
│  [Question nav]      │
│  [Entity cards]      │
│  [Evidence grid]     │
│  [AI chat input]     │
│                      │
└──────────────────────┘
```

- Full viewport width
- Navigation to reader is modal/page transition
- Optimized touch interactions
- Bottom sheet for AI chat

---

## Data Model

### Question
```typescript
interface FlowQuestion {
  id: string;
  text: string;
  source: 'siyuan' | 'reader' | 'ai-suggested';
  siyuanId?: string;  // For sync
  parentId?: string;  // For sub-questions
  status: 'active' | 'paused' | 'resolved';
  createdAt: string;
  updatedAt: string;
}
```

### Exploration Session
```typescript
interface ExplorationSession {
  id: string;
  questionId: string;
  userId: string;
  status: 'active' | 'paused' | 'completed';
  journeyPath: JourneyStep[];
  discoveries: Discovery[];
  aiExchanges: ThinkingPartnerExchange[];
  startedAt: string;
  lastActiveAt: string;
}
```

### Discovery
```typescript
interface Discovery {
  id: string;
  type: 'insight' | 'connection' | 'question' | 'evidence';
  content: string;
  relatedEntities: string[];
  relatedEvidence: string[];
  timestamp: string;
}
```

---

## User Flows

### Flow 1: Start New Exploration

1. Open Flow interface (tab/button)
2. See list of questions (synced + local)
3. Select question or create new
4. System loads related entities and evidence
5. Begin exploration

### Flow 2: Resume Exploration

1. Open Flow interface
2. See "Continue where you left off" section
3. Tap to resume session
4. State restored: current focus, journey breadcrumbs, chat history

### Flow 3: Explore from Reader

1. Reading a book
2. Select text / tap highlighted entity
3. Flow panel shows entity context
4. Can pivot to question-driven exploration from there

### Flow 4: Navigate to Source

1. In Flow, viewing evidence passage
2. Tap "Read in context"
3. Desktop: Reader navigates to CFI location
4. Mobile: Transition to reader view at location

---

## Component Architecture

```
FlowInterface/
├── FlowPage.tsx              # Standalone page wrapper
├── FlowPanel.tsx             # Side panel wrapper (existing, enhanced)
├── components/
│   ├── QuestionNav/
│   │   ├── QuestionList.tsx      # List of questions
│   │   ├── QuestionTree.tsx      # Hierarchical sub-questions
│   │   └── QuestionCreate.tsx    # Create new question
│   ├── EntityExplorer/
│   │   ├── EntityCard.tsx        # Single entity display
│   │   ├── EntityGrid.tsx        # Grid/list of entities
│   │   ├── FacetChips.tsx        # Facet decomposition
│   │   └── RelationshipMap.tsx   # Visual connections
│   ├── EvidenceView/
│   │   ├── EvidenceCard.tsx      # Single passage
│   │   ├── EvidenceGrid.tsx      # Grid of passages
│   │   └── SourceList.tsx        # Books with evidence counts
│   ├── ThinkingPartner/
│   │   ├── ChatThread.tsx        # Conversation history
│   │   ├── ChatInput.tsx         # Message input
│   │   └── SuggestionChips.tsx   # Quick question chips
│   ├── Journey/
│   │   ├── Breadcrumbs.tsx       # Exploration path
│   │   ├── DiscoveryLog.tsx      # Captured insights
│   │   └── SessionStatus.tsx     # Sync/save status
│   └── shared/
│       ├── ResponsiveContainer.tsx
│       └── ModeSwitch.tsx        # Desktop/mobile detection
└── hooks/
    ├── useFlowMode.ts            # Mode management
    ├── useQuestions.ts           # Question CRUD + sync
    ├── useExploration.ts         # Session management
    └── useEvidence.ts            # Evidence fetching
```

---

## API Requirements

### New Endpoints Needed

```
GET  /flow/questions              # List user's questions
POST /flow/questions              # Create question
GET  /flow/questions/:id/tree     # Get question with sub-questions
POST /flow/questions/:id/explore  # Start exploration, get entities + evidence

GET  /flow/sessions/active        # Get active sessions
POST /flow/sessions               # Create session
PUT  /flow/sessions/:id           # Update session state

POST /flow/discoveries            # Save discovery
GET  /flow/discoveries/:sessionId # Get session discoveries
```

### Existing Endpoints Used

```
GET  /graph/entity/:name          # Entity details
GET  /graph/entity/:name/facets   # Facet decomposition
GET  /graph/entity/:name/evidence # Source passages
GET  /sync/sessions               # Cross-app sync
POST /dialogue/exchange           # AI thinking partner
```

---

## Design Requirements

### Visual Design

- **Visual-first**: Hybrid showing entities, relationships, evidence together
- **Information density**: Show enough context without overwhelming
- **Clear hierarchy**: Question → sub-questions → concepts → evidence
- **Touch-friendly**: Large tap targets for mobile
- **Consistent with IES design system**: Glass effects, spacing, typography

### Interaction Design

- **Fluid navigation**: Easy movement between questions, entities, evidence
- **Context preservation**: Never lose track of where you are
- **Quick actions**: Fast ways to save discoveries, ask AI, jump to source
- **Responsive transitions**: Smooth between desktop panel and mobile full-screen

### Accessibility

- Keyboard navigation for all actions
- Screen reader support
- Sufficient color contrast
- Focus indicators

---

## Success Criteria

1. **Question-driven**: Users can start exploration from a question
2. **Evidence-connected**: Every concept shows source passages
3. **AI-integrated**: Thinking partner accessible throughout
4. **Dual-mode**: Works as side panel (desktop) and standalone (mobile)
5. **Resume-able**: Sessions persist and can be continued
6. **SiYuan-synced**: Questions sync bidirectionally

---

## Open Questions for Design Phase

1. **Mobile navigation**: How to handle reader ↔ Flow transitions?
2. **Visual layout**: Canvas vs. structured grid vs. hybrid?
3. **AI chat placement**: Inline, bottom sheet, or dedicated section?
4. **Discovery capture**: How to mark/save insights during exploration?
5. **Question management**: Where does question CRUD UI live?

---

## Design System

| Element | Value |
|---------|-------|
| **Style** | Flat Design + Glassmorphism accents |
| **Primary** | `#3B82F6` (Trust blue) |
| **CTA** | `#F97316` (Orange) |
| **Background** | `#F8FAFC` (Light) / `#0F172A` (Dark) |
| **Text** | `#1E293B` |
| **Border** | `#E2E8F0` |
| **Animations** | 150-300ms transitions |
| **Approach** | Mobile-first responsive |

---

## UI Mockups

### Desktop: Enhanced Side Panel

```
┌─────────────────────────────────────────┬─────────────────────────────┐
│                                         │ Flow                    ≡ × │
│                                         ├─────────────────────────────┤
│                                         │ ┌─────────────────────────┐ │
│          READER CONTENT                 │ │ 🎯 Current Question     │ │
│                                         │ │ "How does ADHD affect   │ │
│   [Book text with                       │ │  time perception?"    ▼ │ │
│    highlighted entities]                │ └─────────────────────────┘ │
│                                         │                             │
│   The relationship between              │ ┌─ Trail ─────────────────┐ │
│   [dopamine] and time perception        │ │ ADHD → Time → Dopamine  │ │
│   has been studied extensively...       │ └─────────────────────────┘ │
│                                         │                             │
│                                         │ ┌─ Concepts ──────────────┐ │
│                                         │ │ ┌───────┐ ┌───────────┐ │ │
│                                         │ │ │Dopamin│ │Time       │ │ │
│                                         │ │ │[★]    │ │Blindness  │ │ │
│                                         │ │ └───────┘ └───────────┘ │ │
│                                         │ │ ┌───────┐ ┌───────────┐ │ │
│                                         │ │ │Execut.│ │Reward     │ │ │
│                                         │ │ │Functio│ │Pathways   │ │ │
│                                         │ │ └───────┘ └───────────┘ │ │
│                                         │ └─────────────────────────┘ │
│                                         │                             │
│                                         │ ┌─ Evidence ──────────────┐ │
│                                         │ │ 📖 Stolen Focus, Ch.3   │ │
│                                         │ │ "Dopamine plays a       │ │
│                                         │ │ crucial role in..."     │ │
│                                         │ │ [Jump to passage →]     │ │
│                                         │ │                         │ │
│                                         │ │ 📖 ADHD 2.0, p.89       │ │
│                                         │ │ "Time blindness is      │ │
│                                         │ │ characterized by..."    │ │
│                                         │ │ [Jump to passage →]     │ │
│                                         │ └─────────────────────────┘ │
│                                         │                             │
│                                         │ ┌─ AI Partner ────────────┐ │
│                                         │ │ 💬 "What aspect of time │ │
│                                         │ │ perception interests    │ │
│                                         │ │ you most?"              │ │
│                                         │ │ ┌─────────────────────┐ │ │
│                                         │ │ │ Type a question...  │ │ │
│                                         │ │ └─────────────────────┘ │ │
│                                         │ └─────────────────────────┘ │
└─────────────────────────────────────────┴─────────────────────────────┘
```

### Mobile: Standalone Explore Tab

```
┌────────────────────────────┐
│ ←  Flow          ⋯  │
├────────────────────────────┤
│ ┌────────────────────────┐ │
│ │ 🎯 How does ADHD affect│ │
│ │    time perception?  ▼ │ │
│ └────────────────────────┘ │
│                            │
│ ADHD → Time → Dopamine     │
│                            │
├────────────────────────────┤
│ Concepts                   │
│ ┌──────────┐ ┌──────────┐ │
│ │ Dopamine │ │ Time     │ │
│ │ ★ 5 refs │ │ Blindness│ │
│ └──────────┘ └──────────┘ │
│ ┌──────────┐ ┌──────────┐ │
│ │ Executive│ │ Reward   │ │
│ │ Function │ │ Pathways │ │
│ └──────────┘ └──────────┘ │
│                            │
├────────────────────────────┤
│ Evidence                   │
│ ┌────────────────────────┐ │
│ │ 📖 Stolen Focus        │ │
│ │ "Dopamine plays a      │ │
│ │ crucial role in..."    │ │
│ │              [Read →]  │ │
│ └────────────────────────┘ │
│ ┌────────────────────────┐ │
│ │ 📖 ADHD 2.0            │ │
│ │ "Time blindness is..." │ │
│ │              [Read →]  │ │
│ └────────────────────────┘ │
│                            │
├────────────────────────────┤
│ ┌────────────────────────┐ │
│ │ 💬 Ask the AI...       │ │
│ └────────────────────────┘ │
├────────────────────────────┤
│ [Questions] [Explore] [Chat] │
└────────────────────────────┘
```

### Mobile: Questions Tab

```
┌────────────────────────────┐
│ ←  Questions       +  │
├────────────────────────────┤
│ Continue Exploring         │
│ ┌────────────────────────┐ │
│ │ 🎯 ADHD & Time         │ │
│ │ Last: 2h ago • 3 steps │ │
│ │ [Resume →]             │ │
│ └────────────────────────┘ │
│                            │
│ My Questions               │
│ ┌────────────────────────┐ │
│ │ Why do I procrastinate │ │
│ │ even on things I want? │ │
│ │ 📚 12 sources          │ │
│ └────────────────────────┘ │
│ ┌────────────────────────┐ │
│ │ How does meditation    │ │
│ │ affect attention?      │ │
│ │ 📚 8 sources           │ │
│ └────────────────────────┘ │
│                            │
│ From SiYuan                │
│ ┌────────────────────────┐ │
│ │ 🔗 Feynman: Time       │ │
│ │    perception models   │ │
│ │ 📚 15 sources          │ │
│ └────────────────────────┘ │
│                            │
├────────────────────────────┤
│ [Questions] [Explore] [Chat] │
└────────────────────────────┘
```

### Mobile: Chat Tab

```
┌────────────────────────────┐
│ ←  AI Partner      ⋯  │
├────────────────────────────┤
│                            │
│        ┌──────────────────┐│
│        │ How does ADHD    ││
│        │ affect my sense  ││
│        │ of time?         ││
│        └──────────────────┘│
│                            │
│┌──────────────────┐        │
││ Great question!  │        │
││ ADHD affects time│        │
││ perception in    │        │
││ several ways:    │        │
││                  │        │
││ 1. Time blindness│        │
││ 2. Hyperfocus    │        │
││                  │        │
││ 📖 See evidence  │        │
│└──────────────────┘        │
│                            │
├────────────────────────────┤
│ ┌────────────────────────┐ │
│ │ Type a question...     │ │
│ └────────────────────────┘ │
├────────────────────────────┤
│ [Questions] [Explore] [Chat] │
└────────────────────────────┘
```

---

## Component Specifications

### QuestionSelector

```typescript
interface QuestionSelectorProps {
  questions: FlowQuestion[];
  currentQuestionId: string | null;
  onSelect: (questionId: string) => void;
  onCreate: (text: string) => void;
  isLoading: boolean;
}

// States: collapsed, expanded, creating
// Behavior: Click→expand, Select→collapse+fire, "+"→creating, Escape→collapse
```

### TrailBreadcrumbs

```typescript
interface TrailBreadcrumbsProps {
  trail: JourneyStep[];
  onNavigate: (stepIndex: number) => void;
  maxVisible?: number; // Default 4
}

// Click breadcrumb → navigate back
// If trail > maxVisible → show "..." with tooltip
```

### ConceptGrid

```typescript
interface ConceptGridProps {
  concepts: ConceptCard[];
  onSelect: (conceptId: string) => void;
  layout: 'grid' | 'chips';
}

interface ConceptCard {
  id: string;
  name: string;
  type: string;
  existsInGraph: boolean;
  evidenceCount: number;
}

// Desktop: 2-col chips | Mobile: 2-col cards
// Badge [★] if existsInGraph
```

### EvidenceList

```typescript
interface EvidenceListProps {
  passages: EvidencePassage[];
  onJumpToSource: (passage: EvidencePassage) => void;
  maxPreviewLength?: number; // Default 120
  isLoading: boolean;
}

// Click card → expand | "Read →" → jump to source
```

### AIPartnerChat

```typescript
interface AIPartnerChatProps {
  exchanges: ThinkingPartnerExchange[];
  onSendMessage: (message: string) => void;
  isThinking: boolean;
  suggestions?: string[];
  position: 'inline' | 'bottom-sheet' | 'full-tab';
}

// Desktop: inline collapsible | Mobile: bottom-sheet or tab
```

---

## Responsive Behavior

### Breakpoints

| Breakpoint | Width | Mode |
|------------|-------|------|
| `sm` | < 640px | Mobile standalone |
| `md` | 640-1024px | Tablet (user choice) |
| `lg` | > 1024px | Desktop side panel |

### Mode Detection Hook

```typescript
const useFlowMode = () => {
  const [mode, setMode] = useState<'panel' | 'standalone'>('panel');

  useEffect(() => {
    const isMobile = window.innerWidth < 640;
    const isTablet = window.innerWidth < 1024;

    if (isMobile) setMode('standalone');
    else if (isTablet) setMode(localStorage.getItem('flowMode') || 'standalone');
    else setMode('panel');
  }, []);

  return { mode, setMode };
};
```

### Layout Differences

| Component | Desktop | Mobile |
|-----------|---------|--------|
| QuestionSelector | Dropdown | Full-width + tab |
| TrailBreadcrumbs | Horizontal, 4 max | Horizontal, 3 max |
| ConceptGrid | 2-col chips | 2-col cards |
| EvidenceList | Compact cards | Full-width cards |
| AIPartnerChat | Collapsible bottom | Tab or sheet |

### Reader ↔ Flow Transitions

```typescript
const handleJumpToSource = (passage: EvidencePassage) => {
  if (mode === 'standalone') {
    // Mobile: Navigate with return context
    router.push({
      pathname: '/reader/[bookId]',
      query: { cfi: passage.location?.cfi, returnTo: 'flow' },
    });
  } else {
    // Desktop: Navigate reader, panel stays
    navigateReaderTo(passage.location?.cfi);
  }
};
```

### Mobile Gestures

| Gesture | Action |
|---------|--------|
| Swipe left on Evidence | Reveal "Read" action |
| Swipe right on Trail | Navigate back |
| Pull down | Refresh data |
| Long press Concept | Quick preview |

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create `useFlowMode` hook for responsive detection
2. Add `FlowPage.tsx` standalone wrapper
3. Extend `FlowPanel.tsx` with new sections
4. Add question state to `flowModeStore.ts`

### Phase 2: Question System
1. Backend: `/flow/questions` endpoints
2. `QuestionSelector` component
3. SiYuan sync integration
4. Question create/edit UI

### Phase 3: Enhanced Exploration
1. `TrailBreadcrumbs` with navigation
2. `ConceptGrid` with facets
3. `EvidenceList` with jump-to-source
4. Mobile tab navigation

### Phase 4: AI Integration
1. `AIPartnerChat` component
2. Bottom sheet for mobile
3. Suggestion chips
4. Discovery logging

### Phase 5: Polish
1. Animations and transitions
2. Gesture support
3. Accessibility audit
4. Performance optimization

---

## Next Steps

1. ✅ Design brief and vision
2. ✅ UI mockups
3. ✅ Component specifications
4. ✅ Responsive behavior
5. → Implementation planning (detailed tasks)
6. → Development in worktree
