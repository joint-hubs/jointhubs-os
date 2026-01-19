---
name: {skill-name}
description: |
  {One paragraph description of what this skill covers.}
  Use when: "{trigger phrase 1}", "{trigger phrase 2}", "{trigger phrase 3}".
metadata:
  author: {your-name}
  version: "1.0"
---

# {Skill Name}

## Purpose

{One paragraph: What is this skill for? When would an agent reference it?}

## Key Concepts

{Core ideas, terminology, or frameworks}

## {Main Section}

{The primary content — could be a process, reference material, templates, etc.}

## Templates

```markdown
{Any reusable templates relevant to this skill}
```

## Related

- `.github/skills/{related-skill}.md`
- `.github/agents/{agent-that-uses-this}.agent.md`

---

## How to Create Your Own Skill

1. **Copy this template** to: `{skill-name}.md`
2. **Fill in the frontmatter** — name, description with trigger phrases, metadata
3. **Define the purpose** — When would an agent need this?
4. **Add the content** — Keep it focused, reference don't repeat
5. **Update README** — Add to the skills table
6. **Reference from agents** — Add to relevant agent files

### Frontmatter Format

```yaml
---
name: my-skill
description: |
  What this skill is about.
  Use when: "trigger 1", "trigger 2", "trigger 3".
metadata:
  author: your-name
  version: "1.0"
---
```

### Tips

- **Skills are knowledge, not personality** — No quirks or voice
- **Keep it focused** — One skill, one domain
- **Trigger phrases help** — Include common phrases that should invoke this skill
- **Templates are useful** — Reusable patterns save time
- **Link, don't duplicate** — Point to other skills when relevant

### Project-Specific Skills

```
Projects/{project-name}/.github/skills/
└── {project-skill}.md
```

Project skills can define project-specific conventions, APIs, or domain knowledge.
