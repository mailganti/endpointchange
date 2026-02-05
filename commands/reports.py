"""Reports commands."""

import click
import time
from unifiedtree.output import output, success, error, info


@click.group()
def reports():
    """Manage and run reports."""
    pass


@reports.command('list')
@click.option('--category', '-c', help='Filter by category')
@click.pass_context
def list_reports(ctx, category):
    """List available reports."""
    client = ctx.obj['client']
    
    try:
        reports_list = client.get('/reports/scripts')
        
        if category:
            reports_list = [r for r in reports_list if r.get('category', '').lower() == category.lower()]
        
        if not reports_list:
            click.echo("No reports found.")
            return
        
        output(ctx, reports_list,
               columns=['script_id', 'name', 'category', 'description'],
               headers=['ID', 'Name', 'Category', 'Description'])
        
        click.echo(f"\nTotal: {len(reports_list)} reports")
        
    except Exception as e:
        error(f"Failed to list reports: {e}")
        raise SystemExit(1)


@reports.command('show')
@click.argument('report_id')
@click.pass_context
def show_report(ctx, report_id):
    """Show report details including parameters."""
    client = ctx.obj['client']
    
    try:
        report = client.get(f'/reports/scripts/{report_id}')
        
        click.echo(f"Report ID:   {report.get('script_id')}")
        click.echo(f"Name:        {report.get('name')}")
        click.echo(f"Category:    {report.get('category', 'General')}")
        click.echo(f"Path:        {report.get('script_path')}")
        click.echo(f"Timeout:     {report.get('timeout', 300)}s")
        click.echo(f"Description: {report.get('description', 'N/A')}")
        
        params = report.get('parameters', [])
        if params:
            click.echo("\nParameters:")
            for p in params:
                required = " (required)" if p.get('required') else ""
                default = f" [default: {p.get('default')}]" if p.get('default') is not None else ""
                click.echo(f"  --{p.get('name')}: {p.get('label', p.get('name'))}{required}{default}")
        
    except Exception as e:
        error(f"Failed to get report: {e}")
        raise SystemExit(1)


@reports.command('run')
@click.argument('report_id')
@click.option('--agent', '-a', required=True, help='Agent ID to run on')
@click.option('--param', '-p', multiple=True, help='Parameter in key=value format')
@click.option('--wait/--no-wait', default=True, help='Wait for completion and show output')
@click.pass_context
def run_report(ctx, report_id, agent, param, wait):
    """Run a report on an agent."""
    client = ctx.obj['client']
    
    # Parse parameters
    params = {}
    for p in param:
        if '=' in p:
            key, value = p.split('=', 1)
            params[key] = value
        else:
            error(f"Invalid parameter format: {p} (use key=value)")
            raise SystemExit(1)
    
    try:
        # Start report execution
        data = {
            'script_id': report_id,
            'agent_id': agent,
            'parameters': params
        }
        
        result = client.post('/reports/run', data)
        run_id = result.get('run_id')
        
        if not wait:
            success(f"Report started: {run_id}")
            return
        
        info(f"Running report {report_id} on {agent}...")
        
        # Poll for completion
        max_wait = 300  # 5 minutes
        poll_interval = 2
        elapsed = 0
        
        while elapsed < max_wait:
            status_result = client.get(f'/reports/runs/{run_id}')
            status = status_result.get('status')
            
            if status == 'completed':
                success("Report completed")
                click.echo("\n--- Output ---")
                click.echo(status_result.get('output', '(no output)'))
                return
            elif status == 'failed':
                error("Report failed")
                click.echo(status_result.get('error', '(no error details)'))
                raise SystemExit(1)
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        error("Report timed out waiting for completion")
        raise SystemExit(1)
        
    except Exception as e:
        error(f"Failed to run report: {e}")
        raise SystemExit(1)


@reports.command('register')
@click.option('--id', 'script_id', required=True, help='Report ID')
@click.option('--name', required=True, help='Display name')
@click.option('--path', required=True, help='Script path on agent')
@click.option('--category', default='General', help='Report category')
@click.option('--timeout', default=300, help='Execution timeout in seconds')
@click.option('--description', '-d', help='Report description')
@click.pass_context
def register_report(ctx, script_id, name, path, category, timeout, description):
    """Register a new report."""
    client = ctx.obj['client']
    
    try:
        data = {
            'script_id': script_id,
            'name': name,
            'script_path': path,
            'category': category,
            'timeout': timeout,
        }
        if description:
            data['description'] = description
        
        result = client.post('/reports/scripts/register', data)
        success(f"Report '{script_id}' registered")
        
    except Exception as e:
        error(f"Failed to register report: {e}")
        raise SystemExit(1)
