# Local Instructions

This folder is for private instructions that should apply only in your local working copy.

## Git Behavior

- Everything in `.github/instructions/local/` is ignored by git
- This `README.md` stays committed so the convention is visible

## Put Instructions Here When

- The rules describe personal preferences you do not want upstream
- The rules depend on local tools, secrets, or machine-specific setup
- The rules are experimental and should not affect the shared repo yet

## Naming

Use the standard instruction naming pattern:

- `{scope}.instructions.md`

Examples:

- `mateusz.instructions.md`
- `local-tools.instructions.md`
- `private-vault.instructions.md`

Each file should still include `applyTo` frontmatter so the rule is scoped correctly.

## Promotion Rule

If a local instruction becomes broadly useful and safe to share, move it into `.github/instructions/` and add it to the main README.