"""Claude Code Wrapped - Main entry point."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from .reader import get_claude_dir, load_all_messages
from .stats import aggregate_stats
from .ui import render_wrapped
from .exporters import export_to_html, export_to_markdown


def main():
    """Main entry point for Claude Code Wrapped."""
    parser = argparse.ArgumentParser(
        description="Claude Code Wrapped - Your year with Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude-code-wrapped                Show your wrapped for current year
  claude-code-wrapped 2025           Show your 2025 wrapped
  claude-code-wrapped all            Show your all-time wrapped
  claude-code-wrapped --no-animate   Skip animations
  claude-code-wrapped --html         Export to HTML file
  claude-code-wrapped --markdown     Export to Markdown file
  claude-code-wrapped all --html --markdown  Export all-time stats to both formats
        """,
    )
    parser.add_argument(
        "year",
        type=str,
        nargs="?",
        default=str(datetime.now().year),
        help="Year to analyze or 'all' for all-time stats (default: current year)",
    )
    parser.add_argument(
        "--no-animate",
        action="store_true",
        help="Disable animations for faster display",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw stats as JSON",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Export to HTML file",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Export to Markdown file",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output filename (without extension)",
    )

    args = parser.parse_args()
    console = Console()

    # Parse year argument
    if args.year.lower() == "all":
        year_filter = None
        year_display = "all-time"
        year_label = "All Time"
    else:
        try:
            year_filter = int(args.year)
            year_display = str(year_filter)
            year_label = str(year_filter)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid year '{args.year}'. Use a year (e.g., 2025) or 'all'.")
            sys.exit(1)

    # Check for Claude directory
    try:
        claude_dir = get_claude_dir()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\nMake sure you have Claude Code installed and have used it at least once.")
        sys.exit(1)

    # Load messages
    if not args.json:
        console.print(f"\n[dim]Loading your Claude Code history for {year_label}...[/dim]\n")

    messages = load_all_messages(claude_dir, year=year_filter)

    if not messages:
        console.print(f"[yellow]No Claude Code activity found for {year_label}.[/yellow]")
        console.print("\nTry a different year or make sure you've used Claude Code.")
        sys.exit(0)

    # Calculate stats
    stats = aggregate_stats(messages, year_filter)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    # Export to HTML if requested
    if args.html:
        if args.output:
            output_name = args.output
        else:
            output_name = f"claude-wrapped-{year_display}-{timestamp}"
        html_path = Path(f"{output_name}.html")
        export_to_html(stats, year_filter, html_path)
        console.print(f"\n[green]✓[/green] Exported to [bold]{html_path}[/bold]")

    # Export to Markdown if requested
    if args.markdown:
        if args.output:
            output_name = args.output
        else:
            output_name = f"claude-wrapped-{year_display}-{timestamp}"
        md_path = Path(f"{output_name}.md")
        export_to_markdown(stats, year_filter, md_path)
        console.print(f"\n[green]✓[/green] Exported to [bold]{md_path}[/bold]")

    # Output
    if args.json:
        import json
        output = {
            "year": stats.year,
            "total_messages": stats.total_messages,
            "total_user_messages": stats.total_user_messages,
            "total_assistant_messages": stats.total_assistant_messages,
            "total_sessions": stats.total_sessions,
            "total_projects": stats.total_projects,
            "total_tokens": stats.total_tokens,
            "total_input_tokens": stats.total_input_tokens,
            "total_output_tokens": stats.total_output_tokens,
            "active_days": stats.active_days,
            "late_night_days": stats.late_night_days,
            "streak_longest": stats.streak_longest,
            "streak_current": stats.streak_current,
            "most_active_hour": stats.most_active_hour,
            "most_active_day": stats.most_active_day[0].isoformat() if stats.most_active_day else None,
            "most_active_day_messages": stats.most_active_day[1] if stats.most_active_day else None,
            "primary_model": stats.primary_model,
            "top_tools": dict(stats.top_tools),
            "top_mcps": dict(stats.top_mcps),
            "top_projects": dict(stats.top_projects),
            "hourly_distribution": stats.hourly_distribution,
            "weekday_distribution": stats.weekday_distribution,
            "estimated_cost_usd": stats.estimated_cost,
            "cost_by_model": stats.cost_by_model,
            # Averages
            "avg_messages_per_day": round(stats.avg_messages_per_day, 1),
            "avg_messages_per_week": round(stats.avg_messages_per_week, 1),
            "avg_messages_per_month": round(stats.avg_messages_per_month, 1),
            "avg_cost_per_day": round(stats.avg_cost_per_day, 2) if stats.avg_cost_per_day else None,
            "avg_cost_per_week": round(stats.avg_cost_per_week, 2) if stats.avg_cost_per_week else None,
            "avg_cost_per_month": round(stats.avg_cost_per_month, 2) if stats.avg_cost_per_month else None,
            # Code activity
            "total_edits": stats.total_edits,
            "total_writes": stats.total_writes,
            "avg_code_changes_per_day": round(stats.avg_edits_per_day, 1),
            "avg_code_changes_per_week": round(stats.avg_edits_per_week, 1),
            # Monthly breakdown
            "monthly_costs": stats.monthly_costs,
            "monthly_tokens": stats.monthly_tokens,
            # Longest conversation
            "longest_conversation_messages": stats.longest_conversation_messages,
            "longest_conversation_tokens": stats.longest_conversation_tokens,
            "longest_conversation_date": stats.longest_conversation_date.isoformat() if stats.longest_conversation_date else None,
        }
        print(json.dumps(output, indent=2))
    else:
        render_wrapped(stats, console, animate=not args.no_animate)


if __name__ == "__main__":
    main()
