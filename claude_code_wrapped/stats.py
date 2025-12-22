"""Aggregate statistics from Claude Code conversation history for Wrapped."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .reader import Message, TokenUsage


@dataclass
class DailyStats:
    """Statistics for a single day."""
    date: datetime
    message_count: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    tokens: TokenUsage = field(default_factory=TokenUsage)
    tool_calls: Counter = field(default_factory=Counter)
    models_used: Counter = field(default_factory=Counter)
    projects: set = field(default_factory=set)
    session_count: int = 0


@dataclass
class WrappedStats:
    """Complete wrapped statistics for a year."""
    year: int

    # Overall counts
    total_messages: int = 0
    total_user_messages: int = 0
    total_assistant_messages: int = 0
    total_sessions: int = 0
    total_projects: int = 0

    # Token usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_creation_tokens: int = 0
    total_cache_read_tokens: int = 0

    # Time patterns
    first_message_date: datetime | None = None
    last_message_date: datetime | None = None
    most_active_day: tuple[datetime, int] | None = None
    most_active_hour: int | None = None
    streak_longest: int = 0
    streak_current: int = 0
    active_days: int = 0

    # Tool usage
    tool_calls: Counter = field(default_factory=Counter)
    top_tools: list[tuple[str, int]] = field(default_factory=list)

    # MCP server usage (extracted from mcp__server__tool format)
    mcp_servers: Counter = field(default_factory=Counter)
    top_mcps: list[tuple[str, int]] = field(default_factory=list)

    # Model usage
    models_used: Counter = field(default_factory=Counter)
    primary_model: str | None = None

    # Projects
    projects: Counter = field(default_factory=Counter)
    top_projects: list[tuple[str, int]] = field(default_factory=list)

    # Daily breakdown
    daily_stats: dict[str, DailyStats] = field(default_factory=dict)

    # Hour distribution (0-23 -> count)
    hourly_distribution: list[int] = field(default_factory=lambda: [0] * 24)

    # Day of week distribution (0=Monday, 6=Sunday)
    weekday_distribution: list[int] = field(default_factory=lambda: [0] * 7)

    # Fun stats
    longest_conversation_tokens: int = 0
    avg_tokens_per_message: float = 0.0

    # Averages (messages)
    avg_messages_per_day: float = 0.0
    avg_messages_per_week: float = 0.0
    avg_messages_per_month: float = 0.0

    # Averages (cost)
    avg_cost_per_day: float = 0.0
    avg_cost_per_week: float = 0.0
    avg_cost_per_month: float = 0.0

    # Code activity (from Edit/Write tools)
    total_edits: int = 0
    total_writes: int = 0
    avg_edits_per_day: float = 0.0
    avg_edits_per_week: float = 0.0

    # Cost tracking (per model)
    model_token_usage: dict[str, dict[str, int]] = field(default_factory=dict)
    estimated_cost: float | None = None
    cost_by_model: dict[str, float] = field(default_factory=dict)

    # Monthly breakdown for cost table
    monthly_costs: dict[str, float] = field(default_factory=dict)  # "YYYY-MM" -> cost
    monthly_tokens: dict[str, dict[str, int]] = field(default_factory=dict)  # "YYYY-MM" -> {input, output, ...}

    # Longest conversation tracking
    longest_conversation_messages: int = 0
    longest_conversation_tokens: int = 0
    longest_conversation_session: str | None = None
    longest_conversation_date: datetime | None = None

    @property
    def total_tokens(self) -> int:
        return (
            self.total_input_tokens +
            self.total_output_tokens +
            self.total_cache_creation_tokens +
            self.total_cache_read_tokens
        )


def extract_project_name(project_path: str | None) -> str:
    """Extract a readable project name from a path."""
    if not project_path:
        return "Unknown"
    # Get the last part of the path
    parts = project_path.rstrip('/').split('/')
    return parts[-1] if parts else "Unknown"


def calculate_streaks(daily_stats: dict[str, DailyStats], year: int) -> tuple[int, int]:
    """Calculate longest and current coding streaks."""
    # Get all active dates in the year
    active_dates = set()
    for date_str, stats in daily_stats.items():
        if stats.message_count > 0:
            try:
                active_dates.add(datetime.strptime(date_str, "%Y-%m-%d").date())
            except ValueError:
                continue

    if not active_dates:
        return 0, 0

    # Sort dates
    sorted_dates = sorted(active_dates)

    # Calculate longest streak
    longest_streak = 1
    current_streak = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1

    # Calculate current streak
    today = datetime.now().date()
    current = 0

    # For past years, current streak is meaningless, so return 0
    # For current year, count back from today
    if year < today.year:
        return longest_streak, 0

    # Start from today for current year
    check_date = today

    while check_date >= datetime(year, 1, 1).date():
        if check_date in active_dates:
            current += 1
            check_date -= timedelta(days=1)
        elif check_date == today:
            # Today doesn't count against streak if we haven't coded yet
            check_date -= timedelta(days=1)
        else:
            break

    return longest_streak, current


def aggregate_stats(messages: list[Message], year: int) -> WrappedStats:
    """Aggregate all messages into wrapped statistics."""
    stats = WrappedStats(year=year)

    if not messages:
        return stats

    # Track unique sessions and projects
    sessions = set()
    projects = Counter()
    daily = defaultdict(lambda: DailyStats(date=datetime.now()))

    # Track monthly token usage for cost breakdown
    monthly_tokens: dict[str, dict[str, int]] = defaultdict(
        lambda: {"input": 0, "output": 0, "cache_create": 0, "cache_read": 0}
    )
    monthly_model_tokens: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"input": 0, "output": 0, "cache_create": 0, "cache_read": 0})
    )

    # Track per-session message counts for longest conversation
    session_messages: dict[str, int] = Counter()
    session_tokens: dict[str, int] = Counter()
    session_first_time: dict[str, datetime] = {}

    # Process each message
    for msg in messages:
        stats.total_messages += 1

        if msg.role == 'user':
            stats.total_user_messages += 1
        else:
            stats.total_assistant_messages += 1

        # Session tracking
        if msg.session_id:
            sessions.add(msg.session_id)
            session_messages[msg.session_id] += 1
            # Track first timestamp for each session
            if msg.session_id not in session_first_time and msg.timestamp:
                session_first_time[msg.session_id] = msg.timestamp

        # Project tracking
        project_name = extract_project_name(msg.project)
        if project_name != "Unknown":
            projects[project_name] += 1

        # Model usage and token tracking
        raw_model = msg.model  # Full model ID for accurate cost calculation
        display_model = None  # Simplified name for display
        if msg.model:
            model_lower = msg.model.lower()
            if 'opus' in model_lower:
                display_model = 'Opus'
            elif 'sonnet' in model_lower:
                display_model = 'Sonnet'
            elif 'haiku' in model_lower:
                display_model = 'Haiku'
            elif msg.model == '<synthetic>':
                display_model = None  # Skip synthetic messages
            else:
                display_model = msg.model

            if display_model:
                stats.models_used[display_model] += 1

        # Token usage (aggregate and per-model with FULL model name for accurate pricing)
        if msg.usage:
            stats.total_input_tokens += msg.usage.input_tokens
            stats.total_output_tokens += msg.usage.output_tokens
            stats.total_cache_creation_tokens += msg.usage.cache_creation_tokens
            stats.total_cache_read_tokens += msg.usage.cache_read_tokens

            # Track per-model token usage for cost calculation (use raw model ID)
            if raw_model and raw_model != '<synthetic>':
                if raw_model not in stats.model_token_usage:
                    stats.model_token_usage[raw_model] = {
                        "input": 0, "output": 0, "cache_create": 0, "cache_read": 0
                    }
                stats.model_token_usage[raw_model]["input"] += msg.usage.input_tokens
                stats.model_token_usage[raw_model]["output"] += msg.usage.output_tokens
                stats.model_token_usage[raw_model]["cache_create"] += msg.usage.cache_creation_tokens
                stats.model_token_usage[raw_model]["cache_read"] += msg.usage.cache_read_tokens

            # Track monthly token usage for cost breakdown
            if msg.timestamp:
                month_key = msg.timestamp.strftime("%Y-%m")
                monthly_tokens[month_key]["input"] += msg.usage.input_tokens
                monthly_tokens[month_key]["output"] += msg.usage.output_tokens
                monthly_tokens[month_key]["cache_create"] += msg.usage.cache_creation_tokens
                monthly_tokens[month_key]["cache_read"] += msg.usage.cache_read_tokens

                # Also track per-model per-month for accurate cost calculation
                if raw_model and raw_model != '<synthetic>':
                    monthly_model_tokens[month_key][raw_model]["input"] += msg.usage.input_tokens
                    monthly_model_tokens[month_key][raw_model]["output"] += msg.usage.output_tokens
                    monthly_model_tokens[month_key][raw_model]["cache_create"] += msg.usage.cache_creation_tokens
                    monthly_model_tokens[month_key][raw_model]["cache_read"] += msg.usage.cache_read_tokens

            # Track per-session tokens for longest conversation
            if msg.session_id:
                session_tokens[msg.session_id] += msg.usage.total_tokens

        # Tool usage (separate MCPs from regular tools)
        for tool in msg.tool_calls:
            if tool.startswith("mcp__"):
                # Extract MCP server name: mcp__servername__toolname -> servername
                parts = tool.split("__")
                if len(parts) >= 2:
                    mcp_server = parts[1]
                    stats.mcp_servers[mcp_server] += 1
            else:
                stats.tool_calls[tool] += 1

        # Time-based stats
        if msg.timestamp:
            # Track first and last
            if stats.first_message_date is None or msg.timestamp < stats.first_message_date:
                stats.first_message_date = msg.timestamp
            if stats.last_message_date is None or msg.timestamp > stats.last_message_date:
                stats.last_message_date = msg.timestamp

            # Hourly distribution
            stats.hourly_distribution[msg.timestamp.hour] += 1

            # Weekday distribution
            stats.weekday_distribution[msg.timestamp.weekday()] += 1

            # Daily stats
            date_str = msg.timestamp.strftime("%Y-%m-%d")
            if date_str not in daily:
                daily[date_str] = DailyStats(date=msg.timestamp)

            daily_stat = daily[date_str]
            daily_stat.message_count += 1
            if msg.role == 'user':
                daily_stat.user_messages += 1
            else:
                daily_stat.assistant_messages += 1

    # Finalize stats
    stats.total_sessions = len(sessions)
    stats.projects = projects
    stats.total_projects = len(projects)
    stats.daily_stats = dict(daily)
    stats.active_days = len([d for d in daily.values() if d.message_count > 0])

    # Most active day
    if daily:
        most_active = max(daily.items(), key=lambda x: x[1].message_count)
        stats.most_active_day = (
            datetime.strptime(most_active[0], "%Y-%m-%d"),
            most_active[1].message_count
        )

    # Most active hour
    if any(stats.hourly_distribution):
        stats.most_active_hour = stats.hourly_distribution.index(max(stats.hourly_distribution))

    # Top tools
    stats.top_tools = stats.tool_calls.most_common(10)

    # Top MCPs
    stats.top_mcps = stats.mcp_servers.most_common(5)

    # Top projects
    stats.top_projects = projects.most_common(5)

    # Primary model
    if stats.models_used:
        stats.primary_model = stats.models_used.most_common(1)[0][0]

    # Streaks
    stats.streak_longest, stats.streak_current = calculate_streaks(daily, year)

    # Calculate estimated cost first (needed for averages)
    from .pricing import calculate_total_cost_by_model
    if stats.model_token_usage:
        stats.estimated_cost, stats.cost_by_model = calculate_total_cost_by_model(
            stats.model_token_usage
        )

    # Calculate monthly costs
    stats.monthly_tokens = dict(monthly_tokens)
    for month_key, model_usage in monthly_model_tokens.items():
        month_cost, _ = calculate_total_cost_by_model(dict(model_usage))
        stats.monthly_costs[month_key] = month_cost

    # Find longest conversation
    if session_messages:
        longest_session = max(session_messages.items(), key=lambda x: x[1])
        stats.longest_conversation_session = longest_session[0]
        stats.longest_conversation_messages = longest_session[1]
        if longest_session[0] in session_tokens:
            stats.longest_conversation_tokens = session_tokens[longest_session[0]]
        if longest_session[0] in session_first_time:
            stats.longest_conversation_date = session_first_time[longest_session[0]]

    # Calculate time periods for averages
    today = datetime.now()
    if year == today.year:
        total_days = (today - datetime(year, 1, 1)).days + 1
    else:
        total_days = 366 if year % 4 == 0 else 365
    total_weeks = max(1, total_days / 7)
    total_months = max(1, total_days / 30.44)  # Average days per month

    # Message averages (over total time period, not just active days)
    if total_days > 0:
        stats.avg_messages_per_day = stats.total_messages / total_days
    stats.avg_messages_per_week = stats.total_messages / total_weeks
    stats.avg_messages_per_month = stats.total_messages / total_months

    # Cost averages
    if stats.estimated_cost is not None and total_days > 0:
        stats.avg_cost_per_day = stats.estimated_cost / total_days
        stats.avg_cost_per_week = stats.estimated_cost / total_weeks
        stats.avg_cost_per_month = stats.estimated_cost / total_months

    # Token averages
    if stats.total_assistant_messages > 0:
        stats.avg_tokens_per_message = stats.total_tokens / stats.total_assistant_messages

    # Code activity from Edit/Write tools
    stats.total_edits = stats.tool_calls.get("Edit", 0)
    stats.total_writes = stats.tool_calls.get("Write", 0)
    total_code_changes = stats.total_edits + stats.total_writes
    if total_days > 0:
        stats.avg_edits_per_day = total_code_changes / total_days
        stats.avg_edits_per_week = total_code_changes / total_weeks

    return stats


def format_tokens(tokens: int) -> str:
    """Format token count for display."""
    if tokens >= 1_000_000_000:
        return f"{tokens / 1_000_000_000:.1f}B"
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    if tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)


if __name__ == "__main__":
    from .reader import load_all_messages, get_claude_dir

    print("Loading messages...")
    messages = load_all_messages(year=2025)
    print(f"Loaded {len(messages)} messages")

    print("\nCalculating stats...")
    stats = aggregate_stats(messages, 2025)

    print(f"\n=== Claude Code Wrapped 2025 ===")
    print(f"Total messages: {stats.total_messages:,}")
    print(f"  User: {stats.total_user_messages:,}")
    print(f"  Assistant: {stats.total_assistant_messages:,}")
    print(f"Total sessions: {stats.total_sessions}")
    print(f"Total projects: {stats.total_projects}")
    print(f"Active days: {stats.active_days}")
    print(f"\nTokens: {format_tokens(stats.total_tokens)}")
    print(f"  Input: {format_tokens(stats.total_input_tokens)}")
    print(f"  Output: {format_tokens(stats.total_output_tokens)}")
    print(f"  Cache created: {format_tokens(stats.total_cache_creation_tokens)}")
    print(f"  Cache read: {format_tokens(stats.total_cache_read_tokens)}")
    print(f"\nPrimary model: {stats.primary_model}")
    print(f"Longest streak: {stats.streak_longest} days")
    print(f"Most active hour: {stats.most_active_hour}:00")
    if stats.most_active_day:
        print(f"Most active day: {stats.most_active_day[0].strftime('%B %d')} ({stats.most_active_day[1]} messages)")
    print(f"\nTop tools: {stats.top_tools[:5]}")
    print(f"Top projects: {stats.top_projects}")
