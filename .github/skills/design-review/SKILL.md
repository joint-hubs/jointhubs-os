---
name: design-review
description: |
  Design review checklists, accessibility standards, and UX patterns.
  Use when: "review design", "check accessibility", "design critique", "UX audit"
---

# Design Review Skill

Checklists and standards for reviewing interfaces.

---

## Quick Audit

Before deep review, answer:
1. **Who** is the user?
2. **What** must this screen accomplish?
3. **Where** does the eye go first?

---

## Visual Hierarchy Checklist

- [ ] Primary action immediately obvious
- [ ] Information flows top→bottom, left→right
- [ ] Size, color, weight create clear importance
- [ ] Related elements grouped, unrelated separated
- [ ] Visual noise minimized

---

## Spacing & Layout

| Rule | Standard |
|------|----------|
| Base unit | 8px grid |
| Touch targets | 44px minimum |
| Breathing room | Adequate around interactive elements |
| Grouping | Related = close, unrelated = far |

---

## Typography Checklist

- [ ] Maximum 2-3 font families
- [ ] Clear size hierarchy (headings > body > captions)
- [ ] Line height 1.4-1.6 for body text
- [ ] Line length 50-75 characters
- [ ] Font weights intentional (not random)

---

## Color & Contrast

| Standard | Requirement |
|----------|-------------|
| WCAG AA text | 4.5:1 contrast ratio minimum |
| WCAG AA large text | 3:1 contrast ratio |
| Color meaning | Consistent (red=danger, green=success) |
| Accessibility | Color not the only indicator |

---

## Interaction States

Every interactive element needs:

| State | Purpose |
|-------|---------|
| Default | Normal appearance |
| Hover | Desktop feedback |
| Focus | Keyboard navigation (accessibility) |
| Active/Pressed | Click feedback |
| Disabled | Unavailable + explanation why |
| Loading | Processing feedback |
| Error | What went wrong + how to fix |

---

## Responsiveness

- [ ] Mobile-first consideration
- [ ] Critical actions accessible on all breakpoints
- [ ] No horizontal scrolling on mobile
- [ ] Touch targets adequate on small screens
- [ ] Text readable without zooming

---

## UX Red Flags

| Issue | Problem |
|-------|---------|
| Unlabeled icons | Users shouldn't guess |
| Walls of text | Nobody reads blocks |
| Disabled without explanation | User deserves to know why |
| Inconsistent patterns | Breaks learned behavior |
| No loading states | User doesn't know if action worked |
| Hostile error messages | "Error 500" tells nothing |
| Buried primary actions | Hidden in dropdowns/menus |
| Modal overuse | Every modal is an interruption |

---

## Animation Guidelines

| Rule | Standard |
|------|----------|
| Duration | Under 300ms for micro-interactions |
| Easing | Natural curves (ease-out for enters, ease-in for exits) |
| Purpose | Guides attention, not decoration |
| Reduce motion | Respect `prefers-reduced-motion` |

---

## Accessibility Quick Check

1. **Keyboard** — Can navigate with Tab? Focus visible?
2. **Screen reader** — Labels on inputs? Alt on images?
3. **Contrast** — Text readable? Colors distinguishable?
4. **Motion** — Reduced motion respected?
5. **Forms** — Errors announced? Labels associated?

---

## Design System References

<!-- CUSTOMIZE: Add your project's design resources -->
| Resource | Location |
|----------|----------|
| Design System | `Second Brain/Projects/{project}/design-system.md` |
| Brand Guide | Project-specific brand documentation |

---

*"Every interface is a conversation. Make it feel human."*
