"""Workflows commands."""

import click
from unifiedtree.output import output, success, error, status_color


@click.group()
def workflows():
    """Manage workflows."""
    pass


@workflows.command('list')
@click.option('--status', type=click.Choice(['all', 'pending', 'approved', 'denied', 'executed', 'failed']), 
              default='all', help='Filter by status')
@click.option('--limit', '-n', default=20, help='Maximum number of workflows to show')
@click.pass_context
def list_workflows(ctx, status, limit):
    """List workflows."""
    client = ctx.obj['client']
    
    try:
        workflows_list = client.get('/workflows')
        
        # Filter by status
        if status != 'all':
            workflows_list = [w for w in workflows_list if w.get('status', '').lower() == status.lower()]
        
        # Limit results
        workflows_list = workflows_list[:limit]
        
        if not workflows_list:
            click.echo("No workflows found.")
            return
        
        output(ctx, workflows_list,
               columns=['workflow_id', 'script_id', 'status', 'requestor', 'created_at'],
               headers=['ID', 'Script', 'Status', 'Requestor', 'Created'])
        
        click.echo(f"\nShowing {len(workflows_list)} workflows")
        
    except Exception as e:
        error(f"Failed to list workflows: {e}")
        raise SystemExit(1)


@workflows.command('show')
@click.argument('workflow_id')
@click.pass_context
def show_workflow(ctx, workflow_id):
    """Show workflow details."""
    client = ctx.obj['client']
    
    try:
        wf = client.get(f'/workflows/{workflow_id}')
        
        click.echo(f"Workflow:    {wf.get('workflow_id')}")
        click.echo(f"Script:      {wf.get('script_id')}")
        click.echo(f"Status:      {status_color(wf.get('status', 'unknown'))}")
        click.echo(f"Requestor:   {wf.get('requestor')}")
        click.echo(f"Approver:    {wf.get('approver', 'N/A')}")
        click.echo(f"Created:     {wf.get('created_at')}")
        click.echo(f"Updated:     {wf.get('updated_at', 'N/A')}")
        
        agents = wf.get('target_agents', [])
        if agents:
            click.echo(f"Agents:      {', '.join(agents)}")
        
        if wf.get('denial_reason'):
            click.echo(f"Denied:      {wf.get('denial_reason')}")
            
    except Exception as e:
        error(f"Failed to get workflow: {e}")
        raise SystemExit(1)


@workflows.command('create')
@click.option('--script', '-s', required=True, help='Script ID to execute')
@click.option('--agent', '-a', multiple=True, required=True, help='Target agent ID (can specify multiple)')
@click.option('--approver', '-p', required=True, help='Approver email')
@click.option('--email', '-e', help='Your email for notifications')
@click.pass_context
def create_workflow(ctx, script, agent, approver, email):
    """Create a new workflow."""
    client = ctx.obj['client']
    
    try:
        data = {
            'script_id': script,
            'target_agents': list(agent),
            'approver_email': approver,
        }
        if email:
            data['requestor_email'] = email
        
        result = client.post('/workflows', data)
        
        workflow_id = result.get('workflow_id')
        success(f"Workflow created: {workflow_id}")
        click.echo(f"Status: {status_color('pending')}")
        click.echo(f"Awaiting approval from: {approver}")
        
    except Exception as e:
        error(f"Failed to create workflow: {e}")
        raise SystemExit(1)


@workflows.command('approve')
@click.argument('workflow_id')
@click.pass_context
def approve_workflow(ctx, workflow_id):
    """Approve a pending workflow."""
    client = ctx.obj['client']
    
    try:
        result = client.post(f'/workflows/{workflow_id}/approve')
        success(f"Workflow {workflow_id} approved")
        
    except Exception as e:
        error(f"Failed to approve workflow: {e}")
        raise SystemExit(1)


@workflows.command('deny')
@click.argument('workflow_id')
@click.option('--reason', '-r', required=True, help='Reason for denial')
@click.pass_context
def deny_workflow(ctx, workflow_id, reason):
    """Deny a pending workflow."""
    client = ctx.obj['client']
    
    try:
        result = client.post(f'/workflows/{workflow_id}/deny', {'reason': reason})
        success(f"Workflow {workflow_id} denied")
        
    except Exception as e:
        error(f"Failed to deny workflow: {e}")
        raise SystemExit(1)


@workflows.command('execute')
@click.argument('workflow_id')
@click.option('--wait', '-w', is_flag=True, help='Wait for execution to complete')
@click.pass_context
def execute_workflow(ctx, workflow_id, wait):
    """Execute an approved workflow."""
    client = ctx.obj['client']
    
    try:
        result = client.post(f'/workflows/{workflow_id}/execute')
        success(f"Workflow {workflow_id} execution started")
        
        if wait:
            click.echo("Waiting for completion...")
            # TODO: Poll for status
            
    except Exception as e:
        error(f"Failed to execute workflow: {e}")
        raise SystemExit(1)
