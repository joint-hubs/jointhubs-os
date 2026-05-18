# Contributing to Jointhubs

Thank you for your interest in contributing to Jointhubs! This project aims to create a focus-friendly, multi-agent personal assistant using VS Code Copilot.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Use a clear title and description
- Include steps to reproduce if it's a bug
- Include your VS Code and Copilot extension versions

### Suggesting Agents or Skills

We welcome new agent ideas! Please open an issue with:
- Agent/skill name and purpose
- Target use case
- Example prompts users would use
- What MCP tools it might need

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-agent`)
3. Make your changes
4. Remove or generalize any personal data, local paths, and machine-specific workflow details
5. Test with VS Code Copilot
6. Commit your changes (`git commit -m 'Add amazing agent'`)
7. Push to the branch (`git push origin feature/amazing-agent`)
8. Open a Pull Request

### Public-Safe Checklist

Before you push to your fork or open a PR to upstream, verify:

- no real personal notes, communication logs, reviews, or generated ThoughtMap output are staged
- no absolute local paths such as `C:\Users\...` remain in shared files
- no real names, emails, or client-specific details remain in prompts, examples, or docs unless intentionally public
- personal or machine-specific workflows live in `.github/agents/local/`, `.github/prompts/local/`, `.github/skills/local/`, or `.github/instructions/local/`
- configuration defaults use placeholders or environment variables instead of your own machine setup

## Development Guidelines

### Agent Files (`.github/agents/*.agent.md`)

- Use clear, specific descriptions
- List only necessary tools
- Include example prompts in the agent description
- Reference relevant skills for detailed workflows
- Follow focus-friendly communication patterns

### Skill Folders (`.github/skills/*/SKILL.md`)

- One domain per skill
- Include practical workflows
- Use tables and checklists for clarity
- Provide templates users can copy (as `template.md` in the skill folder)

### Focus-Friendly Principles

All contributions should follow these principles:

- **Maximum 2-3 options** when presenting choices
- **Break tasks into steps** — No walls of text
- **Make recommendations** — Don't just list possibilities
- **One thing at a time** — Avoid multi-part questions
- **Celebrate progress** — Brief acknowledgments matter

## Code of Conduct

Be kind, be helpful, be patient. We're all learning.

## Questions?

Open an issue with the `question` label or start a discussion.
