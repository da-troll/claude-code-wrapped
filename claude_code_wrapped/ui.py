"""Rich-based terminal UI for Claude Code Wrapped."""

import sys
import time
from datetime import datetime, timedelta

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from .stats import WrappedStats, format_tokens

# Minimal color palette
COLORS = {
    "orange": "#E67E22",
    "purple": "#9B59B6",
    "blue": "#3498DB",
    "green": "#27AE60",
    "white": "#ECF0F1",
    "gray": "#7F8C8D",
    "dark": "#2C3E50",
}

# GitHub-style contribution colors (light to dark green)
CONTRIB_COLORS = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]


def wait_for_keypress():
    """Wait for user to press Enter or Space."""
    try:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            # Also handle escape sequences for special keys
            if ch == '\x1b':
                sys.stdin.read(2)  # consume rest of escape sequence
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (ImportError, AttributeError, OSError):
        # Fallback for non-Unix systems (Windows) or piped input
        input()
        return '\n'


def create_dramatic_stat(value: str, label: str, subtitle: str = "", color: str = COLORS["orange"]) -> Text:
    """Create a dramatic full-screen stat reveal."""
    text = Text()
    text.append("\n\n\n\n\n")
    text.append(f"{value}\n", style=Style(color=color, bold=True))
    text.append(f"{label}\n\n", style=Style(color=COLORS["white"], bold=True))
    if subtitle:
        text.append(subtitle, style=Style(color=COLORS["gray"]))
    text.append("\n\n\n\n")
    text.append("press [ENTER] to continue", style=Style(color=COLORS["dark"]))
    return text


def create_title_slide(year: int) -> Text:
    """Create the opening title."""
    title = Text()
    title.append("\n\n\n")
    title.append("  ░█████╗░██╗░░░░░░█████╗░██╗░░░██╗██████╗░███████╗\n", style=COLORS["orange"])
    title.append("  ██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔══██╗██╔════╝\n", style=COLORS["orange"])
    title.append("  ██║░░╚═╝██║░░░░░███████║██║░░░██║██║░░██║█████╗░░\n", style=COLORS["orange"])
    title.append("  ██║░░██╗██║░░░░░██╔══██║██║░░░██║██║░░██║██╔══╝░░\n", style=COLORS["orange"])
    title.append("  ╚█████╔╝███████╗██║░░██║╚██████╔╝██████╔╝███████╗\n", style=COLORS["orange"])
    title.append("  ░╚════╝░╚══════╝╚═╝░░╚═╝░╚═════╝░╚═════╝░╚══════╝\n", style=COLORS["orange"])
    title.append("\n")
    title.append("              C O D E   W R A P P E D\n", style=Style(color=COLORS["white"], bold=True))
    title.append(f"                     {year}\n\n", style=Style(color=COLORS["purple"], bold=True))
    title.append("                  by ", style=Style(color=COLORS["gray"]))
    title.append("Banker.so", style=Style(color=COLORS["blue"], bold=True, link="https://banker.so"))
    title.append("\n\n\n")
    title.append("            press [ENTER] to begin", style=Style(color=COLORS["dark"]))
    title.append("\n\n")
    return title


def create_big_stat(value: str, label: str, color: str = COLORS["orange"]) -> Text:
    """Create a big statistic display."""
    text = Text()
    text.append(f"{value}\n", style=Style(color=color, bold=True))
    text.append(label, style=Style(color=COLORS["gray"]))
    return text


def create_contribution_graph(daily_stats: dict, year: int) -> Panel:
    """Create a GitHub-style contribution graph for the full year."""
    if not daily_stats:
        return Panel("No activity data", title="Activity", border_style=COLORS["gray"])

    # Always show full year: Jan 1 to Dec 31 (or today if current year)
    start_date = datetime(year, 1, 1)
    today = datetime.now()
    if year == today.year:
        end_date = today
    else:
        end_date = datetime(year, 12, 31)

    max_count = max(s.message_count for s in daily_stats.values()) if daily_stats else 1

    weeks = []
    current = start_date - timedelta(days=start_date.weekday())

    while current <= end_date + timedelta(days=7):
        week = []
        for day in range(7):
            date = current + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            if date_str in daily_stats:
                count = daily_stats[date_str].message_count
                level = min(4, 1 + int((count / max_count) * 3)) if count > 0 else 0
            else:
                level = 0
            week.append(level)
        weeks.append(week)
        current += timedelta(days=7)

    graph = Text()
    days_labels = ["Mon", "   ", "Wed", "   ", "Fri", "   ", "   "]

    for row in range(7):
        graph.append(f"{days_labels[row]} ", style=Style(color=COLORS["gray"]))
        for week in weeks:
            color = CONTRIB_COLORS[week[row]]
            graph.append("■ ", style=Style(color=color))
        graph.append("\n")

    legend = Text()
    legend.append("\n     Less ", style=Style(color=COLORS["gray"]))
    for color in CONTRIB_COLORS:
        legend.append("■ ", style=Style(color=color))
    legend.append("More", style=Style(color=COLORS["gray"]))

    content = Group(graph, Align.center(legend))

    # Calculate total days for context
    today = datetime.now()
    if year == today.year:
        total_days = (today - datetime(year, 1, 1)).days + 1
    else:
        total_days = 366 if year % 4 == 0 else 365
    active_count = len([d for d in daily_stats.values() if d.message_count > 0])

    return Panel(
        Align.center(content),
        title=f"Activity · {active_count} of {total_days} days",
        border_style=Style(color=COLORS["green"]),
        padding=(0, 2),
    )


def create_hour_chart(distribution: list[int]) -> Panel:
    """Create a clean hourly distribution chart."""
    max_val = max(distribution) if any(distribution) else 1
    chars = "▁▂▃▄▅▆▇█"

    content = Text()
    for i, val in enumerate(distribution):
        idx = int((val / max_val) * (len(chars) - 1)) if max_val > 0 else 0
        if 6 <= i < 12:
            color = COLORS["orange"]
        elif 12 <= i < 18:
            color = COLORS["blue"]
        elif 18 <= i < 22:
            color = COLORS["purple"]
        else:
            color = COLORS["gray"]
        content.append(chars[idx], style=Style(color=color))

    content.append("\n")
    content.append("0  6  12  18  24", style=Style(color=COLORS["gray"]))

    return Panel(
        Align.center(content),
        title="Hours",
        border_style=Style(color=COLORS["purple"]),
        padding=(0, 1),
    )


def create_weekday_chart(distribution: list[int]) -> Panel:
    """Create a clean weekday distribution chart."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_val = max(distribution) if any(distribution) else 1

    content = Text()
    for i, (day, count) in enumerate(zip(days, distribution)):
        bar_len = int((count / max_val) * 12) if max_val > 0 else 0
        bar = "█" * bar_len + "░" * (12 - bar_len)
        content.append(f"{day} ", style=Style(color=COLORS["gray"]))
        content.append(bar, style=Style(color=COLORS["blue"]))
        content.append(f" {count:,}\n", style=Style(color=COLORS["gray"]))

    return Panel(
        content,
        title="Days",
        border_style=Style(color=COLORS["blue"]),
        padding=(0, 1),
    )


def create_top_list(items: list[tuple[str, int]], title: str, color: str) -> Panel:
    """Create a clean top items list."""
    content = Text()
    max_val = max(v for _, v in items) if items else 1

    for i, (name, count) in enumerate(items[:5], 1):
        content.append(f"{i}. ", style=Style(color=COLORS["gray"]))
        content.append(f"{name[:12]:<12} ", style=Style(color=COLORS["white"]))
        bar_len = int((count / max_val) * 8)
        content.append("▓" * bar_len, style=Style(color=color))
        content.append("░" * (8 - bar_len), style=Style(color=COLORS["dark"]))
        content.append(f" {count:,}\n", style=Style(color=COLORS["gray"]))

    return Panel(
        content,
        title=title,
        border_style=Style(color=color),
        padding=(0, 1),
    )


def create_personality_card(stats: WrappedStats) -> Panel:
    """Create the personality card."""
    personality = determine_personality(stats)

    content = Text()
    content.append(f"\n  {personality['emoji']}  ", style=Style(bold=True))
    content.append(f"{personality['title']}\n\n", style=Style(color=COLORS["purple"], bold=True))
    content.append(f"  {personality['description']}\n", style=Style(color=COLORS["gray"]))

    return Panel(
        content,
        title="Your Type",
        border_style=Style(color=COLORS["purple"]),
        padding=(0, 1),
    )


def determine_personality(stats: WrappedStats) -> dict:
    """Determine user's coding personality based on stats."""
    night_hours = sum(stats.hourly_distribution[22:]) + sum(stats.hourly_distribution[:6])
    day_hours = sum(stats.hourly_distribution[6:22])
    top_tool = stats.top_tools[0][0] if stats.top_tools else None
    weekend_msgs = stats.weekday_distribution[5] + stats.weekday_distribution[6]
    weekday_msgs = sum(stats.weekday_distribution[:5])

    if night_hours > day_hours * 0.4:
        return {"emoji": "🦉", "title": "Night Owl", "description": "The quiet hours are your sanctuary."}
    elif stats.streak_longest >= 14:
        return {"emoji": "🔥", "title": "Streak Master", "description": f"{stats.streak_longest} days. Unstoppable."}
    elif top_tool == "Edit":
        return {"emoji": "🎨", "title": "The Refactorer", "description": "You see beauty in clean code."}
    elif top_tool == "Bash":
        return {"emoji": "⚡", "title": "Terminal Warrior", "description": "Command line is your domain."}
    elif stats.total_projects >= 5:
        return {"emoji": "🚀", "title": "Empire Builder", "description": f"{stats.total_projects} projects. Legend."}
    elif weekend_msgs > weekday_msgs * 0.5:
        return {"emoji": "🌙", "title": "Weekend Warrior", "description": "Passion fuels your weekends."}
    elif stats.models_used.get("Opus", 0) > stats.models_used.get("Sonnet", 0):
        return {"emoji": "🎯", "title": "Perfectionist", "description": "Only the best will do."}
    else:
        return {"emoji": "💻", "title": "Dedicated Dev", "description": "Steady and reliable."}


def get_fun_facts(stats: WrappedStats) -> list[tuple[str, str]]:
    """Generate fun facts / bloopers based on stats."""
    facts = []

    # Late night coding
    late_night = sum(stats.hourly_distribution[0:5])
    if late_night > 100:
        facts.append(("🌙", f"You coded after midnight {late_night:,} times. Sleep is overrated."))

    # Most active day insight
    if stats.most_active_day:
        day_name = stats.most_active_day[0].strftime("%A")
        facts.append(("📅", f"Your biggest day was a {day_name}. {stats.most_active_day[1]:,} messages. Epic."))

    # Tool obsession
    if stats.top_tools:
        top_tool, count = stats.top_tools[0]
        facts.append(("🔧", f"You used {top_tool} {count:,} times. It's basically muscle memory now."))

    # If they use Opus a lot
    opus_count = stats.models_used.get("Opus", 0)
    if opus_count > 1000:
        facts.append(("🎭", f"You summoned Opus {opus_count:,} times. Only the best for you."))

    # Streak fact
    if stats.streak_longest >= 7:
        facts.append(("🔥", f"Your {stats.streak_longest}-day streak was legendary. Consistency wins."))

    # Multi-project
    if stats.total_projects >= 3:
        facts.append(("🏗️", f"You juggled {stats.total_projects} projects. Multitasking champion."))

    # Token usage perspective
    if stats.total_tokens > 1_000_000_000:
        books = stats.total_tokens // 100_000  # ~100k tokens per book
        facts.append(("📚", f"You processed enough tokens for ~{books:,} books. Wow."))

    # Weekend warrior
    weekend = stats.weekday_distribution[5] + stats.weekday_distribution[6]
    if weekend > 1000:
        facts.append(("🏖️", f"Even weekends weren't safe. {weekend:,} weekend messages."))

    return facts[:5]  # Limit to 5 facts


def create_fun_facts_slide(facts: list[tuple[str, str]]) -> Text:
    """Create a fun facts slide."""
    text = Text()
    text.append("\n\n")
    text.append("  B L O O P E R S  &  F U N  F A C T S\n\n", style=Style(color=COLORS["purple"], bold=True))

    for emoji, fact in facts:
        text.append(f"    {emoji}  ", style=Style(bold=True))
        text.append(f"{fact}\n\n", style=Style(color=COLORS["white"]))

    text.append("\n")
    text.append("    press [ENTER] for credits", style=Style(color=COLORS["dark"]))
    text.append("\n")
    return text


def simplify_model_name(model: str) -> str:
    """Simplify a full model ID to a display name."""
    model_lower = model.lower()
    if 'opus-4-5' in model_lower or 'opus-4.5' in model_lower:
        return 'Opus 4.5'
    elif 'opus-4-1' in model_lower or 'opus-4.1' in model_lower:
        return 'Opus 4.1'
    elif 'opus' in model_lower:
        return 'Opus'
    elif 'sonnet-4-5' in model_lower or 'sonnet-4.5' in model_lower:
        return 'Sonnet 4.5'
    elif 'sonnet' in model_lower:
        return 'Sonnet'
    elif 'haiku-4-5' in model_lower or 'haiku-4.5' in model_lower:
        return 'Haiku 4.5'
    elif 'haiku' in model_lower:
        return 'Haiku'
    return model


def create_credits_roll(stats: WrappedStats) -> list[Text]:
    """Create end credits content."""
    from .pricing import format_cost

    frames = []

    # Aggregate costs by simplified model name for display
    display_costs: dict[str, float] = {}
    for model, cost in stats.cost_by_model.items():
        display_name = simplify_model_name(model)
        display_costs[display_name] = display_costs.get(display_name, 0) + cost

    # Frame 1: The Numbers (cost + tokens)
    numbers = Text()
    numbers.append("\n\n\n")
    numbers.append("              T H E   N U M B E R S\n\n", style=Style(color=COLORS["green"], bold=True))
    if stats.estimated_cost is not None:
        numbers.append(f"              Estimated Cost  ", style=Style(color=COLORS["white"], bold=True))
        numbers.append(f"{format_cost(stats.estimated_cost)}\n", style=Style(color=COLORS["green"], bold=True))
        for model, cost in sorted(display_costs.items(), key=lambda x: -x[1]):
            numbers.append(f"                {model}: {format_cost(cost)}\n", style=Style(color=COLORS["gray"]))
    numbers.append(f"\n              Tokens  ", style=Style(color=COLORS["white"], bold=True))
    numbers.append(f"{format_tokens(stats.total_tokens)}\n", style=Style(color=COLORS["orange"], bold=True))
    numbers.append(f"                Input: {format_tokens(stats.total_input_tokens)}\n", style=Style(color=COLORS["gray"]))
    numbers.append(f"                Output: {format_tokens(stats.total_output_tokens)}\n", style=Style(color=COLORS["gray"]))
    numbers.append("\n\n")
    numbers.append("    [ENTER]", style=Style(color=COLORS["dark"]))
    frames.append(numbers)

    # Frame 2: Timeline (full year context)
    timeline = Text()
    timeline.append("\n\n\n")
    timeline.append("              T I M E L I N E\n\n", style=Style(color=COLORS["orange"], bold=True))
    timeline.append("              Year           ", style=Style(color=COLORS["white"], bold=True))
    timeline.append(f"{stats.year}\n", style=Style(color=COLORS["orange"], bold=True))
    if stats.first_message_date:
        timeline.append("              Journey started ", style=Style(color=COLORS["white"], bold=True))
        timeline.append(f"{stats.first_message_date.strftime('%B %d')}\n", style=Style(color=COLORS["gray"]))
    # Calculate total days in year (up to today if current year)
    today = datetime.now()
    if stats.year == today.year:
        total_days = (today - datetime(stats.year, 1, 1)).days + 1
    else:
        total_days = 366 if stats.year % 4 == 0 else 365
    timeline.append(f"\n              Active days    ", style=Style(color=COLORS["white"], bold=True))
    timeline.append(f"{stats.active_days}", style=Style(color=COLORS["orange"], bold=True))
    timeline.append(f" of {total_days}\n", style=Style(color=COLORS["gray"]))
    if stats.most_active_hour is not None:
        hour_label = "AM" if stats.most_active_hour < 12 else "PM"
        hour_12 = stats.most_active_hour % 12 or 12
        timeline.append(f"              Peak hour      ", style=Style(color=COLORS["white"], bold=True))
        timeline.append(f"{hour_12}:00 {hour_label}\n", style=Style(color=COLORS["purple"], bold=True))
    timeline.append("\n\n")
    timeline.append("    [ENTER]", style=Style(color=COLORS["dark"]))
    frames.append(timeline)

    # Frame 3: Cast (models)
    cast = Text()
    cast.append("\n\n\n")
    cast.append("              S T A R R I N G\n\n", style=Style(color=COLORS["purple"], bold=True))
    for model, count in stats.models_used.most_common(3):
        cast.append(f"              Claude {model}", style=Style(color=COLORS["white"], bold=True))
        cast.append(f"  ({count:,} messages)\n", style=Style(color=COLORS["gray"]))
    cast.append("\n\n\n")
    cast.append("    [ENTER]", style=Style(color=COLORS["dark"]))
    frames.append(cast)

    # Frame 4: Projects
    if stats.top_projects:
        projects = Text()
        projects.append("\n\n\n")
        projects.append("              P R O J E C T S\n\n", style=Style(color=COLORS["blue"], bold=True))
        for proj, count in stats.top_projects[:5]:
            projects.append(f"              {proj}", style=Style(color=COLORS["white"], bold=True))
            projects.append(f"  ({count:,} messages)\n", style=Style(color=COLORS["gray"]))
        projects.append("\n\n\n")
        projects.append("    [ENTER]", style=Style(color=COLORS["dark"]))
        frames.append(projects)

    # Frame 5: Final card
    final = Text()
    final.append("\n\n\n\n")
    final.append("              See you in ", style=Style(color=COLORS["gray"]))
    final.append(f"{stats.year + 1}", style=Style(color=COLORS["orange"], bold=True))
    final.append("\n\n\n\n", style=Style(color=COLORS["gray"]))
    final.append("              ", style=Style())
    final.append("Banker.so", style=Style(color=COLORS["blue"], bold=True, link="https://banker.so"))
    final.append(" presents\n\n", style=Style(color=COLORS["gray"]))
    final.append("    [ENTER] to exit", style=Style(color=COLORS["dark"]))
    frames.append(final)

    return frames


def render_wrapped(stats: WrappedStats, console: Console | None = None, animate: bool = True):
    """Render the complete wrapped experience."""
    if console is None:
        console = Console()

    # === CINEMATIC MODE ===
    if animate:
        # Loading
        console.clear()
        with Progress(
            SpinnerColumn(style=COLORS["orange"]),
            TextColumn("[bold]Unwrapping your year...[/bold]"),
            BarColumn(complete_style=COLORS["orange"], finished_style=COLORS["green"]),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("", total=100)
            for _ in range(100):
                time.sleep(0.012)
                progress.update(task, advance=1)

        console.clear()

        # Title slide - wait for keypress
        console.print(Align.center(create_title_slide(stats.year)))
        wait_for_keypress()
        console.clear()

        # Dramatic stat reveals
        slides = [
            (f"{stats.total_messages:,}", "MESSAGES", "conversations with Claude", COLORS["orange"]),
            (str(stats.total_sessions), "SESSIONS", "coding adventures", COLORS["purple"]),
            (format_tokens(stats.total_tokens), "TOKENS", "processed through the AI", COLORS["green"]),
            (f"{stats.streak_longest}", "DAY STREAK", "your longest run", COLORS["blue"]),
        ]

        for value, label, subtitle, color in slides:
            console.print(Align.center(create_dramatic_stat(value, label, subtitle, color)))
            wait_for_keypress()
            console.clear()

        # Personality reveal
        personality = determine_personality(stats)
        personality_text = Text()
        personality_text.append("\n\n\n\n")
        personality_text.append(f"  {personality['emoji']}\n\n", style=Style(bold=True))
        personality_text.append(f"  You are\n", style=Style(color=COLORS["gray"]))
        personality_text.append(f"  {personality['title']}\n\n", style=Style(color=COLORS["purple"], bold=True))
        personality_text.append(f"  {personality['description']}\n\n\n", style=Style(color=COLORS["white"]))
        personality_text.append("  [ENTER]", style=Style(color=COLORS["dark"]))
        console.print(Align.center(personality_text))
        wait_for_keypress()
        console.clear()

    # === DASHBOARD VIEW ===
    console.print()

    # Header
    header = Text()
    header.append("═" * 60 + "\n", style=Style(color=COLORS["orange"]))
    header.append("  CLAUDE CODE WRAPPED ", style=Style(color=COLORS["white"], bold=True))
    header.append(str(stats.year), style=Style(color=COLORS["orange"], bold=True))
    header.append("\n" + "═" * 60, style=Style(color=COLORS["orange"]))
    console.print(Align.center(header))
    console.print()

    # Big stats row
    stats_table = Table(show_header=False, box=None, padding=(0, 3), expand=True)
    stats_table.add_column(justify="center")
    stats_table.add_column(justify="center")
    stats_table.add_column(justify="center")
    stats_table.add_column(justify="center")

    stats_table.add_row(
        create_big_stat(f"{stats.total_messages:,}", "messages", COLORS["orange"]),
        create_big_stat(str(stats.total_sessions), "sessions", COLORS["purple"]),
        create_big_stat(format_tokens(stats.total_tokens), "tokens", COLORS["green"]),
        create_big_stat(f"{stats.streak_longest}d", "best streak", COLORS["blue"]),
    )
    console.print(Align.center(stats_table))
    console.print()

    # Contribution graph
    console.print(create_contribution_graph(stats.daily_stats, stats.year))

    # Charts row
    charts = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    charts.add_column(ratio=1)
    charts.add_column(ratio=2)
    charts.add_row(
        create_personality_card(stats),
        create_weekday_chart(stats.weekday_distribution),
    )
    console.print(charts)

    # Hour chart
    console.print(create_hour_chart(stats.hourly_distribution))

    # Top lists
    lists = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    lists.add_column(ratio=1)
    lists.add_column(ratio=1)
    lists.add_row(
        create_top_list(stats.top_tools[:5], "Top Tools", COLORS["orange"]),
        create_top_list(stats.top_projects, "Top Projects", COLORS["green"]),
    )
    console.print(lists)

    # Insights
    insights = Text()
    if stats.most_active_day:
        insights.append("  Peak day: ", style=Style(color=COLORS["gray"]))
        insights.append(f"{stats.most_active_day[0].strftime('%b %d')}", style=Style(color=COLORS["orange"], bold=True))
        insights.append(f" ({stats.most_active_day[1]:,} msgs)", style=Style(color=COLORS["gray"]))
    if stats.most_active_hour is not None:
        insights.append("  •  Peak hour: ", style=Style(color=COLORS["gray"]))
        insights.append(f"{stats.most_active_hour}:00", style=Style(color=COLORS["purple"], bold=True))
    if stats.primary_model:
        insights.append("  •  Favorite: ", style=Style(color=COLORS["gray"]))
        insights.append(f"Claude {stats.primary_model}", style=Style(color=COLORS["blue"], bold=True))

    console.print()
    console.print(Align.center(insights))

    # === CREDITS SEQUENCE ===
    if animate:
        console.print()
        continue_text = Text()
        continue_text.append("\n    press [ENTER] for fun facts & credits", style=Style(color=COLORS["dark"]))
        console.print(Align.center(continue_text))
        wait_for_keypress()
        console.clear()

        # Fun facts
        facts = get_fun_facts(stats)
        if facts:
            console.print(Align.center(create_fun_facts_slide(facts)))
            wait_for_keypress()
            console.clear()

        # Credits roll
        for frame in create_credits_roll(stats):
            console.print(Align.center(frame))
            wait_for_keypress()
            console.clear()

    # Final footer
    console.print()
    footer = Text()
    footer.append("─" * 60 + "\n\n", style=Style(color=COLORS["dark"]))
    footer.append("Thanks for building with Claude ", style=Style(color=COLORS["gray"]))
    footer.append("✨\n\n", style=Style(color=COLORS["orange"]))
    footer.append("Built by ", style=Style(color=COLORS["gray"]))
    footer.append("Mert Deveci", style=Style(color=COLORS["white"], bold=True, link="https://x.com/gm_mertd"))
    footer.append(" · ", style=Style(color=COLORS["dark"]))
    footer.append("@gm_mertd", style=Style(color=COLORS["blue"], link="https://x.com/gm_mertd"))
    footer.append(" · ", style=Style(color=COLORS["dark"]))
    footer.append("Banker.so", style=Style(color=COLORS["blue"], bold=True, link="https://banker.so"))
    footer.append("\n")
    console.print(Align.center(footer))


if __name__ == "__main__":
    from .reader import load_all_messages
    from .stats import aggregate_stats

    print("Loading data...")
    messages = load_all_messages(year=2025)
    stats = aggregate_stats(messages, 2025)

    render_wrapped(stats)
