# Local Agents

This folder is for agents that should stay local to your machine or private fork.

## Git Behavior

- Everything in `.github/agents/local/` is ignored by git
- This `README.md` stays committed so the folder and convention are visible

## Put Agents Here When

- The agent encodes your personal voice or judgment
- The agent depends on private notes, clients, or sensitive context
- The agent is still experimental and not ready to share

## Naming

Use the same naming convention as shared agents:

- `{name}.agent.md`

Examples:

- `mateusz-work.agent.md`
- `private-client.agent.md`
- `experiment-sprint.agent.md`

## Promotion Rule

If a local agent becomes stable, reusable, and safe to publish, move it into `.github/agents/` and add it to the main README.