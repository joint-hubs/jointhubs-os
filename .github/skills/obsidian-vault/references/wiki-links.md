# Wiki Links Reference

Obsidian linking conventions for connecting notes.

## Basic Syntax

| Syntax | Result |
|--------|--------|
| `[[Note Name]]` | Link to note by name |
| `[[folder/Note]]` | Link with path |
| `[[Note\|Display Text]]` | Custom display text |
| `[[Note#Heading]]` | Link to heading |
| `[[Note#^blockid]]` | Link to block |

## Common Link Patterns

### Daily Notes
```markdown
[[2026-01-20]]                    # Today's note
[[2026-01-19]]                    # Yesterday
```

### Weekly Notes
```markdown
[[2026-W03]]                      # This week
[[2026-W03#Next]]                 # Embed weekly priorities
```

### Project Context
```markdown
[[Second Brain/Projects/my-app/CONTEXT]]
[[my-app/CONTEXT|My App Context]]   # With alias
```

### Cross-References
```markdown
See [[training-log]] for workout history.
Discussed in [[2026-01-20#Meeting Notes]].
```

## Embeds

Embed content from other notes:

```markdown
![[2026-W03#Next]]                # Embed weekly priorities in daily
![[training-log#Recent PRs]]      # Embed a section
![[image.png]]                    # Embed image
```

## Block References

Reference specific paragraphs:

```markdown
# In source note
This is important. ^important-block

# In another note
See [[Source Note#^important-block]]
```

## Best Practices

1. **Use relative paths** when possible
2. **Add display text** for clarity: `[[CONTEXT|Project Status]]`
3. **Embed weekly #Next** in daily notes for focus
4. **Link liberally** — connections are valuable
5. **Use heading links** to point to specific sections
