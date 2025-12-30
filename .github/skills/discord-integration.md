# Discord Integration Skill

> Connect with your Discord servers for communication, community management, and notifications

## Overview

The Discord MCP server allows agents to send and receive messages, manage channels, and interact with your Discord communities directly from the assistant.

---

## Available Tools

### Messaging

| Tool | Description |
|------|-------------|
| `send-message` | Send a message to a Discord channel |
| `read-messages` | Read recent messages from a channel |
| `read-multiple-channels` | Read from multiple channels at once |

### Channel Management

| Tool | Description |
|------|-------------|
| `list-servers` | List all servers the bot is connected to |
| `list-channels` | List all text channels in a server |
| `create-channel` | Create a new text channel |

### Role Management

| Tool | Description |
|------|-------------|
| `list-roles` | List all roles in a server |
| `assign-role` | Assign a role to a user |
| `remove-role` | Remove a role from a user |
| `create-role` | Create a new role |
| `delete-role` | Delete a role |
| `update-role` | Update role properties |

### Member Info

| Tool | Description |
|------|-------------|
| `get-member-count` | Get total members in a server |
| `get-role-member-count` | Get members with a specific role |

---

## Setup Requirements

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the **Bot Token** (keep it secret!)
5. Enable these Privileged Gateway Intents:
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 2. Invite Bot to Your Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`, `applications.commands`
3. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Manage Channels (if creating channels)
   - Manage Roles (if managing roles)
4. Copy the generated URL and open it to invite the bot

### 3. Configure MCP Server

Add to your `.vscode/mcp.json`:

```jsonc
{
  "servers": {
    "discord": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "discord-mcp-mod"],
      "env": {
        "DISCORD_TOKEN": "your-bot-token-here"
      }
    }
  }
}
```

---

## Usage Examples

### Send a Message

```
"Send a message to the general channel saying the meeting starts in 10 minutes"
```

The agent will use `send-message` with:
- `channel`: "general" or channel ID
- `message`: "The meeting starts in 10 minutes"

### Read Recent Messages

```
"What were the last 5 messages in the announcements channel?"
```

The agent will use `read-messages` with:
- `channel`: "announcements"
- `limit`: 5

### Check Server Activity

```
"Summarize what happened in the development channel today"
```

The agent will use `read-messages` to fetch recent history and summarize.

---

## Use Cases for Jointhubs

### Daily Planning
- Check morning messages from team channels
- Send focus status to team ("Deep work until 2pm")
- Review any @mentions or DMs

### Meeting Prep
- Pull context from project channels before meetings
- Send meeting summaries to relevant channels after

### Community Management
- Monitor channels for questions
- Post announcements or updates
- Assign roles for new members

### Notifications
- Send reminders to yourself via DM
- Post daily/weekly review summaries to a personal channel
- Alert channels about schedule changes

---

## Security Considerations

- **Bot Token is Secret**: Never commit it to version control
- **Minimal Permissions**: Only grant permissions the bot needs
- **Message Approval**: The assistant asks before sending messages
- **Channel Access**: Bot can only access channels it has permissions for

---

## Troubleshooting

### Bot not responding
- Check if the bot is online in your Discord server
- Verify the token is correct in `.vscode/mcp.json`
- Ensure required intents are enabled

### Can't read messages
- Enable "Message Content Intent" in Developer Portal
- Check bot has "Read Message History" permission

### Can't manage roles
- Bot's role must be higher than roles it manages
- Enable "Server Members Intent" for member operations

---

## Integration with Agents

The Discord tools are available to all agents. Common patterns:

**Planner Agent**: 
- Send focus status updates
- Check for schedule-related messages

**Journal Agent**:
- Log reflections to a private Discord channel
- Pull conversation context for pattern recognition

**Review Agent**:
- Post weekly summaries to a review channel
- Archive insights for team visibility
