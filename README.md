# Claude Code Wrapped

```
  ░█████╗░██╗░░░░░░█████╗░██╗░░░██╗██████╗░███████╗
  ██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔══██╗██╔════╝
  ██║░░╚═╝██║░░░░░███████║██║░░░██║██║░░██║█████╗░░
  ██║░░██╗██║░░░░░██╔══██║██║░░░██║██║░░██║██╔══╝░░
  ╚█████╔╝███████╗██║░░██║╚██████╔╝██████╔╝███████╗
  ░╚════╝░╚══════╝╚═╝░░╚═╝░╚═════╝░╚═════╝░╚══════╝

            C O D E   W R A P P E D   2025
                    by Banker.so
```

Your year with Claude Code, Spotify Wrapped style.

## Installation

```bash
# Using uvx (recommended)
uvx claude-code-wrapped

# Using npx
npx claude-code-wrapped

# Or install via pip
pip install claude-code-wrapped
claude-code-wrapped
```

Press `Enter` to advance through your personalized stats.

## What You'll See

**Dramatic stat reveals** - one at a time, like Spotify Wrapped:
- Total messages exchanged
- Coding sessions
- Tokens processed
- Your longest streak

**GitHub-style contribution graph** - see your coding patterns at a glance

**Your coding personality** - based on your habits:
- 🦉 Night Owl
- 🔥 Streak Master
- ⚡ Terminal Warrior
- 🎨 The Refactorer
- 🚀 Empire Builder
- 🌙 Weekend Warrior
- 🎯 Perfectionist
- 💻 Dedicated Dev

**Fun facts & bloopers** - like "You coded after midnight 47 times"

**Movie-style credits** - featuring your top tools, projects, and models

## Options

```bash
claude-code-wrapped              # Full cinematic experience
claude-code-wrapped --no-animate # Skip to dashboard view
claude-code-wrapped --json       # Export stats as JSON
claude-code-wrapped 2025         # View a specific year
```

## Including Backup Directories

Have Claude Code backups in Dropbox, external drives, or exported conversations? Include them:

```bash
# Create a .env file
cp .env.example .env

# Edit .env and add your backup locations (comma-separated)
CLAUDE_BACKUP_DIRS=~/Dropbox/claude-backups/.claude,~/exported-chats

# Run as normal - automatically combines all data
claude-code-wrapped
```

**Supported directory structures (auto-detected):**
- **Standard**: `backup-dir/projects/[project-folders]/*.jsonl` (has `projects/` subdirectory)
- **Projects folder**: `projects/[project-folders]/*.jsonl` (IS the projects folder)
- **Flat**: `backup-dir/*.jsonl` (JSONL files directly in directory)

**Deduplication:**
- Messages are automatically deduplicated by `message_id`
- **Order matters**: Later directories override earlier ones for duplicates
- List most authoritative/complete sources **last** (e.g., pre-compaction backups)

## Requirements

- Python 3.12+ (with uvx, pipx, or pip)
- Or Node.js 16+ (for npx)
- Claude Code installed (`~/.claude/` directory exists)

## How It Works

Reads your local Claude Code conversation history from `~/.claude/projects/` and aggregates:
- Message counts and timestamps
- Token usage (input, output, cache)
- Tool usage (Bash, Read, Edit, etc.)
- Model preferences (Opus, Sonnet, Haiku)
- Project activity

All data stays local. Nothing is sent anywhere.

## Privacy

This tool is completely local and privacy-focused:

- **No network requests** - All data is read from your local `~/.claude/` directory
- **No data collection** - Nothing is sent to any server
- **No API keys needed** - Works entirely offline
- **No secrets exposed** - Only aggregated stats are shown, not conversation content

## Author

Built by [Mert Deveci](https://x.com/gm_mertd), Maker of [Banker.so](https://banker.so)

## License

MIT - see [LICENSE](LICENSE) for details.
