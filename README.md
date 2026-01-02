# Claude Code Wrapped

```
  ░█████╗░██╗░░░░░░█████╗░██╗░░░██╗██████╗░███████╗
  ██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔══██╗██╔════╝
  ██║░░╚═╝██║░░░░░███████║██║░░░██║██║░░██║█████╗░░
  ██║░░██╗██║░░░░░██╔══██║██║░░░██║██║░░██║██╔══╝░░
  ╚█████╔╝███████╗██║░░██║╚██████╔╝██████╔╝███████╗
  ░╚════╝░╚══════╝╚═╝░░╚═╝░╚═════╝░╚═════╝░╚══════╝

            C O D E   W R A P P E D
                    by Banker.so
```

**Your year with Claude Code, Spotify Wrapped style.** ✨

A beautiful terminal experience that analyzes your local Claude Code conversation history and presents your coding year in a cinematic, Spotify Wrapped-inspired format.

---

## 🚀 Quick Start

**No installation needed** - Just run one of these commands:

```bash
# Using uvx (recommended - Python, no install)
uvx claude-wrapped

# Using npx (Node.js, no install)
npx claude-wrapped

# Or install once and run anytime
pip install claude-wrapped
claude-wrapped
```

The tool launches in **interactive mode** with arrow-key prompts to guide you through all options. Press `Enter` to advance through your personalized stats!

> **☕ Pro tip:** Using Claude Code? Just paste this repo URL (`https://github.com/da-troll/claude-code-wrapped`) into your conversation and ask Claude to install and run it for you. Sit back, sip your coffee, and let Claude handle the setup while you wait for your stats. Meta, right? 😎

---

## ✨ Features

### 📊 Comprehensive Stats
- **Total messages** exchanged with Claude
- **Coding sessions** and project counts
- **Tokens processed** (input, output, cache)
- **Cost estimates** based on official Anthropic pricing
- **Longest coding streak** with start and end dates
- **Current streak** to keep you motivated

### 🎬 Cinematic Experience
- **Dramatic reveals** - Stats appear one at a time, Spotify Wrapped style
- **GitHub-style contribution graph** - Visualize your coding patterns
- **Movie-style credits** - Featuring your top tools, projects, and models
- **Fun facts & insights** - Like "You coded after midnight 47 times"

### 🎭 Personality Types
Based on your coding habits, discover your type:
- 🦉 **Night Owl** - The quiet hours are your sanctuary
- 🔥 **Streak Master** - Consistency is your superpower
- ⚡ **Terminal Warrior** - Command line is your domain
- 🎨 **The Refactorer** - You see beauty in clean code
- 🚀 **Empire Builder** - Building across multiple projects
- 🌙 **Weekend Warrior** - Passion fuels your weekends
- 🎯 **Perfectionist** - Only the best will do
- 💻 **Dedicated Dev** - Steady and reliable

### 📤 Export Options
- **HTML export** - Beautiful web page with interactive graphs
- **Markdown export** - Clean, readable format for sharing
- **JSON export** - Raw data for your own analysis
- **Timestamped filenames** - Never overwrite previous exports

---

## 🎯 Usage

### Two Ways to Use

**🎨 Interactive Mode (Recommended for beginners)**

Simply run the command without any arguments:

```bash
claude-wrapped
```

You'll be guided through beautiful prompts to select:
- ⏳ **Time period** - Current year, specific year, or all-time
- 📤 **Export format** - Terminal only, HTML, Markdown, or JSON
- 🎬 **Animations** - Show dramatic reveals or skip to dashboard
- 📝 **Custom filename** - Optional custom name for exports

No need to remember complex command-line arguments!

**⚡ CLI Mode (For power users & scripts)**

Pass arguments directly for quick access:

```bash
# Full cinematic experience (current year)
claude-wrapped 2025

# Skip animations, go straight to dashboard
claude-wrapped --no-animate

# All-time statistics
claude-wrapped all

# Export to HTML
claude-wrapped --html

# Export to Markdown
claude-wrapped --markdown

# All-time stats with exports
claude-wrapped all --html --markdown

# Export raw data as JSON
claude-wrapped --json
```

### Custom Output Filename

```bash
# Custom filename (without extension)
claude-wrapped --html --output my-wrapped-2025
# Creates: my-wrapped-2025.html

# Default timestamped filenames
claude-wrapped --html
# Creates: claude-wrapped-2025-20260102-1430.html
```

---

## 💾 Including Backup Directories

Have Claude Code backups in Dropbox, external drives, or exported conversations? Include them all:

### Setup

```bash
# 1. Create a .env file
cp .env.example .env

# 2. Edit .env and add your backup locations (comma-separated)
CLAUDE_BACKUP_DIRS=~/Dropbox/claude-backups/.claude,~/exported-chats,/Volumes/backup/.claude

# 3. Run as normal - automatically combines all data
claude-code-wrapped
```

### Supported Directory Structures

The tool auto-detects three different directory layouts:

#### 1. Standard `~/.claude` Structure
```
backup-dir/
├── projects/
│   └── -Users-you-code-project/
│       └── session-uuid.jsonl
└── history.jsonl (optional)
```

#### 2. Projects Folder
```
projects-dir/
├── -Users-you-code-project1/
│   └── session.jsonl
└── -Users-you-code-project2/
    └── session.jsonl
```

#### 3. Flat Structure
```
backup-dir/
├── session1.jsonl
├── session2.jsonl
└── session3.jsonl
```

### Deduplication

- Messages are automatically deduplicated by `message_id`
- **Order matters**: Later directories override earlier ones for duplicates
- List most authoritative/complete sources **last**

**Example:**
```bash
# CORRECT: Pre-compaction backups listed last (highest priority)
CLAUDE_BACKUP_DIRS=~/.claude/backups/old,~/external-drive/pre-compaction

# WRONG: Pre-compaction backups will be overridden
CLAUDE_BACKUP_DIRS=~/external-drive/pre-compaction,~/.claude/backups/old
```

---

## 📋 Requirements

- **Python 3.12+** (with uvx, pipx, or pip)
- **Or Node.js 16+** (for npx)
- **Claude Code installed** (`~/.claude/` directory exists)

---

## 🔒 Privacy

This tool is **100% local and private**:

- ✅ **No network requests** - All data read from local `~/.claude/` directory
- ✅ **No data collection** - Nothing sent to any server
- ✅ **No API keys needed** - Works entirely offline
- ✅ **No secrets exposed** - Only aggregated stats shown, not conversation content
- ✅ **Open source** - Inspect the code yourself

Your conversations never leave your machine.

---

## 🎨 What You'll See

### Dashboard View
```
════════════════════════════════════════════════════════
  CLAUDE CODE WRAPPED 2025
════════════════════════════════════════════════════════

   71,108         263          2.9B           40d
  messages      sessions      tokens      best streak

╭─────────────── Activity · 90 of 365 days ────────────╮
│  Mon ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■     │
│      ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■     │
│  Wed ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■     │
│                                                      │
│                Less ■ ■ ■ ■ ■ More                   │
╰──────────────────────────────────────────────────────╯
```

### Credits Sequence
- 💵 **THE NUMBERS** - Cost breakdown by model, total tokens
- 📅 **TIMELINE** - Journey start, active days, peak coding hour
- 📊 **AVERAGES** - Messages and cost per day/week/month
- 🔥 **LONGEST STREAK** - Your best consecutive coding days with dates
- 💬 **LONGEST CONVERSATION** - Your epic coding session stats
- ⭐ **STARRING** - Your favorite Claude models
- 📁 **PROJECTS** - Top projects by message count

---

## 🛠️ How It Works

Reads your local Claude Code conversation history from `~/.claude/projects/` and aggregates:

- **Message counts** and timestamps
- **Token usage** (input, output, cache reads/writes)
- **Tool usage** (Bash, Read, Edit, Grep, etc.)
- **MCP server usage** (extracted from tool names)
- **Model preferences** (Opus, Sonnet, Haiku)
- **Project activity** (intelligently aggregates common subdirectories)
- **Coding patterns** (hourly distribution, weekday patterns, streaks)
- **Cost estimates** (based on official Anthropic API pricing)

### Intelligent Project Aggregation

The tool recognizes common subdirectories and aggregates them properly:

```python
# Both of these become "my-project":
/Users/you/code/my-project/app
/Users/you/code/my-project/src

# Common subdirectories recognized:
app, src, lib, frontend, backend, api, server, client,
test, tests, public, static, dist, build, etc.
```

---

## 📦 Installation Methods

### 🚀 No Install Required (Recommended)

**uvx** (Python ecosystem - most reliable):
```bash
uvx claude-wrapped
```
- ✅ No installation needed
- ✅ Always runs latest version
- ✅ Isolated environment
- ✅ Requires Python 3.12+ or `uv` installed

**npx** (Node.js ecosystem):
```bash
npx claude-wrapped
```
- ✅ No installation needed
- ✅ Works if you have Node.js 16+
- ⚠️ Wrapper script that calls Python version

### 📥 Install Globally

**pip** (system-wide Python install):
```bash
pip install claude-wrapped
claude-wrapped
```
- Installs `claude-wrapped` command globally
- Requires Python 3.12+

**pipx** (isolated Python install):
```bash
pipx install claude-wrapped
claude-wrapped
```
- ✅ Best of both worlds: installed command + isolated environment
- ✅ Doesn't pollute global Python packages
- Requires `pipx` ([installation guide](https://pipx.pypa.io/stable/installation/))

**Homebrew** (macOS/Linux package manager):
```bash
brew tap da-troll/claude-wrapped
brew install claude-wrapped
```
- ✅ Native macOS/Linux package manager
- ✅ Easy updates with `brew upgrade`
- Tap repository: [homebrew-claude-wrapped](https://github.com/da-troll/homebrew-claude-wrapped)

### 🔧 Development Mode

**From source** (for contributors):
```bash
git clone https://github.com/da-troll/claude-code-wrapped.git
cd claude-code-wrapped
uv sync
uv run python -m claude_code_wrapped
```

**Editable install** (makes `claude-wrapped` command available locally):
```bash
uv pip install -e .
claude-wrapped
```

---

## 🤝 Contributing

Contributions are welcome! This project is open source and community-driven.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/da-troll/claude-code-wrapped.git
cd claude-code-wrapped

# Install dependencies with uv
uv sync

# Run from source
uv run python -m claude_code_wrapped

# Run tests
uv run python -m claude_code_wrapped.reader
uv run python -m claude_code_wrapped.stats
```

---

## 👏 Credits

**Original Creator:** [Mert Deveci](https://x.com/gm_mertd) - Maker of [Banker.so](https://banker.so)

**Fork Maintainer:** [Daniel Tollefsen](https://github.com/da-troll)

### Recent Enhancements
- All-time statistics support
- HTML and Markdown export functionality
- Streak date tracking
- Improved project name aggregation
- Custom backup directory support
- Intelligent deduplication across multiple sources

---

## 📄 License

MIT - see [LICENSE](LICENSE) for details.

---

## ⭐ Show Your Support

If you found this useful, consider:
- Giving it a star on GitHub ⭐
- Sharing your wrapped on social media
- Contributing improvements

---

**Built with ❤️ for the Claude Code community**
