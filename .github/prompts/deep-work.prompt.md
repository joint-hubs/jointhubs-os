---
name: deep-work
description: Start a protected focus session with clear scope, ThoughtMap-grounded context, and defined end
agent: Planner
tools: ['read', 'edit', 'todo']
argument-hint: What are you focusing on? (and for how long?)
---

# Deep Work Session

Protected focus time. No distractions, clear scope, defined end. Before starting, surface everything the knowledge base already knows about the subject so the user builds on prior work instead of restarting from zero.

## Steps

### 1. Define the Session

Ask:
- "What's the ONE thing you're working on?"
- "How long do you have?" (default: 90 minutes)

### 2. Ground the session in ThoughtMap (context priming)

Before scoping, spend ~2 minutes surfacing prior context on the subject. This is non-negotiable — it's what makes the session additive instead of repetitive.

**2a. Identify subject anchors**
From the user's input, extract:
- **Entities** (people, projects, orgs, tools) — match against `Second Brain/Operations/thoughtmap-out/entities/_entity-index.md`
- **Topics / themes** — likely candidates for `Second Brain/Operations/thoughtmap-out/topics/<slug>.md`

**2b. Read what already exists (cheapest first)**
1. **Entity notes** for each anchor: `entities/{type}/<slug>.md` — grab Summary, Topic Boundaries (CENTER/EDGES), Area Context, and source files.
2. **Topic notes** for each theme: `topics/<slug>.md` — grab Summary, Related Topics, Representative Fragments.
3. If the subject is a **project** → also read `Second Brain/Projects/<project>/CONTEXT.md` for Past/Current/Future state.
4. Check `REPORT.md` build date — if >7 days old, warn that ThoughtMap may be stale.

**2c. Run the MCP grounding bundle**
For non-trivial sessions, do semantic grounding even if the static notes already look good.

For each primary anchor, run a short MCP bundle:
1. the user's exact phrasing
2. `"<anchor> current status"`
3. `"<anchor> open questions"` or `"<anchor> next step"`

Keep strong hits when possible (`distance < 0.40`) and read the top 1-2 backing source files behind the best results.

**2d. Build a compact context pack**

Turn the routed context + MCP hits into one compact working artifact:

```markdown
## Context Pack

**Prior decisions**:
- [max 3 bullets, each tied to a concrete note/file]

**Open threads**:
- [max 3 bullets]

**Reusable assets**:
- [max 3 bullets: notes, files, prompts, outlines, fragments]

**Freshest relevant source**:
- [1 bullet: date + file + why it matters now]

**Gaps / conflicts**:
- [max 2 bullets; if evidence is weak, say so explicitly]
```

Quality rules:
- every field should be source-backed,
- at least one field should point to a fresh source when possible,
- if there are no strong hits, record that in `Gaps / conflicts` instead of guessing,
- continue the session using this pack, not raw search output.

**2e. Frame the findings for the user**

Present a compact briefing — **max ~15 lines**, no walls of text:

```markdown
## 📍 What you already have on "<subject>"

**Prior decisions**:
- [from the context pack]

**Open threads**:
- [from the context pack]

**Reusable assets**:
- [from the context pack]

**Freshest relevant source**:
- [from the context pack]

**Gaps / conflicts**:
- [from the context pack]
```

**2f. Propose session frames (2-3 options, user picks)**

Based on the briefing and the context pack, offer 2-3 concrete ways to shape the session. Examples:
- "**Extend**: build on the decision from [note] — next logical step is X"
- "**Close a gap**: [open thread] has been sitting 3 weeks; 90 minutes could unblock it"
- "**Synthesize**: 4 related fragments exist but no canonical note — consolidate them"

Let the user pick. Do not auto-select.

### 3. Scope It Down

Once the frame is picked, the task must be:
- **Specific**: Not "work on the project" but "write hero section copy"
- **Achievable**: Can be meaningfully progressed in the time available
- **Clear end**: You'll know when it's done
- **Anchored**: Name the specific file(s) that will be created or updated, and which existing notes to reference

If the task is too big, break it down:
"That's a 4-hour task. For this session, let's focus on [subset]."

### 4. Clear the Decks

Remind:
- Close email, Slack, notifications
- Phone on silent or in another room
- Browser tabs closed (except what's needed)
- "If something urgent comes up, it can wait 90 minutes"

### 5. Log the Start

Add to today's log:
```markdown
HH:MM — 🔒 Deep Work Start
Focus: [task]
Frame: [chosen option from step 2e]
Target: [specific outcome]
Duration: [X] minutes
Priors loaded:
- [[entity or topic note 1]]
- [[entity or topic note 2]]
- [[file to extend or update]]
```

### 6. Set the Container

State clearly:
- "For the next [X] minutes, you're working on [task], building on [primary prior note]."
- "I'll be here if you need to think through something or pull more context."
- "When the time is up, we'll log what happened and link it back."

### 7. During Session

If user asks for something off-topic:
- Gently redirect: "Let's capture that for later. Back to [task]?"
- Or: "Want to add that to today's log and return to it after?"

If user gets stuck on a concept:
- Offer to pull one more specific fragment from ThoughtMap (`search_thoughts` with a narrow query)
- Do not open a second briefing — one fragment, back to work

### 8. Session End

When time is up (or user signals done):
- "Time's up. How did it go?"
- Log the outcome
- Celebrate progress, however small

Add to today's log:
```markdown
HH:MM — 🔓 Deep Work End
Result: [what was accomplished]
Files touched: [[created or updated notes]]
Built on: [prior notes referenced]
Next: [what's next for this task]
```

### 9. Close the loop (knowledge capture)

- If a new note was created, ensure it wikilinks back to the entity/topic notes identified in step 2b — this keeps ThoughtMap's map coherent on next rebuild.
- If a decision was made, note it in the relevant `CONTEXT.md` Decision History or peer note.
- If an open thread was closed, mark it closed in its source note so it stops showing up as "unresolved".
- If a gap remains and warrants a dedicated note, flag it as a Wispr Recording Session candidate for the next daily review.
