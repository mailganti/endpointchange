"""Output formatting helpers."""

import json
import click
from typing import List, Dict, Any


def format_table(data: List[Dict], columns: List[str], headers: List[str] = None) -> str:
    """Format data as a simple table."""
    if not data:
        return "No data found."
    
    headers = headers or columns
    
    # Calculate column widths
    widths = []
    for i, col in enumerate(columns):
        header_width = len(headers[i])
        data_width = max(len(str(row.get(col, ''))) for row in data) if data else 0
        widths.append(max(header_width, data_width, 4))
    
    # Build table
    lines = []
    
    # Header
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in data:
        row_line = "  ".join(str(row.get(col, '')).ljust(widths[i]) for i, col in enumerate(columns))
        lines.append(row_line)
    
    return "\n".join(lines)


def output(ctx, data: Any, columns: List[str] = None, headers: List[str] = None):
    """Output data in requested format."""
    output_format = ctx.obj.get('output', 'table')
    
    if output_format == 'json':
        click.echo(json.dumps(data, indent=2, default=str))
    elif isinstance(data, list) and columns:
        click.echo(format_table(data, columns, headers))
    elif isinstance(data, dict):
        for key, value in data.items():
            click.echo(f"{key}: {value}")
    else:
        click.echo(data)


def success(message: str):
    """Print success message."""
    click.echo(click.style(f"✓ {message}", fg='green'))


def error(message: str):
    """Print error message."""
    click.echo(click.style(f"✗ {message}", fg='red'), err=True)


def warning(message: str):
    """Print warning message."""
    click.echo(click.style(f"⚠ {message}", fg='yellow'))


def info(message: str):
    """Print info message."""
    click.echo(click.style(f"ℹ {message}", fg='blue'))


def status_color(status: str) -> str:
    """Get colored status string."""
    colors = {
        'online': 'green',
        'offline': 'red',
        'pending': 'yellow',
        'approved': 'green',
        'denied': 'red',
        'executed': 'blue',
        'failed': 'red',
        'running': 'cyan',
    }
    color = colors.get(status.lower(), 'white')
    return click.style(status, fg=color)
