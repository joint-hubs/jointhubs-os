---
description: 'Break down a complex task into smaller, actionable steps with a structured plan.'
agent: 'planner'
tools: ['search/codebase', 'read']
---

# Task Breakdown

Break down the following task into a structured implementation plan.

## Output Format

```markdown
# Implementation Plan: {Task Title}

## Summary
One paragraph describing the goal and approach.

## Prerequisites
- [ ] What needs to exist before starting
- [ ] Dependencies to install
- [ ] Context to understand

## Tasks

### Phase 1: {Phase Name}
- [ ] Task 1.1: {Specific action}
  - Files: `path/to/file.ts`
  - Details: What exactly to do
- [ ] Task 1.2: {Specific action}

### Phase 2: {Phase Name}
- [ ] Task 2.1: {Specific action}

## Verification
- [ ] How to verify Phase 1 works
- [ ] How to verify Phase 2 works
- [ ] Final integration test

## Risks & Mitigations
- Risk: {What could go wrong}
  - Mitigation: {How to handle it}

## Estimated Effort
- Phase 1: {time estimate}
- Phase 2: {time estimate}
- Total: {total estimate}
```

## Guidelines

1. **Be specific** — Each task should be clear enough to execute without questions
2. **Order matters** — Tasks should be in logical sequence
3. **Include file paths** — Reference specific files when known
4. **Add verification** — How do we know each phase is done?
5. **Surface risks** — What could block progress?

## Task Size

Each task should be:
- Completable in one focused session (15-60 min)
- Testable independently
- Small enough to have clear success criteria

## Example

For "Add user authentication to the API":

```markdown
### Phase 1: Setup
- [ ] Task 1.1: Install auth dependencies
  - Files: `package.json`
  - Details: Add passport, passport-jwt, bcrypt
- [ ] Task 1.2: Create auth config
  - Files: `src/config/auth.ts`
  - Details: JWT secret, expiry, refresh settings

### Phase 2: Implementation
- [ ] Task 2.1: Create User model
  - Files: `src/models/user.ts`
  - Details: id, email, passwordHash, createdAt
```
