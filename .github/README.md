# .github

This folder contains VS Code Copilot configuration for the multi-agent assistant.

## Structure

- **agents/** — Agent definitions (planner, journal, review, inbox, deepwork)
- **instructions/** — Global assistant instructions
- **skills/** — Domain knowledge files that agents reference

## How It Works

Each agent is defined in a `.agent.md` file with:
- A description and instructions
- Tools it can use (MCP servers, file access)
- Skills it references for domain knowledge

The agents work together to help you plan, reflect, and stay organized.
