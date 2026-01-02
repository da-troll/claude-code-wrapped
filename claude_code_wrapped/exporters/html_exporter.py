"""HTML export for Claude Code Wrapped."""

from datetime import datetime, timedelta
from pathlib import Path

from ..stats import WrappedStats, format_tokens
from ..pricing import format_cost
from ..ui import COLORS, CONTRIB_COLORS, determine_personality, get_fun_facts, simplify_model_name, format_year_display


def export_to_html(stats: WrappedStats, year: int | None, output_path: Path) -> None:
    """Export wrapped stats to a nicely formatted HTML file.

    Args:
        stats: Wrapped statistics dataclass
        year: Year being wrapped
        output_path: Path to output HTML file
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

    # Build HTML
    html = _build_html_document(stats, year, personality, fun_facts, start_date, end_date)

    # Write to file
    output_path.write_text(html, encoding='utf-8')


def _build_html_document(stats: WrappedStats, year: int, personality: dict,
                         fun_facts: list, start_date: datetime, end_date: datetime) -> str:
    """Build the complete HTML document."""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code Wrapped {year}</title>
    {_get_css()}
</head>
<body>
    <div class="container">
        {_build_title_section(year)}
        {_build_dramatic_reveals(stats, start_date, end_date)}
        {_build_dashboard(stats, year, personality, fun_facts)}
        {_build_credits(stats, year)}
    </div>
</body>
</html>"""


def _get_css() -> str:
    """Get embedded CSS styles."""
    return f"""<style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --orange: {COLORS["orange"]};
            --purple: {COLORS["purple"]};
            --blue: {COLORS["blue"]};
            --green: {COLORS["green"]};
            --white: {COLORS["white"]};
            --gray: {COLORS["gray"]};
            --dark: {COLORS["dark"]};
            --bg: #0D1117;
            --fg: #E6EDF3;
        }}

        body {{
            background: var(--bg);
            color: var(--fg);
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .section {{
            margin: 80px 0;
            padding: 40px;
            background: #161B22;
            border-radius: 12px;
            border: 1px solid #30363D;
        }}

        .section-title {{
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 40px;
            letter-spacing: 0.2em;
        }}

        /* Title Section */
        .title-section {{
            text-align: center;
            padding: 100px 40px;
        }}

        .title-logo {{
            font-size: 3em;
            font-weight: bold;
            color: var(--purple);
            margin-bottom: 20px;
        }}

        .title-year {{
            font-size: 2em;
            color: var(--orange);
            margin: 20px 0;
        }}

        .title-credit {{
            color: var(--gray);
            margin-top: 40px;
        }}

        /* Dramatic Reveals */
        .reveal {{
            text-align: center;
            padding: 60px 40px;
        }}

        .reveal-value {{
            font-size: 4em;
            font-weight: bold;
            margin: 20px 0;
        }}

        .reveal-label {{
            font-size: 1.8em;
            font-weight: bold;
            color: var(--white);
            letter-spacing: 0.1em;
        }}

        .reveal-subtitle {{
            color: var(--gray);
            margin-top: 10px;
        }}

        .reveal-extra {{
            margin-top: 30px;
            font-size: 1.1em;
        }}

        /* Dashboard Grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}

        .panel {{
            background: #0D1117;
            border: 1px solid;
            border-radius: 8px;
            padding: 20px;
        }}

        .panel-title {{
            font-weight: bold;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}

        /* Stats Table */
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .stats-table th {{
            padding: 15px;
            text-align: center;
            font-size: 0.9em;
            color: var(--gray);
            border-bottom: 1px solid #30363D;
        }}

        .stats-table td {{
            padding: 15px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
        }}

        /* Personality Card */
        .personality {{
            text-align: center;
            padding: 30px;
        }}

        .personality-emoji {{
            font-size: 4em;
            margin-bottom: 15px;
        }}

        .personality-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: var(--purple);
            margin-bottom: 10px;
        }}

        .personality-desc {{
            color: var(--gray);
        }}

        /* Bar Charts */
        .bar-chart {{
            margin: 10px 0;
        }}

        .bar-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}

        .bar-label {{
            width: 120px;
            text-align: right;
            padding-right: 10px;
            color: var(--gray);
        }}

        .bar {{
            height: 20px;
            background: var(--purple);
            border-radius: 3px;
            transition: width 0.3s;
        }}

        .bar-value {{
            margin-left: 10px;
            color: var(--white);
        }}

        /* Monthly Cost Table */
        .cost-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .cost-table th {{
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #30363D;
            font-weight: bold;
        }}

        .cost-table td {{
            padding: 12px;
            border-bottom: 1px solid #30363D;
        }}

        .cost-table tr:last-child td {{
            border-bottom: none;
            font-weight: bold;
        }}

        /* Fun Facts */
        .fun-facts {{
            margin: 30px 0;
        }}

        .fun-fact {{
            margin: 15px 0;
            padding: 15px;
            background: #0D1117;
            border-left: 3px solid var(--purple);
            border-radius: 4px;
        }}

        .fun-fact-emoji {{
            font-size: 1.5em;
            margin-right: 10px;
        }}

        /* Credits */
        .credits-frame {{
            text-align: center;
            padding: 60px 40px;
            margin: 40px 0;
        }}

        .credits-title {{
            font-size: 2em;
            font-weight: bold;
            letter-spacing: 0.3em;
            margin-bottom: 30px;
        }}

        .credits-item {{
            margin: 20px 0;
        }}

        .credits-label {{
            color: var(--white);
            font-weight: bold;
            margin-right: 10px;
        }}

        .credits-value {{
            font-weight: bold;
            font-size: 1.2em;
        }}

        .credits-subitem {{
            color: var(--gray);
            margin-left: 40px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .reveal-value {{
                font-size: 2.5em;
            }}

            .section-title {{
                font-size: 1.8em;
            }}

            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Print Styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}

            .section {{
                page-break-inside: avoid;
                border: 1px solid #ccc;
            }}
        }}
    </style>"""


def _build_title_section(year: int | None) -> str:
    """Build the title section."""
    year_display = format_year_display(year)
    return f"""
    <div class="section title-section">
        <div class="title-logo">🎬 CLAUDE CODE WRAPPED</div>
        <div class="title-year">Your {year_display}</div>
        <div class="title-credit">
            A year in review · Generated {datetime.now().strftime('%B %d, %Y')}
        </div>
    </div>"""


def _build_dramatic_reveals(stats: WrappedStats, start_date: datetime, end_date: datetime) -> str:
    """Build the dramatic reveal sections."""
    date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

    from ..pricing import format_cost

    reveals = f"""
    <div class="section reveal">
        <div class="reveal-value" style="color: var(--orange);">{stats.total_messages:,}</div>
        <div class="reveal-label">TOTAL MESSAGES</div>
        <div class="reveal-subtitle">{date_range}</div>
    </div>

    <div class="section reveal">
        <div class="reveal-label">YOUR AVERAGES</div>
        <div class="reveal-extra">
            <div style="color: var(--blue); margin: 10px 0;">
                <strong>{stats.avg_messages_per_day:.1f}</strong> messages per day
            </div>
            <div style="color: var(--purple); margin: 10px 0;">
                <strong>{stats.avg_messages_per_week:.1f}</strong> messages per week
            </div>
            <div style="color: var(--orange); margin: 10px 0;">
                <strong>{stats.avg_messages_per_month:.1f}</strong> messages per month
            </div>"""

    if stats.estimated_cost is not None:
        reveals += f"""
            <div style="margin-top: 30px; color: var(--gray);">━━━━━━━━━━━━━━━━</div>
            <div style="color: var(--green); margin: 10px 0;">
                <strong>{format_cost(stats.avg_cost_per_day)}</strong> per day
            </div>
            <div style="color: var(--green); margin: 10px 0;">
                <strong>{format_cost(stats.avg_cost_per_week)}</strong> per week
            </div>
            <div style="color: var(--green); margin: 10px 0;">
                <strong>{format_cost(stats.avg_cost_per_month)}</strong> per month
            </div>"""

    reveals += """
        </div>
    </div>

    <div class="section reveal">
        <div class="reveal-value" style="color: var(--green);">{:,}</div>
        <div class="reveal-label">TOTAL TOKENS</div>
        <div class="reveal-subtitle">
            {}<br>
            <span style="color: var(--gray);">
                Input: {} · Output: {}
            </span>
        </div>
    </div>""".format(
        stats.total_tokens,
        format_tokens(stats.total_tokens),
        format_tokens(stats.total_input_tokens),
        format_tokens(stats.total_output_tokens)
    )

    return reveals


def _build_dashboard(stats: WrappedStats, year: int | None, personality: dict, fun_facts: list) -> str:
    """Build the main dashboard section."""

    year_display = format_year_display(year).upper()
    html = f"""
    <div class="section">
        <div class="section-title" style="color: var(--purple);">YOUR {year_display} DASHBOARD</div>

        <table class="stats-table">
            <thead>
                <tr>
                    <th>Messages</th>
                    <th>Sessions</th>
                    <th>Tokens</th>
                    <th>Streak</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color: var(--orange);">{stats.total_messages:,}</td>
                    <td style="color: var(--purple);">{stats.total_sessions:,}</td>
                    <td style="color: var(--green);">{format_tokens(stats.total_tokens)}</td>
                    <td style="color: var(--blue);">{stats.streak_longest}</td>
                </tr>
            </tbody>
        </table>

        {_build_contribution_graph(stats.daily_stats, year)}

        <div class="dashboard-grid">
            <div class="panel personality" style="border-color: var(--purple);">
                <div class="personality-emoji">{personality['emoji']}</div>
                <div class="personality-title">{personality['title']}</div>
                <div class="personality-desc">{personality['description']}</div>
            </div>

            <div class="panel" style="border-color: var(--blue);">
                <div class="panel-title" style="color: var(--blue);">Weekday Activity</div>
                {_build_weekday_chart(stats.weekday_distribution)}
            </div>
        </div>

        <div style="margin-top: 40px;">
            <div class="panel" style="border-color: var(--orange);">
                <div class="panel-title" style="color: var(--orange);">Hourly Activity</div>
                {_build_hourly_chart(stats.hourly_distribution)}
            </div>
        </div>

        {_build_tools_and_projects(stats)}
        {_build_mcp_section(stats)}
        {_build_monthly_costs(stats)}
        {_build_fun_facts_section(fun_facts)}
    </div>"""

    return html


def _build_contribution_graph(daily_stats: dict, year: int | None) -> str:
    """Build SVG contribution graph."""
    if not daily_stats:
        return '<div style="text-align: center; color: var(--gray); padding: 40px;">No activity data</div>'

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
                week.append((level, count, date_str))
            else:
                week.append((0, 0, date_str))

        weeks.append(week)
        current += timedelta(days=7)

    # SVG dimensions
    cell_size = 12
    cell_gap = 3
    label_width = 40
    graph_width = len(weeks) * (cell_size + cell_gap) + label_width
    graph_height = 7 * (cell_size + cell_gap) + 40

    # Build SVG
    svg = f'<svg width="{graph_width}" height="{graph_height}" style="margin: 40px auto; display: block;">\n'

    # Day labels
    days_labels = ["Mon", "", "Wed", "", "Fri", "", ""]
    for i, label in enumerate(days_labels):
        if label:
            y = i * (cell_size + cell_gap) + cell_size
            svg += f'<text x="0" y="{y}" fill="{COLORS["gray"]}" font-size="10">{label}</text>\n'

    # Cells
    for week_idx, week in enumerate(weeks):
        for day_idx, cell in enumerate(week):
            if cell is None:
                continue

            level, count, date_str = cell
            x = label_width + week_idx * (cell_size + cell_gap)
            y = day_idx * (cell_size + cell_gap)
            color = CONTRIB_COLORS[level]

            svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2">\n'
            svg += f'<title>{date_str}: {count} messages</title>\n'
            svg += '</rect>\n'

    # Legend
    legend_y = graph_height - 20
    legend_x = label_width
    svg += f'<text x="{legend_x}" y="{legend_y}" fill="{COLORS["gray"]}" font-size="10">Less</text>\n'

    for i, color in enumerate(CONTRIB_COLORS):
        x = legend_x + 40 + i * (cell_size + cell_gap)
        svg += f'<rect x="{x}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"></rect>\n'

    svg += f'<text x="{legend_x + 40 + len(CONTRIB_COLORS) * (cell_size + cell_gap) + 5}" y="{legend_y}" fill="{COLORS["gray"]}" font-size="10">More</text>\n'

    svg += '</svg>'

    # Activity count
    active_count = len([d for d in daily_stats.values() if d.message_count > 0])
    total_days = (end_date - start_date).days + 1

    return f'''
    <div style="margin: 40px 0;">
        <div style="text-align: center; color: var(--green); font-weight: bold; margin-bottom: 20px;">
            Activity · {active_count} of {total_days} days
        </div>
        {svg}
    </div>'''


def _build_weekday_chart(weekday_dist: list[int]) -> str:
    """Build weekday activity bar chart."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_val = max(weekday_dist) if weekday_dist else 1

    html = '<div class="bar-chart">'
    for i, (day, count) in enumerate(zip(days, weekday_dist)):
        width = int((count / max_val) * 100) if max_val > 0 else 0
        html += f'''
        <div class="bar-item">
            <div class="bar-label">{day}</div>
            <div class="bar" style="width: {width}%; background: var(--blue);"></div>
            <div class="bar-value">{count:,}</div>
        </div>'''
    html += '</div>'
    return html


def _build_hourly_chart(hourly_dist: list[int]) -> str:
    """Build hourly activity chart."""
    max_val = max(hourly_dist) if hourly_dist else 1

    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(60px, 1fr)); gap: 10px; margin-top: 20px;">'

    for hour, count in enumerate(hourly_dist):
        # Determine color by time of day
        if 6 <= hour < 12:
            color = "var(--orange)"
        elif 12 <= hour < 18:
            color = "var(--blue)"
        elif 18 <= hour < 22:
            color = "var(--purple)"
        else:
            color = "var(--gray)"

        height = int((count / max_val) * 100) if max_val > 0 else 0

        html += f'''
        <div style="text-align: center;">
            <div style="height: 100px; display: flex; align-items: flex-end; justify-content: center;">
                <div style="width: 100%; height: {height}%; background: {color}; border-radius: 3px;" title="{hour}:00 - {count:,} messages"></div>
            </div>
            <div style="font-size: 0.8em; color: var(--gray); margin-top: 5px;">{hour}</div>
        </div>'''

    html += '</div>'
    return html


def _build_tools_and_projects(stats: WrappedStats) -> str:
    """Build tools and projects panels."""
    html = '<div class="dashboard-grid" style="margin-top: 40px;">'

    # Top Tools
    if stats.top_tools:
        max_tool_count = stats.top_tools[0][1] if stats.top_tools else 1
        html += '''
        <div class="panel" style="border-color: var(--purple);">
            <div class="panel-title" style="color: var(--purple);">Top Tools</div>
            <div class="bar-chart">'''

        for tool, count in stats.top_tools[:5]:
            width = int((count / max_tool_count) * 100)
            html += f'''
            <div class="bar-item">
                <div class="bar-label">{tool}</div>
                <div class="bar" style="width: {width}%; background: var(--purple);"></div>
                <div class="bar-value">{count:,}</div>
            </div>'''

        html += '</div></div>'

    # Top Projects
    if stats.top_projects:
        max_proj_count = stats.top_projects[0][1] if stats.top_projects else 1
        html += '''
        <div class="panel" style="border-color: var(--blue);">
            <div class="panel-title" style="color: var(--blue);">Top Projects</div>
            <div class="bar-chart">'''

        for proj, count in stats.top_projects[:5]:
            width = int((count / max_proj_count) * 100)
            # Truncate long project names
            display_name = proj if len(proj) <= 20 else proj[:17] + "..."
            html += f'''
            <div class="bar-item">
                <div class="bar-label" title="{proj}">{display_name}</div>
                <div class="bar" style="width: {width}%; background: var(--blue);"></div>
                <div class="bar-value">{count:,}</div>
            </div>'''

        html += '</div></div>'

    html += '</div>'
    return html


def _build_mcp_section(stats: WrappedStats) -> str:
    """Build MCP servers section if any."""
    if not stats.top_mcps:
        return ""

    max_mcp_count = stats.top_mcps[0][1] if stats.top_mcps else 1

    html = '''
    <div style="margin-top: 40px;">
        <div class="panel" style="border-color: var(--green);">
            <div class="panel-title" style="color: var(--green);">MCP Servers</div>
            <div class="bar-chart">'''

    for mcp, count in stats.top_mcps[:3]:
        width = int((count / max_mcp_count) * 100)
        html += f'''
        <div class="bar-item">
            <div class="bar-label">{mcp}</div>
            <div class="bar" style="width: {width}%; background: var(--green);"></div>
            <div class="bar-value">{count:,}</div>
        </div>'''

    html += '</div></div></div>'
    return html


def _build_monthly_costs(stats: WrappedStats) -> str:
    """Build monthly cost breakdown table."""
    if not stats.monthly_costs:
        return ""

    html = '''
    <div style="margin-top: 40px;">
        <div class="panel" style="border-color: var(--green);">
            <div class="panel-title" style="color: var(--green);">Monthly Cost Breakdown</div>
            <table class="cost-table">
                <thead>
                    <tr>
                        <th>Month</th>
                        <th style="color: var(--blue);">Input</th>
                        <th style="color: var(--orange);">Output</th>
                        <th style="color: var(--purple);">Cache</th>
                        <th style="color: var(--green);">Cost</th>
                    </tr>
                </thead>
                <tbody>'''

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

            html += f'''
                <tr>
                    <td>{month_label}</td>
                    <td style="color: var(--blue);">{format_tokens(input_tokens)}</td>
                    <td style="color: var(--orange);">{format_tokens(output_tokens)}</td>
                    <td style="color: var(--purple);">{format_tokens(cache_tokens)}</td>
                    <td style="color: var(--green);">{format_cost(cost)}</td>
                </tr>'''

    html += f'''
                <tr style="border-top: 2px solid #30363D;">
                    <td><strong>Total</strong></td>
                    <td style="color: var(--blue);"><strong>{format_tokens(total_input)}</strong></td>
                    <td style="color: var(--orange);"><strong>{format_tokens(total_output)}</strong></td>
                    <td style="color: var(--purple);"><strong>{format_tokens(total_cache)}</strong></td>
                    <td style="color: var(--green);"><strong>{format_cost(total_cost)}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>'''

    return html


def _build_fun_facts_section(fun_facts: list) -> str:
    """Build fun facts section."""
    if not fun_facts:
        return ""

    html = '''
    <div style="margin-top: 40px;">
        <div class="panel" style="border-color: var(--purple);">
            <div class="panel-title" style="color: var(--purple);">Insights</div>
            <div class="fun-facts">'''

    for emoji, fact in fun_facts:
        html += f'''
            <div class="fun-fact">
                <span class="fun-fact-emoji">{emoji}</span>
                <span>{fact}</span>
            </div>'''

    html += '</div></div></div>'
    return html


def _build_credits(stats: WrappedStats, year: int | None) -> str:
    """Build credits section."""

    # Aggregate costs by simplified model name
    display_costs = {}
    for model, cost in stats.cost_by_model.items():
        display_name = simplify_model_name(model)
        display_costs[display_name] = display_costs.get(display_name, 0) + cost

    html = '<div class="section">'

    # Frame 1: The Numbers
    html += '''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--green);">THE NUMBERS</div>'''

    if stats.estimated_cost is not None:
        html += f'''
        <div class="credits-item">
            <span class="credits-label">Estimated Cost</span>
            <span class="credits-value" style="color: var(--green);">{format_cost(stats.estimated_cost)}</span>
        </div>'''

        for model, cost in sorted(display_costs.items(), key=lambda x: -x[1]):
            html += f'''
        <div class="credits-subitem">{model}: {format_cost(cost)}</div>'''

    html += f'''
        <div class="credits-item" style="margin-top: 30px;">
            <span class="credits-label">Tokens</span>
            <span class="credits-value" style="color: var(--orange);">{format_tokens(stats.total_tokens)}</span>
        </div>
        <div class="credits-subitem">Input: {format_tokens(stats.total_input_tokens)}</div>
        <div class="credits-subitem">Output: {format_tokens(stats.total_output_tokens)}</div>
    </div>'''

    # Frame 2: Timeline
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
    html += f'''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--orange);">TIMELINE</div>
        <div class="credits-item">
            <span class="credits-label">Period</span>
            <span class="credits-value" style="color: var(--orange);">{period_text}</span>
        </div>'''

    if stats.first_message_date:
        html += f'''
        <div class="credits-item">
            <span class="credits-label">Journey started</span>
            <span class="credits-value" style="color: var(--gray);">{stats.first_message_date.strftime('%B %d')}</span>
        </div>'''

    html += f'''
        <div class="credits-item">
            <span class="credits-label">Active days</span>
            <span class="credits-value" style="color: var(--orange);">{stats.active_days}</span>
            <span style="color: var(--gray);"> of {total_days}</span>
        </div>'''

    if stats.most_active_hour is not None:
        hour_label = "AM" if stats.most_active_hour < 12 else "PM"
        hour_12 = stats.most_active_hour % 12 or 12
        html += f'''
        <div class="credits-item">
            <span class="credits-label">Peak hour</span>
            <span class="credits-value" style="color: var(--purple);">{hour_12}:00 {hour_label}</span>
        </div>'''

    html += '</div>'

    # Frame 3: Averages
    html += f'''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--blue);">AVERAGES</div>
        <div class="credits-item">
            <span class="credits-label">Messages</span>
        </div>
        <div class="credits-subitem">Per day: {stats.avg_messages_per_day:.1f}</div>
        <div class="credits-subitem">Per week: {stats.avg_messages_per_week:.1f}</div>
        <div class="credits-subitem">Per month: {stats.avg_messages_per_month:.1f}</div>'''

    if stats.estimated_cost is not None:
        html += f'''
        <div class="credits-item" style="margin-top: 20px;">
            <span class="credits-label">Cost</span>
        </div>
        <div class="credits-subitem">Per day: {format_cost(stats.avg_cost_per_day)}</div>
        <div class="credits-subitem">Per week: {format_cost(stats.avg_cost_per_week)}</div>
        <div class="credits-subitem">Per month: {format_cost(stats.avg_cost_per_month)}</div>'''

    html += '</div>'

    # Frame 4: Longest Streak (if significant)
    if stats.streak_longest >= 3 and stats.streak_longest_start and stats.streak_longest_end:
        html += f'''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--blue);">LONGEST STREAK</div>
        <div class="credits-item">
            <span class="credits-value" style="color: var(--blue);">{stats.streak_longest} days</span>
            <span style="color: var(--white);"> of consistent coding</span>
        </div>
        <div class="credits-item" style="margin-top: 20px;">
            <span class="credits-label">From</span>
            <span class="credits-value">{stats.streak_longest_start.strftime('%B %d, %Y')}</span>
        </div>
        <div class="credits-item">
            <span class="credits-label">To</span>
            <span class="credits-value">{stats.streak_longest_end.strftime('%B %d, %Y')}</span>
        </div>
        <div style="margin-top: 20px; color: var(--gray); font-style: italic;">
            Consistency is the key to mastery.'''

        if stats.streak_current > 0:
            html += f'''<br><br>Current streak: {stats.streak_current} days'''

        html += '''
        </div>
    </div>'''

    # Frame 5: Longest Conversation
    if stats.longest_conversation_messages > 0:
        html += f'''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--purple);">LONGEST CONVERSATION</div>
        <div class="credits-item">
            <span class="credits-label">Messages</span>
            <span class="credits-value" style="color: var(--purple);">{stats.longest_conversation_messages:,}</span>
        </div>'''

        if stats.longest_conversation_tokens > 0:
            html += f'''
        <div class="credits-item">
            <span class="credits-label">Tokens</span>
            <span class="credits-value" style="color: var(--orange);">{format_tokens(stats.longest_conversation_tokens)}</span>
        </div>'''

        if stats.longest_conversation_date:
            html += f'''
        <div class="credits-item">
            <span class="credits-label">Date</span>
            <span class="credits-value" style="color: var(--gray);">{stats.longest_conversation_date.strftime('%B %d, %Y')}</span>
        </div>'''

        html += '''
        <div style="margin-top: 20px; color: var(--gray);">That's one epic coding session!</div>
    </div>'''

    # Frame 5: Starring (Models)
    html += '''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--purple);">STARRING</div>'''

    for model, count in stats.models_used.most_common(3):
        html += f'''
        <div class="credits-item">
            <span class="credits-label">Claude {model}</span>
            <span style="color: var(--gray);">({count:,} messages)</span>
        </div>'''

    html += '</div>'

    # Frame 6: Projects
    if stats.top_projects:
        html += '''
    <div class="credits-frame">
        <div class="credits-title" style="color: var(--blue);">PROJECTS</div>'''

        for proj, count in stats.top_projects[:5]:
            html += f'''
        <div class="credits-item">
            <span class="credits-label">{proj}</span>
            <span style="color: var(--gray);">({count:,} messages)</span>
        </div>'''

        html += '</div>'

    # Final card
    if year is not None:
        farewell_text = f'See you in <span style="color: var(--orange); font-weight: bold;">{year + 1}</span>'
    else:
        farewell_text = '<span style="color: var(--orange); font-weight: bold;">Keep coding!</span>'

    html += f'''
    <div class="credits-frame">
        <div style="font-size: 1.5em; color: var(--gray); margin-bottom: 20px;">
            {farewell_text}
        </div>
        <div style="margin-top: 40px;">
            <a href="https://banker.so" style="color: var(--blue); text-decoration: none; font-weight: bold;">
                Banker.so
            </a>
            <span style="color: var(--gray);"> presents</span>
        </div>
    </div>
    '''

    html += '</div>'  # Close credits section

    return html
