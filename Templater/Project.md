---
project: <% tp.file.title %>
status: active
priority: P2
started: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - project
type: project
---

# <% tp.file.title %>

> One-line description of what this project is

## 📌 Status

| Field | Value |
|-------|-------|
| Status | 🟡 Active |
| Priority | P2 |
| Started | <% tp.date.now("YYYY-MM-DD") %> |
| Target | |
| Owner | |

---

## 🎯 Goal
> What does success look like?

## 📋 Key Milestones

- [ ] Milestone 1
- [ ] Milestone 2
- [ ] Milestone 3

## 🔗 Links

- Repo: 
- Docs: 
- Related: 

---

## 📝 Notes

### Latest Updates


### Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

---

## ✅ Tasks

```tasks
not done
tags include #<% tp.file.title.toLowerCase().replace(/\s+/g, '-') %>
sort by priority
```
