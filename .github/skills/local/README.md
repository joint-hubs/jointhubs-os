# Local Skills

This folder is for private or unstable skills that should not be committed upstream.

## Git Behavior

- Everything in `.github/skills/local/` is ignored by git
- This `README.md` stays committed so the convention is visible

## Put Skills Here When

- The skill contains personal workflows or sensitive context
- The skill is useful only in your local vault or machine setup
- The skill is still being tested and should not become part of the shared library yet

## Structure

Create one folder per skill:

```text
.github/skills/local/{skill-name}/
└── SKILL.md
```

Add templates, examples, or scripts inside that skill folder as needed.

## Promotion Rule

If a local skill becomes reusable and safe to share, move it into `.github/skills/{skill-name}/` and add it to the main README.