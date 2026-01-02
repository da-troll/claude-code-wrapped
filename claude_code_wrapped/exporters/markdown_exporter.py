"""Markdown export for Claude Code Wrapped."""

from datetime import datetime, timedelta
from pathlib import Path

from ..stats import WrappedStats, format_tokens
from ..pricing import format_cost
from ..ui import CONTRIB_COLORS, determine_personality, get_fun_facts, simplify_model_name, format_year_display


def export_to_markdown(stats: WrappedStats, year: int | None, output_path: Path) -> None:
    """Export wrapped stats to a nicely formatted Markdown file.

    Args:
        stats: Wrapped statistics dataclass
        year: Year being wrapped
        output_path: Path to output Markdown file
    """
    personality = determine_personality(stats)
    fun_facts = get_fun_facts(stats)

    # Calculate date range
    if year is None:
        # All-time: use first and last message dates
        start_date = stats.first_message_date or datetime.now()
        end_date = stats.last_message_date or datetime.now()
    else:
        start_date = datetime(year, 1, 1)
        today = datetime.now()
        end_date = today if year == today.year else datetime(year, 12, 31)

    # Build Markdown
    markdown = _build_markdown_document(stats, year, personality, fun_facts, start_date, end_date)

    # Write to file
    output_path.write_text(markdown, encoding='utf-8')


def _build_markdown_document(stats: WrappedStats, year: int | None, personality: dict,
                              fun_facts: list, start_date: datetime, end_date: datetime) -> str:
    """Build the complete Markdown document."""

    sections = [
        _build_title_section(year),
        _build_dramatic_reveals(stats, start_date, end_date),
        _build_dashboard(stats, year, personality),
        _build_contribution_graph(stats.daily_stats, year),
        _build_charts(stats),
        _build_tools_and_projects(stats),
        _build_mcp_section(stats),
        _build_monthly_costs(stats),
        _build_fun_facts_section(fun_facts),
        _build_credits(stats, year),
    ]

    return "\n\n".join(filter(None, sections))


def _build_title_section(year: int | None) -> str:
    """Build the title section."""
    year_display = format_year_display(year)
    return f"""# 🎬 CLAUDE CODE WRAPPED
## Your {year_display}

*A year in review · Generated {datetime.now().strftime('%B %d, %Y')}*"""


def _build_dramatic_reveals(stats: WrappedStats, start_date: datetime, end_date: datetime) -> str:
    """Build the dramatic reveal sections."""
    date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

    sections = [
        f"""---

## 📊 Total Messages

**{stats.total_messages:,}** messages

*{date_range}*""",

        f"""---

## 📈 Your Averages

### Messages
- **{stats.avg_messages_per_day:.1f}** per day
- **{stats.avg_messages_per_week:.1f}** per week
- **{stats.avg_messages_per_month:.1f}** per month"""
    ]

    if stats.estimated_cost is not None:
        sections[-1] += f"""

### Cost
- **{format_cost(stats.avg_cost_per_day)}** per day
- **{format_cost(stats.avg_cost_per_week)}** per week
- **{format_cost(stats.avg_cost_per_month)}** per month"""

    sections.append(f"""---

## 🔢 Total Tokens

**{stats.total_tokens:,}** tokens ({format_tokens(stats.total_tokens)})

- Input: {format_tokens(stats.total_input_tokens)}
- Output: {format_tokens(stats.total_output_tokens)}""")

    return "\n\n".join(sections)


def _build_dashboard(stats: WrappedStats, year: int | None, personality: dict) -> str:
    """Build the main dashboard section."""

    year_display = format_year_display(year)
    return f"""---

## 📋 Your {year_display} Dashboard

| Messages | Sessions | Tokens | Streak |
|----------|----------|--------|--------|
| {stats.total_messages:,} | {stats.total_sessions:,} | {format_tokens(stats.total_tokens)} | {stats.streak_longest} days |

### {personality['emoji']} {personality['title']}

*{personality['description']}*"""


def _build_contribution_graph(daily_stats: dict, year: int | None) -> str:
    """Build ASCII contribution graph."""
    if not daily_stats:
        return "### 📅 Activity Graph\n\n*No activity data*"

    # Calculate date range
    if year is None:
        # All-time: use actual date range from daily_stats
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in daily_stats.keys()]
        start_date = min(dates) if dates else datetime.now()
        end_date = max(dates) if dates else datetime.now()
    else:
        start_date = datetime(year, 1, 1)
        today = datetime.now()
        end_date = today if year == today.year else datetime(year, 12, 31)

    # Calculate max count for color scaling
    max_count = max(s.message_count for s in daily_stats.values()) if daily_stats else 1

    # Build weeks grid
    weeks = []
    current = start_date - timedelta(days=start_date.weekday())

    while current <= end_date + timedelta(days=7):
        week = []
        for day in range(7):
            date = current + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")

            if date < start_date or date > end_date:
                week.append(None)
            elif date_str in daily_stats:
                count = daily_stats[date_str].message_count
                level = min(4, 1 + int((count / max_count) * 3)) if count > 0 else 0
                week.append(level)
            else:
                week.append(0)

        weeks.append(week)
        current += timedelta(days=7)

    # Build ASCII graph
    graph = "```\n"
    days_labels = ["Mon", "   ", "Wed", "   ", "Fri", "   ", "   "]

    for row in range(7):
        graph += f"{days_labels[row]} "
        for week in weeks:
            if week[row] is None:
                graph += "  "
            else:
                graph += "■ "
        graph += "\n"

    graph += "\n     Less ■ ■ ■ ■ ■ More\n"
    graph += "```"

    # Activity count
    active_count = len([d for d in daily_stats.values() if d.message_count > 0])
    total_days = (end_date - start_date).days + 1

    return f"""---

## 📅 Activity Graph

*{active_count} of {total_days} days active*

{graph}"""


def _build_charts(stats: WrappedStats) -> str:
    """Build weekday and hourly charts."""

    # Weekday chart
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_weekday = max(stats.weekday_distribution) if stats.weekday_distribution else 1

    weekday_chart = "### Weekday Activity\n\n```\n"
    for i, (day, count) in enumerate(zip(days, stats.weekday_distribution)):
        bar_width = int((count / max_weekday) * 30)
        bar = "█" * bar_width
        weekday_chart += f"{day} {bar} {count:,}\n"
    weekday_chart += "```"

    # Hourly chart
    max_hourly = max(stats.hourly_distribution) if stats.hourly_distribution else 1

    hourly_chart = "### Hourly Activity\n\n```\n"
    for hour, count in enumerate(stats.hourly_distribution):
        if count > 0:
            bar_width = int((count / max_hourly) * 40)
            bar = "█" * bar_width
            hourly_chart += f"{hour:02d}:00 {bar} {count:,}\n"
    hourly_chart += "```"

    return f"""---

## 📊 Activity Patterns

{weekday_chart}

{hourly_chart}"""


def _build_tools_and_projects(stats: WrappedStats) -> str:
    """Build tools and projects sections."""

    sections = []

    # Top Tools
    if stats.top_tools:
        max_tool = stats.top_tools[0][1]
        tools_md = "### 🔧 Top Tools\n\n```\n"
        for tool, count in stats.top_tools[:5]:
            bar_width = int((count / max_tool) * 30)
            bar = "█" * bar_width
            tools_md += f"{tool:<20} {bar} {count:,}\n"
        tools_md += "```"
        sections.append(tools_md)

    # Top Projects
    if stats.top_projects:
        max_proj = stats.top_projects[0][1]
        projects_md = "### 📁 Top Projects\n\n```\n"
        for proj, count in stats.top_projects[:5]:
            bar_width = int((count / max_proj) * 30)
            bar = "█" * bar_width
            # Truncate long names
            display_name = proj if len(proj) <= 20 else proj[:17] + "..."
            projects_md += f"{display_name:<20} {bar} {count:,}\n"
        projects_md += "```"
        sections.append(projects_md)

    if sections:
        return "---\n\n## 🛠️  Tools & Projects\n\n" + "\n\n".join(sections)

    return ""


def _build_mcp_section(stats: WrappedStats) -> str:
    """Build MCP servers section if any."""
    if not stats.top_mcps:
        return ""

    max_mcp = stats.top_mcps[0][1]

    mcp_md = "```\n"
    for mcp, count in stats.top_mcps[:3]:
        bar_width = int((count / max_mcp) * 30)
        bar = "█" * bar_width
        mcp_md += f"{mcp:<20} {bar} {count:,}\n"
    mcp_md += "```"

    return f"""---

## 🔌 MCP Servers

{mcp_md}"""


def _build_monthly_costs(stats: WrappedStats) -> str:
    """Build monthly cost breakdown table."""
    if not stats.monthly_costs:
        return ""

    # Build table
    table = "| Month | Input | Output | Cache | Cost |\n"
    table += "|-------|-------|--------|-------|------|\n"

    total_cost = 0
    total_input = 0
    total_output = 0
    total_cache = 0

    for month_str in sorted(stats.monthly_costs.keys()):
        cost = stats.monthly_costs[month_str]
        total_cost += cost

        # Get tokens for this month
        if month_str in stats.monthly_tokens:
            tokens = stats.monthly_tokens[month_str]
            input_tokens = tokens.get('input', 0)
            output_tokens = tokens.get('output', 0)
            cache_tokens = tokens.get('cache_create', 0) + tokens.get('cache_read', 0)

            total_input += input_tokens
            total_output += output_tokens
            total_cache += cache_tokens

            # Format month
            month_date = datetime.strptime(month_str, "%Y-%m")
            month_label = month_date.strftime("%b %Y")

            table += f"| {month_label} | {format_tokens(input_tokens)} | {format_tokens(output_tokens)} | {format_tokens(cache_tokens)} | {format_cost(cost)} |\n"

    table += f"| **Total** | **{format_tokens(total_input)}** | **{format_tokens(total_output)}** | **{format_tokens(total_cache)}** | **{format_cost(total_cost)}** |\n"

    return f"""---

## 💰 Monthly Cost Breakdown

{table}"""


def _build_fun_facts_section(fun_facts: list) -> str:
    """Build fun facts section."""
    if not fun_facts:
        return ""

    facts_md = "\n".join([f"- {emoji} {fact}" for emoji, fact in fun_facts])

    return f"""---

## 💡 Insights

{facts_md}"""


def _build_credits(stats: WrappedStats, year: int | None) -> str:
    """Build credits section."""

    # Aggregate costs by simplified model name
    display_costs = {}
    for model, cost in stats.cost_by_model.items():
        display_name = simplify_model_name(model)
        display_costs[display_name] = display_costs.get(display_name, 0) + cost

    sections = []

    # The Numbers
    numbers = "### 💵 THE NUMBERS\n\n"
    if stats.estimated_cost is not None:
        numbers += f"**Estimated Cost:** {format_cost(stats.estimated_cost)}\n\n"
        for model, cost in sorted(display_costs.items(), key=lambda x: -x[1]):
            numbers += f"- {model}: {format_cost(cost)}\n"
        numbers += "\n"

    numbers += f"**Tokens:** {format_tokens(stats.total_tokens)}\n\n"
    numbers += f"- Input: {format_tokens(stats.total_input_tokens)}\n"
    numbers += f"- Output: {format_tokens(stats.total_output_tokens)}\n"
    sections.append(numbers)

    # Timeline
    today = datetime.now()
    if year is None:
        # All-time: calculate days from first to last message
        if stats.first_message_date and stats.last_message_date:
            total_days = (stats.last_message_date - stats.first_message_date).days + 1
        else:
            total_days = stats.active_days
    elif year == today.year:
        total_days = (today - datetime(year, 1, 1)).days + 1
    else:
        total_days = 366 if year % 4 == 0 else 365

    year_display = format_year_display(year)
    # Use sentence case for "All time" in Period field
    period_text = "All time" if year is None else year_display
    timeline = "### 📅 TIMELINE\n\n"
    timeline += f"- **Period:** {period_text}\n"
    if stats.first_message_date:
        date_str = stats.first_message_date.strftime('%B %d, %Y') if year is None else stats.first_message_date.strftime('%B %d')
        timeline += f"- **Journey started:** {date_str}\n"
    timeline += f"- **Active days:** {stats.active_days} of {total_days}\n"
    if stats.most_active_hour is not None:
        hour_label = "AM" if stats.most_active_hour < 12 else "PM"
        hour_12 = stats.most_active_hour % 12 or 12
        timeline += f"- **Peak hour:** {hour_12}:00 {hour_label}\n"
    sections.append(timeline)

    # Averages
    averages = "### 📊 AVERAGES\n\n"
    averages += "**Messages:**\n"
    averages += f"- Per day: {stats.avg_messages_per_day:.1f}\n"
    averages += f"- Per week: {stats.avg_messages_per_week:.1f}\n"
    averages += f"- Per month: {stats.avg_messages_per_month:.1f}\n"

    if stats.estimated_cost is not None:
        averages += "\n**Cost:**\n"
        averages += f"- Per day: {format_cost(stats.avg_cost_per_day)}\n"
        averages += f"- Per week: {format_cost(stats.avg_cost_per_week)}\n"
        averages += f"- Per month: {format_cost(stats.avg_cost_per_month)}\n"
    sections.append(averages)

    # Longest Streak (if significant)
    if stats.streak_longest >= 3 and stats.streak_longest_start and stats.streak_longest_end:
        streak = "### 🔥 LONGEST STREAK\n\n"
        streak += f"- **{stats.streak_longest} days** of consistent coding\n"
        streak += f"- **From:** {stats.streak_longest_start.strftime('%B %d, %Y')}\n"
        streak += f"- **To:** {stats.streak_longest_end.strftime('%B %d, %Y')}\n"
        streak += "\n*Consistency is the key to mastery.*"
        sections.append(streak)

    # Longest Conversation
    if stats.longest_conversation_messages > 0:
        longest = "### 💬 LONGEST CONVERSATION\n\n"
        longest += f"- **Messages:** {stats.longest_conversation_messages:,}\n"
        if stats.longest_conversation_tokens > 0:
            longest += f"- **Tokens:** {format_tokens(stats.longest_conversation_tokens)}\n"
        if stats.longest_conversation_date:
            longest += f"- **Date:** {stats.longest_conversation_date.strftime('%B %d, %Y')}\n"
        longest += "\n*That's one epic coding session!*"
        sections.append(longest)

    # Starring (Models)
    starring = "### ⭐ STARRING\n\n"
    for model, count in stats.models_used.most_common(3):
        starring += f"- **Claude {model}** ({count:,} messages)\n"
    sections.append(starring)

    # Projects
    if stats.top_projects:
        projects = "### 📁 PROJECTS\n\n"
        for proj, count in stats.top_projects[:5]:
            projects += f"- **{proj}** ({count:,} messages)\n"
        sections.append(projects)

    # Final card
    if year is not None:
        final = f"""---

## 👋 See you in {year + 1}

*Presented by [Banker.so](https://banker.so)*"""
    else:
        final = """---

## 👋 Keep coding!

*Presented by [Banker.so](https://banker.so)*"""
    sections.append(final)

    return "---\n\n## 🎬 CREDITS\n\n" + "\n\n".join(sections)
