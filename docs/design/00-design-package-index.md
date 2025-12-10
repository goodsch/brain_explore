# IES UI/UX Design Package

> Comprehensive design system and interaction blueprint for the Intelligent Exploration System
> Generated: December 9, 2025
> Status: **COMPLETE**

---

## Document Index

| # | Document | Size | Status | Purpose |
|---|----------|------|--------|---------|
| 01 | [Discovery Report](./01-discovery-report.md) | 11KB | ✅ Complete | Component inventory, interaction catalog |
| 02 | [Critical Evaluation](./02-critical-evaluation.md) | 36KB | ✅ Complete | Unbiased UX critique, 30 issues with severity ratings |
| 03 | [Competitive Analysis](./03-competitive-analysis.md) | 47KB | ✅ Complete | 9-tool analysis of spatial navigation patterns |
| 04 | [Design Language Guide](./04-design-language-guide.md) | 37KB | ✅ Complete | Colors, typography, spacing, animations |
| 05 | [Component Library Specs](./05-component-library-specs.md) | 43KB | ✅ Complete | 15 reusable component specifications |
| 06 | [Flow Mode Blueprint](./06-flow-mode-blueprint.md) | 54KB | ✅ Complete | Novel movement-based navigation design |
| 07 | [Implementation Roadmap](./07-implementation-roadmap.md) | 39KB | ✅ Complete | 12-week prioritized implementation plan |
| 08 | [Aesthetic Directions & Component Systems](./08-aesthetic-directions-and-component-systems.md) | 53KB | ✅ Complete | 6 aesthetic options, 4 component system architectures |

**Total Package Size:** ~323KB of design documentation

---

## Executive Summary

### Project Scope

The IES (Intelligent Exploration System) consists of four layers:
1. **Knowledge Graph** - Neo4j with 179 books, 50k+ entities
2. **Backend APIs** - FastAPI serving graph, session, extraction endpoints
3. **SiYuan Plugin** - Processing hub with Dashboard, FlowMode, ForgeMode (~10,377 lines)
4. **IES Reader** - E-book reader with entity overlay and flow panel (~3,500 lines)

### Design Focus Areas

1. **Flow Mode Reimagining** - Transform from card-based lists to true spatial graph navigation
2. **Movement-Based Interaction** - Novel navigation paradigm using physics and gesture
3. **Cross-App Continuity** - Seamless handoff between Reader and SiYuan
4. **ADHD-Friendly Patterns** - Energy-based navigation, low cognitive load
5. **Unified Design System** - Consistent dark theme visual language across all components

---

## Key Findings Summary

### Critical UX Issues Discovered (02-critical-evaluation.md)

**30 Issues Identified:**
| Severity | Count | Examples |
|----------|-------|----------|
| CRITICAL | 6 | Flow Mode has NO graph, questions can't be deleted, entity hooks are stubs |
| HIGH | 12 | Theme mismatch, no keyboard navigation, accessibility violations |
| MEDIUM | 8 | Areas chips non-functional, progress indicators unclear |
| LOW | 4 | No optimistic UI, empty state guidance missing |

**Root Cause:** Features built in isolation without holistic UX design or user testing.

### Competitive Landscape (03-competitive-analysis.md)

**9 Tools Analyzed:**
Roam Research, Obsidian, TheBrain, Kinopio, Scapple, Logseq, Heptabase, Muse, Kosmik

**Three Dominant Paradigms:**
1. **Force-Directed Graphs** (Roam, Obsidian, Logseq) - Auto-discovery, poor scaling
2. **Freeform Canvas** (Kinopio, Scapple, Kosmik) - User control, no discovery
3. **Hybrid Approaches** (TheBrain, Heptabase, Muse) - Best of both worlds

**Top 8 Patterns to Adopt:**
1. Hybrid layout (auto-suggest + manual pin)
2. Radial focus view with animated transitions (TheBrain)
3. Always-visible minimap (Kinopio)
4. Three-layer semantic zoom
5. Gesture-first navigation (Muse)
6. Multi-modal navigation (graph + list + timeline)
7. AI-powered discovery layer
8. Prevent-empty-scroll (Muse)

---

## Design Philosophy

**"Movement Through Knowledge"**

The redesigned system should feel like physically moving through a space of ideas:

| Principle | Implementation |
|-----------|----------------|
| **Spatial Memory** | Pinned entities have stable positions; minimap provides overview |
| **Momentum Navigation** | Gesture-based pan/zoom with inertia and spring physics |
| **Trail Visualization** | Breadcrumb trail rendered spatially on graph |
| **Gravity Wells** | Related concepts attract via force-directed layout |
| **Semantic Zoom** | Three layers: Overview → Navigation → Detail |

---

## Design System Highlights (04-design-language-guide.md)

### Unified Dark Theme
- **Background:** 5 levels from #0a0a0b to #2a2a2e
- **Text:** 5 levels from #f5f5f5 to #4a4a50
- **Accent:** Amber #c9872e for primary actions

### Entity Type Colors
| Type | Color | Icon |
|------|-------|------|
| Concept | #3b82f6 (Blue) | ● Circle |
| Person | #10b981 (Green) | ■ Square |
| Theory | #8b5cf6 (Purple) | ▲ Triangle |
| Framework | #f59e0b (Orange) | ◆ Diamond |
| Assessment | #ef4444 (Red) | ★ Star |

### Animation Principles (ADHD-Friendly)
- Fast by default: 150ms for interactions
- No aggressive motion (soft pulses, not rapid blinks)
- Reduced motion support built-in
- Spring physics for natural feel

---

## Component Library (05-component-library-specs.md)

**15 Reusable Components:**

### Core Components
1. EntityBadge - Type badges (3 sizes, 4 states)
2. EntityCard - Expandable entity display
3. QuestionClassBadge - 9 question classes
4. BreadcrumbTrail - Journey navigation
5. Minimap - Graph overview
6. SearchInput - Debounced search
7. FilterPills - Entity type toggles
8. SyncStatusIndicator - Cross-app sync
9. SelectionBar - Floating actions

### Graph Components
10. GraphNode - Entity visualization
11. GraphEdge - Relationship lines
12. GraphCanvas - Pan/zoom container

### Layout Components
13. FlowPanel - Sidebar/drawer
14. TabBar - Mode switching
15. BottomSheet - Mobile drawer

---

## Flow Mode Blueprint (06-flow-mode-blueprint.md)

### Current State vs Proposed

| Aspect | Current | Proposed |
|--------|---------|----------|
| Visualization | Card lists | Force-directed graph |
| Navigation | Click through lists | Pan/zoom/gesture |
| Focus | None | Radial centered view |
| Overview | None | Always-visible minimap |
| Zoom | None | 3-level semantic zoom |
| Animation | Basic | Spring physics |
| Keyboard | None | Full navigation |

### Visual Architecture
```
┌─────────────────────────────────────────────────────┐
│ Breadcrumbs | Search | Filters | Mode Tabs          │
├─────────────────────────────────────────────────────┤
│  ┌──────┐                                           │
│  │Mini- │   Main Graph Canvas                       │
│  │map   │   (Radial Focus + Force-Directed)         │
│  │      │                                           │
│  └──────┘   [Active Entity Centered]                │
│             [Related Entities in Rings]             │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Detail Panel: Description | Facets | Relationships  │
└─────────────────────────────────────────────────────┘
```

### Performance Targets
- 200+ entities at 60fps
- <500ms entity selection transitions
- WebGL fallback for large graphs

---

## Implementation Roadmap (07-implementation-roadmap.md)

### 12-Week Plan

| Phase | Weeks | Focus | Effort |
|-------|-------|-------|--------|
| 0 | 1 | Quick Wins (10 critical fixes) | 40h |
| 1 | 2 | Design System Foundation | 40h |
| 2 | 3-4 | Flow Mode Core (Graph viz) | 80h |
| 3 | 5-6 | Flow Mode Enhancement | 80h |
| 4 | 7-8 | Component Library | 80h |
| 5 | 9-10 | Mobile & Polish | 80h |
| 6 | 11-12 | AI & Discovery | 80h |

**Total Effort:** 480 hours (1 FTE for 12 weeks)

### Priority Framework

| Priority | Definition | Examples |
|----------|------------|----------|
| P0 | Broken/Misleading | Flow Mode stub, selection bar positioning |
| P1 | Major UX Issues | Question CRUD, keyboard nav, theme mismatch |
| P2 | Quality of Life | Areas chips, FAB discovery |
| P3 | Polish | Optimistic UI, empty states |

---

## Technology Stack

| Component | Current | Proposed | Library |
|-----------|---------|----------|---------|
| IES Reader | React + Zustand | Keep | - |
| SiYuan Plugin | Svelte | Keep | - |
| Graph Viz | None | **Add** | D3.js + d3-force |
| Gestures | None | **Add** | react-use-gesture |
| Animations | CSS | **Upgrade** | Framer Motion |
| Documentation | None | **Add** | Storybook |

---

## Immediate Next Steps

### Week 1 Quick Wins (P0)
1. ☐ Fix selection bar positioning (bounds checking)
2. ☐ Add question delete/edit controls
3. ☐ Complete entity lookup stubs
4. ☐ Add ARIA labels to icon buttons
5. ☐ Add cross-app sync status indicator

### Week 2 Design Foundation
6. ☐ Consolidate design tokens to single source
7. ☐ Apply unified dark theme
8. ☐ Fix contrast ratio issues (text-muted)
9. ☐ Add reduced motion CSS support
10. ☐ Setup Storybook

---

## Success Metrics

### User-Facing
- Graph interaction rate: 60%+ users engage with graph view
- Question creation: 50+ questions per month
- Session duration: 2x increase in Flow Mode time

### Technical
- Test coverage: ≥80%
- Lighthouse performance: ≥90
- WCAG AA compliance: 100%

### Quality
- Critical bugs resolved: <3 days
- User satisfaction (CSAT): ≥4.5/5

---

## Package Validation

### Completeness Check
- [x] Discovery: All components mapped
- [x] Critical Analysis: 30 issues documented with severity
- [x] Competitive Research: 9 tools analyzed
- [x] Design Language: Complete token system
- [x] Components: 15 components specified
- [x] Flow Mode: Novel interaction design
- [x] Roadmap: 12-week actionable plan

### Design Principles Applied
- [x] Modern, clean aesthetic (unified dark theme)
- [x] Movement-based navigation (spatial graph + gestures)
- [x] ADHD-friendly (fast animations, low friction)
- [x] Accessible (WCAG AA compliance targets)
- [x] Cross-app continuity (sync indicators, shared state)

---

*This design package is ready for implementation review and developer handoff.*

*Generated by multi-agent analysis with UI/UX specialized tools*
*Date: December 9, 2025*
