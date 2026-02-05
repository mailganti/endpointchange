"""Scripts commands."""

import click
from unifiedtree.output import output, success, error


@click.group()
def scripts():
    """Manage scripts."""
    pass


@scripts.command('list')
@click.pass_context
def list_scripts(ctx):
    """List all registered scripts."""
    client = ctx.obj['client']
    
    try:
        scripts_list = client.get('/scripts')
        
        if not scripts_list:
            click.echo("No scripts registered.")
            return
        
        output(ctx, scripts_list,
               columns=['script_id', 'name', 'script_path', 'timeout'],
               headers=['ID', 'Name', 'Path', 'Timeout'])
        
        click.echo(f"\nTotal: {len(scripts_list)} scripts")
        
    except Exception as e:
        error(f"Failed to list scripts: {e}")
        raise SystemExit(1)


@scripts.command('show')
@click.argument('script_id')
@click.pass_context
def show_script(ctx, script_id):
    """Show script details."""
    client = ctx.obj['client']
    
    try:
        script = client.get(f'/scripts/{script_id}')
        
        click.echo(f"Script ID:   {script.get('script_id')}")
        click.echo(f"Name:        {script.get('name')}")
        click.echo(f"Path:        {script.get('script_path')}")
        click.echo(f"Timeout:     {script.get('timeout', 300)}s")
        click.echo(f"Description: {script.get('description', 'N/A')}")
        
    except Exception as e:
        error(f"Failed to get script: {e}")
        raise SystemExit(1)


@scripts.command('register')
@click.option('--id', 'script_id', required=True, help='Script ID')
@click.option('--name', required=True, help='Display name')
@click.option('--path', required=True, help='Script path on agent')
@click.option('--timeout', default=300, help='Execution timeout in seconds')
@click.option('--description', '-d', help='Script description')
@click.pass_context
def register_script(ctx, script_id, name, path, timeout, description):
    """Register a new script."""
    client = ctx.obj['client']
    
    try:
        data = {
            'script_id': script_id,
            'name': name,
            'script_path': path,
            'timeout': timeout,
        }
        if description:
            data['description'] = description
        
        result = client.post('/scripts/register', data)
        success(f"Script '{script_id}' registered")
        
    except Exception as e:
        error(f"Failed to register script: {e}")
        raise SystemExit(1)


@scripts.command('delete')
@click.argument('script_id')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete_script(ctx, script_id, yes):
    """Delete a script."""
    client = ctx.obj['client']
    
    if not yes:
        click.confirm(f"Delete script '{script_id}'?", abort=True)
    
    try:
        client.delete(f'/scripts/{script_id}')
        success(f"Script '{script_id}' deleted")
        
    except Exception as e:
        error(f"Failed to delete script: {e}")
        raise SystemExit(1)
