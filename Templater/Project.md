---
project: <% tp.file.title %>
status: active
priority: P2
started: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - project
  - type/project
type: project
---

# <% tp.file.title %>

> One-line description of what this project is

## Overview

[2-3 sentences explaining the project's purpose and scope]

## Quick Start

[How to get started with this project]

## Status

See [CONTEXT.md](CONTEXT.md) for current state.

## Structure

```
<% tp.file.title %>/
├── README.md       ← You are here
├── CONTEXT.md      ← Past/Current/Future state
└── tasks/          ← Task breakdown
```

## 🔗 Links

- Repo: 
- Docs: 
- Related: 

---

## ✅ Tasks

```tasks
not done
tags include #<% tp.file.title.toLowerCase().replace(/\s+/g, '-') %>
sort by priority
```
