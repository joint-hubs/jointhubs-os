---
name: design-review
description: Review an interface design for UX issues, accessibility, and polish
agent: designer
tools: ['execute', 'read', 'edit', 'search', 'web', 'github/*', 'todo']
argument-hint: Share a URL, screenshot, or describe what to review
---

# Design Review

Critical eye on interfaces. Find what's broken before users do.

## Steps

### 1. Get the Design

Options:
- URL → Take snapshot/screenshot
- Screenshot shared → Analyze it
- Description → Ask clarifying questions
- File reference → Read the component code

### 2. First Impression (3 seconds)

What does the eye see first? Is it the right thing?

Note:
- Visual hierarchy
- Primary action visibility
- Cognitive load

### 3. Systematic Review

Check each category:

#### Layout & Spacing
- [ ] Consistent spacing rhythm
- [ ] Proper alignment (nothing floating)
- [ ] Breathing room (not cramped)
- [ ] Responsive considerations

#### Typography
- [ ] Clear hierarchy (H1 > H2 > body)
- [ ] Readable sizes (min 16px body)
- [ ] Appropriate line height
- [ ] Contrast (text on background)

#### Color & Contrast
- [ ] Meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Consistent color usage
- [ ] Not relying on color alone

#### Interaction
- [ ] Clear clickable elements
- [ ] Visible focus states
- [ ] Loading states exist
- [ ] Error states defined

#### Copy & Labels
- [ ] Clear, action-oriented CTAs
- [ ] Helpful labels (not just icons)
- [ ] Error messages are helpful
- [ ] No jargon

### 4. Prioritize Issues

Categorize findings:
- 🔴 **Critical**: Blocks users or accessibility fail
- 🟡 **Important**: Causes confusion or friction
- 🟢 **Polish**: Nice-to-have improvements

### 5. Deliver Feedback

Format:
```markdown
## Design Review: {Component/Page}

### 🔴 Critical
- Issue 1: [description] → [fix]

### 🟡 Important  
- Issue 2: [description] → [fix]

### 🟢 Polish
- Issue 3: [description] → [fix]

### What's Working
- Positive 1
- Positive 2
```

### 6. Handoff

Ask: "Want me to create tasks for these issues?"

Or: "Ready to implement fixes?" → handoff to Tech Lead
