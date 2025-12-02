# Review Backlog

View and manage captured ideas, features, bugs, and changes.

**Usage:** `/backlog [filter]`

**Filters:** `all`, `ies`, `framework`, `therapy`, `feature`, `bug`, `idea`, `change`, `question`

---

## Examples

```
/backlog              # Show all pending items
/backlog ies          # Show only @ies items
/backlog feature      # Show only features
/backlog therapy idea # Show therapy ideas
```

---

## Process

1. Read `/backlog.md`
2. Apply any filters (project and/or type)
3. Display pending items in a clean format
4. Show count summary

---

## Display Format

Group by project if showing all, or just list if filtered:

```
## @ies (3 items)
- [ ] **feature** Question engine follow-up chains — Dec 1
- [ ] **bug** Session context slow loading — Dec 1
- [ ] **change** Cache profile loading — Nov 30

## @therapy (2 items)
- [ ] **idea** Polyvagal theory integration — Dec 1
- [ ] **question** Window of tolerance + capacity link — Dec 1

## General (1 item)
- [ ] **idea** Some untagged idea — Nov 29
```

---

## Actions

After showing the list, offer quick actions:

> **Actions:** `done [item]` | `move [item] @project` | `delete [item]` | `clear done`

If user provides an action in the same message, execute it:
- `done 1` — Mark first item complete, move to Done section
- `move 2 @ies` — Add project tag to item 2
- `delete 3` — Remove item 3
- `clear done` — Remove all completed items from Done section

---

## If Empty

> Backlog is empty. Use `/add` to capture ideas.
