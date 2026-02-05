"""Tokens commands."""

import click
from unifiedtree.output import output, success, error, info


@click.group()
def tokens():
    """Manage API tokens."""
    pass


@tokens.command('list')
@click.option('--include-revoked', is_flag=True, help='Include revoked tokens')
@click.option('--role', type=click.Choice(['admin', 'user', 'agent', 'readonly']), help='Filter by role')
@click.pass_context
def list_tokens(ctx, include_revoked, role):
    """List tokens."""
    client = ctx.obj['client']
    
    try:
        params = {}
        if include_revoked:
            params['include_revoked'] = 'true'
        if role:
            params['role'] = role
        
        result = client.get('/tokens', params=params)
        tokens_list = result.get('tokens', [])
        
        if not tokens_list:
            click.echo("No tokens found.")
            return
        
        output(ctx, tokens_list,
               columns=['token_id', 'token_name', 'role', 'username', 'token_masked', 'revoked'],
               headers=['ID', 'Name', 'Role', 'User', 'Token', 'Revoked'])
        
        click.echo(f"\nTotal: {len(tokens_list)} tokens")
        
    except Exception as e:
        error(f"Failed to list tokens: {e}")
        raise SystemExit(1)


@tokens.command('create')
@click.option('--name', '-n', required=True, help='Token name/description')
@click.option('--role', '-r', type=click.Choice(['admin', 'user', 'agent', 'readonly']), default='user', help='Token role')
@click.option('--username', '-u', help='Associate with username')
@click.option('--expires', '-e', type=int, help='Expiration in days')
@click.option('--env', '-E', multiple=True, help='Environment access (DEV, TEST, PROD, or *)')
@click.pass_context
def create_token(ctx, name, role, username, expires, env):
    """Create a new API token."""
    client = ctx.obj['client']
    
    try:
        data = {
            'token_name': name,
            'role': role
        }
        if username:
            data['username'] = username
        if expires:
            data['expires_days'] = expires
        if env:
            data['environments'] = list(env)
        
        result = client.post('/tokens', data)
        
        success(f"Token created: {result.get('token_name')}")
        click.echo("")
        click.echo(click.style("═" * 60, fg='yellow'))
        click.echo(click.style("  YOUR API TOKEN (save this now!):", fg='yellow', bold=True))
        click.echo(click.style(f"  {result.get('token')}", fg='green', bold=True))
        click.echo(click.style("═" * 60, fg='yellow'))
        click.echo("")
        click.echo(f"Token ID: {result.get('token_id')}")
        click.echo(f"Role:     {result.get('role')}")
        if result.get('expires_at'):
            click.echo(f"Expires:  {result.get('expires_at')}")
        click.echo("")
        click.echo(click.style("⚠️  This token will NOT be shown again!", fg='red', bold=True))
        
    except Exception as e:
        error(f"Failed to create token: {e}")
        raise SystemExit(1)


@tokens.command('revoke')
@click.argument('token_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def revoke_token(ctx, token_id, yes):
    """Revoke a token."""
    client = ctx.obj['client']
    
    if not yes:
        click.confirm(f"Revoke token ID {token_id}?", abort=True)
    
    try:
        result = client.post(f'/tokens/{token_id}/revoke')
        success(result.get('message', f'Token {token_id} revoked'))
        
    except Exception as e:
        error(f"Failed to revoke token: {e}")
        raise SystemExit(1)


@tokens.command('regenerate')
@click.argument('token_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def regenerate_token(ctx, token_id, yes):
    """Regenerate a token (creates new value, invalidates old)."""
    client = ctx.obj['client']
    
    if not yes:
        click.confirm(f"Regenerate token ID {token_id}? The old token will stop working immediately.", abort=True)
    
    try:
        result = client.post(f'/tokens/{token_id}/regenerate')
        
        success(f"Token regenerated: {result.get('token_name')}")
        click.echo("")
        click.echo(click.style("═" * 60, fg='yellow'))
        click.echo(click.style("  YOUR NEW API TOKEN (save this now!):", fg='yellow', bold=True))
        click.echo(click.style(f"  {result.get('token')}", fg='green', bold=True))
        click.echo(click.style("═" * 60, fg='yellow'))
        click.echo("")
        click.echo(click.style("⚠️  This token will NOT be shown again!", fg='red', bold=True))
        
    except Exception as e:
        error(f"Failed to regenerate token: {e}")
        raise SystemExit(1)


@tokens.command('delete')
@click.argument('token_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete_token(ctx, token_id, yes):
    """Permanently delete a token."""
    client = ctx.obj['client']
    
    if not yes:
        click.confirm(f"Permanently delete token ID {token_id}? This cannot be undone.", abort=True)
    
    try:
        result = client.delete(f'/tokens/{token_id}')
        success(result.get('message', f'Token {token_id} deleted'))
        
    except Exception as e:
        error(f"Failed to delete token: {e}")
        raise SystemExit(1)


@tokens.command('info')
@click.pass_context
def token_info(ctx):
    """Show info about the current token being used."""
    client = ctx.obj['client']
    
    try:
        result = client.get('/tokens/me')
        
        click.echo(f"Token:        {result.get('token_name', 'unknown')}")
        click.echo(f"Role:         {result.get('role', 'unknown')}")
        click.echo(f"Username:     {result.get('username', 'N/A')}")
        click.echo(f"Environments: {', '.join(result.get('environments', []))}")
        if result.get('has_full_access'):
            click.echo(click.style("Full Access:  Yes (superadmin)", fg='green'))
        
    except Exception as e:
        error(f"Failed to get token info: {e}")
        raise SystemExit(1)
