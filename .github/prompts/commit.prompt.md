---
name: commit
description: Generate a conventional commit message for current changes
agent: Tech Lead
tools: ['execute', 'read']
argument-hint: What did you change? (or I'll analyze git diff)
---

# Generate Commit Message

Create a clear, conventional commit message.

## Steps

### 1. Analyze Changes

Run: `git status` and `git diff --stat`

Understand what files changed.

### 2. Determine Scope

Identify the primary scope:
- `log:` — Daily log updates
- `{project}:` — Project-specific changes (fenix, avatar, etc.)
- `agents:` — Agent definition changes
- `skills:` — Skill updates
- `prompts:` — Prompt file changes
- `docs:` — Documentation only
- `fix:` — Bug fixes
- `feat:` — New features

### 3. Generate Message

Format: `{scope}: {description}`

Rules:
- Lowercase
- Present tense ("add" not "added")
- No period at end
- Under 72 characters
- Describe *what* changed, not *how*

Examples:
- `log: daily update 2026-01-20`
- `fenix: add hero section copy`
- `agents: improve planner handoffs`
- `fix: correct daily log template path`

### 4. Present Options

If changes span multiple scopes, offer options:
1. Single commit with primary scope
2. Multiple commits (suggest split)

### 5. Execute (if approved)

Run:
```bash
git add -A
git commit -m "{message}"
```

### 6. Confirm

Show: "✓ Committed: {message}"

If appropriate, ask: "Push to remote?"
