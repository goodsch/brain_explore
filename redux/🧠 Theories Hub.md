# 🧠 Theories Hub

(block_id: THEORIES_HUB)

Welcome to the central hub for all the theories, models, and big ideas I'm developing.  
These are **living frameworks** — long-term thinking structures that evolve as I learn, reflect, explore, and connect ideas across my life and work.

This page acts as:

- a **dashboard** for all existing theories
- a **collector** for related notes
- a **starting point** for Flow Mode
- a **map** for understanding my cognitive architecture

---

# ⭐ Current Core Theories

These are the active, foundational models I’m building.

### 🔶 Entry Point Theory

→ [[Entry Point Theory]]

### 🔶 Movement Creates Meaning

→ [[Movement Creates Meaning]]

### 🔶 Exploration Before Structure

→ [[Exploration Before Structure]]

### 🔶 Relational Insight Model

→ [[Relational Insight Model]]

### 🔶 Time Perception Framework

→ [[Time Perception Framework]]

---

# 🌿 Secondary or Emerging Theories

Ideas that are developing, not yet primary frameworks.

{{query  
  blocks where  
    doc.path contains "Theories"  
    and block.text contains "Theory"  
    and not block.text contains "Entry Point"  
    and not block.text contains "Movement Creates Meaning"  
    and not block.text contains "Exploration Before Structure"  
    and not block.text contains "Relational Insight"  
    and not block.text contains "Time Perception"  
}}

---

# 🌱 Seedlings That Might Become Theories

Ideas that are showing “theory potential.”

{{query  
  blocks where doc.path contains "Seedlings"  
  and (block.text contains "model"  
       or block.text contains "theory"  
       or block.text contains "why"  
       or block.text contains "how")  
}}

---

# 🧩 Concepts Connected to Theories

Related core concepts from the Concepts folder.

{{query  
  blocks where doc.path contains "Concepts"  
  and block.text contains "theory"  
}}

---

# 🔭 Flow Maps Highlighting Theoretical Relationships

Flow maps (clusters) that involve or connect theories.

{{query  
  blocks where  
    doc.path contains "Maps"  
    and block.text contains "Theory"  
}}

---

# 💬 Sessions Where Theories Were Developed

Sessions that contributed meaningfully to theoretical development.

{{query  
  blocks where  
    doc.path contains "Sessions"  
    and (block.text contains "theory"  
         or block.text contains "model"  
         or block.text contains "framework")  
}}

---

# ❓ Open Questions Driving Theory Development

These questions help shape evolving theoretical edges.

{{query  
  blocks where doc.path contains "Questions"  
  and block.text contains "why"  
}}

---

# 🕸 Meta-Structure: How My Theories Connect

(This becomes powerful for Flow Mode.)

- [[Entry Point Theory]]
- ↓ explains
- [[Why Can't I Start From Zero?]]
- ↓ interacts with
- [[Movement Creates Meaning]]
- ↓ supports
- [[Exploration Before Structure]]
- ↓ influences
- [[Flow Mode Architecture]]
- ↓ interacts with
- [[Time Perception Framework]]

 *(AI can expand, visualize, and maintain this map.)*

---

# 📌 How to Add a New Theory

1. Create a new file in `Mind/Theories/`
2. Use the Hard Note Theory Template
3. Add a link to it under **Current Core Theories** or **Emerging Theories**
4. Flow Mode will pick it up automatically
5. AI can enrich and maintain its relationships

---

# 📚 Purpose of This Page

This is the **single, unified place** where my long-term intellectual structures converge.  
It is the parent node for Flow Mode’s theoretical exploration and should always stay simple, clear, and navigable.
