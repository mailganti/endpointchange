"""Agents commands."""

import click
from unifiedtree.output import output, success, error, status_color, format_table


@click.group()
def agents():
    """Manage agents."""
    pass


@agents.command('list')
@click.option('--status', type=click.Choice(['all', 'online', 'offline']), default='all', help='Filter by status')
@click.option('--env', type=click.Choice(['all', 'DEV', 'TEST', 'PROD']), default='all', help='Filter by environment')
@click.pass_context
def list_agents(ctx, status, env):
    """List all registered agents."""
    client = ctx.obj['client']
    
    try:
        agents_list = client.get('/agents')
        
        # Filter by status
        if status != 'all':
            agents_list = [a for a in agents_list if a.get('status', '').lower() == status.lower()]
        
        # Filter by environment
        if env != 'all':
            agents_list = [a for a in agents_list if a.get('environment', '').upper() == env.upper()]
        
        if not agents_list:
            click.echo("No agents found.")
            return
        
        # Add colored status
        for agent in agents_list:
            agent['status_display'] = status_color(agent.get('status', 'unknown'))
        
        output(ctx, agents_list, 
               columns=['agent_id', 'hostname', 'environment', 'status', 'last_seen'],
               headers=['ID', 'Hostname', 'Env', 'Status', 'Last Seen'])
        
        # Summary
        online = sum(1 for a in agents_list if a.get('status') == 'online')
        click.echo(f"\nTotal: {len(agents_list)} agents ({online} online)")
        
    except Exception as e:
        error(f"Failed to list agents: {e}")
        raise SystemExit(1)


@agents.command('status')
@click.argument('agent_id', required=False)
@click.pass_context
def agent_status(ctx, agent_id):
    """Show agent status (all or specific agent)."""
    client = ctx.obj['client']
    
    try:
        if agent_id:
            # Single agent
            agent = client.get(f'/agents/{agent_id}')
            click.echo(f"Agent:       {agent.get('agent_id')}")
            click.echo(f"Hostname:    {agent.get('hostname')}")
            click.echo(f"Environment: {agent.get('environment')}")
            click.echo(f"Status:      {status_color(agent.get('status', 'unknown'))}")
            click.echo(f"Last Seen:   {agent.get('last_seen')}")
            click.echo(f"IP Address:  {agent.get('ip_address', 'N/A')}")
        else:
            # Summary of all agents
            agents_list = client.get('/agents')
            
            total = len(agents_list)
            online = sum(1 for a in agents_list if a.get('status') == 'online')
            offline = total - online
            
            click.echo("Agent Status Summary")
            click.echo("=" * 30)
            click.echo(f"Total:   {total}")
            click.echo(f"Online:  {click.style(str(online), fg='green')}")
            click.echo(f"Offline: {click.style(str(offline), fg='red')}")
            
            # By environment
            envs = {}
            for a in agents_list:
                env = a.get('environment', 'UNKNOWN')
                if env not in envs:
                    envs[env] = {'total': 0, 'online': 0}
                envs[env]['total'] += 1
                if a.get('status') == 'online':
                    envs[env]['online'] += 1
            
            if envs:
                click.echo("\nBy Environment:")
                for env, counts in sorted(envs.items()):
                    click.echo(f"  {env}: {counts['online']}/{counts['total']} online")
    
    except Exception as e:
        error(f"Failed to get agent status: {e}")
        raise SystemExit(1)


@agents.command('ping')
@click.argument('agent_id')
@click.pass_context
def ping_agent(ctx, agent_id):
    """Ping an agent to check connectivity."""
    client = ctx.obj['client']
    
    click.echo(f"Pinging agent {agent_id}...")
    
    try:
        result = client.post(f'/agents/{agent_id}/ping')
        
        if result.get('success'):
            success(f"Agent {agent_id} is reachable ({result.get('latency_ms', '?')}ms)")
        else:
            error(f"Agent {agent_id} did not respond")
            
    except Exception as e:
        error(f"Ping failed: {e}")
        raise SystemExit(1)
