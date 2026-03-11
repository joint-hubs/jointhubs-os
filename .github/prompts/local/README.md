# Local Prompts

This folder is for private prompts that should stay in your local working copy.

## Git Behavior

- Everything in `.github/prompts/local/` is ignored by git
- This `README.md` stays committed so the convention is visible

## Put Prompts Here When

- The prompt reflects a personal workflow you do not want upstream
- The prompt depends on private notes, tools, or local habits
- The prompt is still experimental and not ready to become part of the shared library

## Naming

Use the standard prompt naming pattern:

- `{name}.prompt.md`

Examples:

- `plan-week.prompt.md`
- `remember.prompt.md`
- `private-review.prompt.md`

## Promotion Rule

If a local prompt becomes stable and broadly useful, move it into `.github/prompts/` and add it to the main prompts README.