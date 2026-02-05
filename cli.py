"""UnifiedTree CLI - Main entry point."""

import click
import os
import json
from pathlib import Path

from unifiedtree.config import Config
from unifiedtree.client import UTClient
from unifiedtree.commands import agents, workflows, scripts, reports, tokens

# Config file location
CONFIG_DIR = Path.home() / ".unifiedtree"
CONFIG_FILE = CONFIG_DIR / "config.json"


@click.group()
@click.option('--server', envvar='UNIFIEDTREE_SERVER', help='Server URL')
@click.option('--token', envvar='UNIFIEDTREE_TOKEN', help='API token')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.version_option(version='1.0.0', prog_name='unifiedtree')
@click.pass_context
def cli(ctx, server, token, output):
    """
    UnifiedTree CLI - Orchestration system command line interface.
    
    \b
    Configure with environment variables:
      UNIFIEDTREE_SERVER=https://your-server:8443
      UNIFIEDTREE_TOKEN=your-api-token
    
    \b
    Or use a config file (~/.unifiedtree/config.json):
      unifiedtree config set-server https://your-server:8443
      unifiedtree config set-token your-api-token
    """
    ctx.ensure_object(dict)
    
    # Load config
    config = Config.load()
    
    # Override with command line options
    if server:
        config.server = server
    if token:
        config.token = token
    
    ctx.obj['config'] = config
    ctx.obj['output'] = output
    ctx.obj['client'] = UTClient(config)


@cli.group()
def config():
    """Configure CLI settings."""
    pass


@cli.command('configure')
def configure_interactive():
    """Interactive configuration setup."""
    click.echo("UnifiedTree CLI Configuration")
    click.echo("=" * 40)
    
    cfg = Config.load()
    
    # Server URL
    default_server = cfg.server or "https://localhost:8443"
    cfg.server = click.prompt("Server URL", default=default_server).rstrip('/')
    
    # API Base Path
    default_base = cfg.api_base_path or "/api/v1"
    cfg.api_base_path = click.prompt("API Base Path", default=default_base)
    
    # API Token
    token_display = '****' + cfg.token[-4:] if cfg.token and len(cfg.token) > 4 else "(not set)"
    click.echo(f"Current API Token: {token_display}")
    new_token = click.prompt("API Token (leave blank to keep current)", default="", show_default=False)
    if new_token:
        cfg.token = new_token
    
    # SSL Verification
    cfg.ssl_verify = click.confirm("Verify SSL certificates?", default=cfg.ssl_verify)
    
    # Request Timeout
    cfg.timeout = click.prompt("Request timeout (seconds)", default=cfg.timeout, type=int)
    
    # Save
    cfg.save()
    click.echo("\n✓ Configuration saved to ~/.unifiedtree/config.json")
    
    # Test connection option
    if click.confirm("\nTest connection now?", default=True):
        client = UTClient(cfg)
        try:
            click.echo(f"Connecting to {cfg.server}{cfg.api_base_path}/tokens/validate...")
            result = client.get('/tokens/validate')
            click.echo(f"✓ Connected successfully!")
            click.echo(f"  Token: {result.get('token_name', 'unknown')}")
            click.echo(f"  Role:  {result.get('role', 'unknown')}")
        except Exception as e:
            click.echo(f"✗ Connection failed: {e}", err=True)


@config.command('set-server')
@click.argument('url')
def set_server(url):
    """Set the server URL."""
    cfg = Config.load()
    cfg.server = url.rstrip('/')
    cfg.save()
    click.echo(f"✓ Server set to: {cfg.server}")


@config.command('set-token')
@click.argument('token')
def set_token(token):
    """Set the API token."""
    cfg = Config.load()
    cfg.token = token
    cfg.save()
    click.echo("✓ Token saved")


@config.command('show')
def show_config():
    """Show current configuration."""
    cfg = Config.load()
    click.echo(f"Server:        {cfg.server or '(not set)'}")
    click.echo(f"API Base Path: {cfg.api_base_path}")
    click.echo(f"Token:         {'****' + cfg.token[-4:] if cfg.token and len(cfg.token) > 4 else '(not set)'}")
    click.echo(f"SSL Verify:    {cfg.ssl_verify}")
    click.echo(f"Timeout:       {cfg.timeout}s")
    click.echo(f"Config File:   {CONFIG_FILE}")


@config.command('test')
@click.pass_context
def test_connection(ctx):
    """Test connection to server."""
    client = ctx.obj.get('client') or UTClient(Config.load())
    
    click.echo(f"Testing connection to {client.config.server}...")
    
    try:
        result = client.get('/tokens/validate')
        click.echo(f"✓ Connected successfully!")
        click.echo(f"  Token: {result.get('token_name', 'unknown')}")
        click.echo(f"  Role:  {result.get('role', 'unknown')}")
        if result.get('username'):
            click.echo(f"  User:  {result.get('username')}")
    except Exception as e:
        click.echo(f"✗ Connection failed: {e}", err=True)
        raise SystemExit(1)


# Register command groups
cli.add_command(agents.agents)
cli.add_command(workflows.workflows)
cli.add_command(scripts.scripts)
cli.add_command(reports.reports)
cli.add_command(tokens.tokens)


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()
