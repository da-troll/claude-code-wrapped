"""Claude Code Wrapped - Main entry point."""

import argparse
import sys
from datetime import datetime

from rich.console import Console

from .reader import get_claude_dir, load_all_messages
from .stats import aggregate_stats
from .ui import render_wrapped


def main():
    """Main entry point for Claude Code Wrapped."""
    parser = argparse.ArgumentParser(
        description="Claude Code Wrapped - Your year with Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude-code-wrapped              Show your wrapped for current year
  claude-code-wrapped 2025         Show your 2025 wrapped
  claude-code-wrapped --no-animate Skip animations
        """,
    )
    parser.add_argument(
        "year",
        type=int,
        nargs="?",
        default=datetime.now().year,
        help="Year to analyze (default: current year)",
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

    args = parser.parse_args()
    console = Console()

    # Check for Claude directory
    try:
        claude_dir = get_claude_dir()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\nMake sure you have Claude Code installed and have used it at least once.")
        sys.exit(1)

    # Load messages
    if not args.json:
        console.print(f"\n[dim]Loading your Claude Code history for {args.year}...[/dim]\n")

    messages = load_all_messages(claude_dir, year=args.year)

    if not messages:
        console.print(f"[yellow]No Claude Code activity found for {args.year}.[/yellow]")
        console.print("\nTry a different year or make sure you've used Claude Code.")
        sys.exit(0)

    # Calculate stats
    stats = aggregate_stats(messages, args.year)

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
            "streak_longest": stats.streak_longest,
            "streak_current": stats.streak_current,
            "most_active_hour": stats.most_active_hour,
            "most_active_day": stats.most_active_day[0].isoformat() if stats.most_active_day else None,
            "most_active_day_messages": stats.most_active_day[1] if stats.most_active_day else None,
            "primary_model": stats.primary_model,
            "top_tools": dict(stats.top_tools),
            "top_projects": dict(stats.top_projects),
            "hourly_distribution": stats.hourly_distribution,
            "weekday_distribution": stats.weekday_distribution,
            "estimated_cost_usd": stats.estimated_cost,
            "cost_by_model": stats.cost_by_model,
        }
        print(json.dumps(output, indent=2))
    else:
        render_wrapped(stats, console, animate=not args.no_animate)


if __name__ == "__main__":
    main()
