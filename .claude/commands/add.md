# Quick Add to Backlog

Quickly capture ideas, features, bugs, or changes without interrupting your flow.

**Usage:** `/add [type]: [description] @[project]`

**Types:** `idea`, `feature`, `bug`, `change`, `question`

**Projects:** `ies`, `framework`, `therapy`, or omit for general

---

## Examples

```
/add feature: Question engine should support follow-up chains @ies
/add idea: Explore polyvagal theory integration @therapy
/add bug: Session context not loading when backend slow @ies
/add change: Refactor profile loading to use cache @framework
/add question: How does window of tolerance relate to capacity?
```

---

## Process

1. Parse the input for type, description, and optional project tag
2. Append to `/backlog.md` with timestamp
3. Confirm with a one-line response

**Format in backlog.md:**
```markdown
- [ ] **[TYPE]** Description text `@project` — *YYYY-MM-DD*
```

**If no type provided:** Default to `idea`

**If no project provided:** Leave project tag off (general backlog item)

---

## Append Entry

Add the new entry to the **top** of the appropriate section in `/backlog.md`.

If the file doesn't exist, create it with this structure:
```markdown
# Backlog

Quick-captured ideas, features, and changes.

## Pending

- [ ] **[TYPE]** Description `@project` — *YYYY-MM-DD*

## Done

<!-- Move completed items here -->
```

---

## Response

Keep it brief — just confirm what was added:

> Added **feature** to backlog: "Question engine should support follow-up chains" @ies

Then return to whatever the user was doing. No follow-up questions.
