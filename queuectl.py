#!/usr/bin/env python3
"""
QueueCTL - CLI-based background job queue system
"""

import json
import signal
import sys
import time
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from src.job_queue import JobQueue
from src.worker_manager import WorkerManager
from src.config import Config
from src.banner import show_startup_screen, show_welcome_message
from src.interactive_shell import start_interactive_shell

app = typer.Typer(
    help="CLI-based background job queue system",
    no_args_is_help=False,  # Allow callback to run when no args provided
    add_completion=False,
    invoke_without_command=True  # Enable callback without subcommand
)
worker_app = typer.Typer(help="Worker management commands")
dlq_app = typer.Typer(help="Dead Letter Queue management")
config_app = typer.Typer(help="Configuration management")

app.add_typer(worker_app, name="worker")
app.add_typer(dlq_app, name="dlq")
app.add_typer(config_app, name="config")

console = Console()
job_queue = JobQueue()
worker_manager = WorkerManager(job_queue)
config = Config()

# Global worker manager for signal handling
_global_worker_manager = None


def signal_handler(signum, frame):
    """Handle graceful shutdown on SIGINT"""
    if _global_worker_manager:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
        _global_worker_manager.stop_all()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version information"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start interactive shell")
):
    """
    QueueCTL - CLI-based background job queue system
    
    A production-grade job queue with workers, retries, and Dead Letter Queue.
    """
    if version:
        console.print("[#bbfa01]QueueCTL v1.0.0[/#bbfa01]")
        console.print("CLI-based Background Job Queue System")
        return
    
    if interactive:
        # Start interactive shell
        start_interactive_shell()
        return
    
    if ctx.invoked_subcommand is None:
        # Show startup screen with ASCII art and automatically start interactive shell
        show_startup_screen()
        
        # Automatically start interactive shell
        start_interactive_shell()
        return


@app.command()
def enqueue(
    job_json: str = typer.Argument(..., help="Job JSON string"),
    priority: Optional[int] = typer.Option(None, "--priority", "-p", help="Job priority (higher numbers = higher priority)")
):
    """
    Add a new job to the queue.
    
    Windows Example: queuectl enqueue "{\"id\":\"job1\",\"command\":\"echo Hello\"}" --priority 10
    Linux/Mac Example: queuectl enqueue '{"id":"job1","command":"echo Hello"}' --priority 10
    """
    try:
        # Handle Windows command line JSON parsing
        job_json = job_json.strip()
        
        # Remove outer single quotes if present (Windows CMD issue)
        if job_json.startswith("'") and job_json.endswith("'"):
            job_json = job_json[1:-1]
        
        # Try to fix common Windows JSON issues
        if not job_json.startswith('{'):
            # If it doesn't start with {, it might be malformed
            console.print(f"[red]Error:[/red] JSON must start with '{{'. Got: {job_json[:20]}...")
            console.print("[dim]Windows Tip: Use double quotes like this:[/dim]")
            console.print('[dim]python queuectl.py enqueue "{\\"id\\":\\"test\\",\\"command\\":\\"echo hello\\"}"[/dim]')
            raise typer.Exit(1)
        
        job_data = json.loads(job_json)
        
        # Add priority from command line option if provided
        if priority is not None:
            job_data['priority'] = priority
        
        # Validate required fields
        if "command" not in job_data:
            raise typer.BadParameter("Job must contain 'command' field")
        
        job = job_queue.enqueue(job_data)
        console.print(f"[green]OK[/green] Job enqueued: [bold]{job['id']}[/bold]")
        console.print(f"  Command: {job['command']}")
        console.print(f"  Priority: {job['priority']}")
        console.print(f"  Max retries: {job['max_retries']}")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON format: {e}")
        console.print("[dim]Example: python queuectl.py enqueue '{\"id\":\"test\",\"command\":\"echo hello\"}'[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error enqueuing job:[/red] {e}")
        raise typer.Exit(1)





@worker_app.command("start")
def start_workers(
    count: int = typer.Option(1, "--count", "-c", help="Number of workers to start")
):
    """Start worker processes"""
    global _global_worker_manager
    _global_worker_manager = worker_manager
    
    try:
        if count < 1:
            console.print("[red]Error:[/red] Worker count must be at least 1")
            raise typer.Exit(1)
            
        worker_manager.start(count)
        console.print(f"[green]OK[/green] Started [bold]{count}[/bold] worker(s)")
        console.print("[dim]Press Ctrl+C to stop workers gracefully[/dim]")
        
        # Keep the main process alive
        worker_manager.wait_for_workers()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping workers...[/yellow]")
        worker_manager.stop_all()
    except Exception as e:
        console.print(f"[red]Error starting workers:[/red] {e}")
        raise typer.Exit(1)


@worker_app.command("stop")
def stop_workers():
    """Stop all workers gracefully"""
    try:
        active_count = worker_manager.get_active_worker_count()
        if active_count == 0:
            console.print("[yellow]No active workers to stop[/yellow]")
            return
            
        worker_manager.stop_all()
        console.print(f"[green]OK[/green] Stopped all workers")
        
    except Exception as e:
        console.print(f"[red]Error stopping workers:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status():
    """Show system status"""
    try:
        job_status = job_queue.get_status()
        active_workers = worker_manager.get_active_worker_count()
        
        # Create status table
        table = Table(title="QueueCTL Status", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        table.add_row("Active Workers", str(active_workers))
        table.add_row("Pending Jobs", str(job_status.get('pending', 0)))
        table.add_row("Processing Jobs", str(job_status.get('processing', 0)))
        table.add_row("Completed Jobs", str(job_status.get('completed', 0)))
        table.add_row("Failed Jobs", str(job_status.get('failed', 0)))
        table.add_row("Dead Jobs (DLQ)", str(job_status.get('dead', 0)))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error getting status:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_jobs(
    state: Optional[str] = typer.Option(None, "--state", "-s", help="Filter by job state")
):
    """List jobs, optionally filtered by state"""
    try:
        jobs = job_queue.list_jobs(state)
        
        if not jobs:
            if state:
                console.print(f"[yellow]No jobs found with state: {state}[/yellow]")
            else:
                console.print("[yellow]No jobs found[/yellow]")
            return
        
        # Check if we're showing scheduled jobs specifically
        has_scheduled_jobs = any(job['state'] == 'scheduled' for job in jobs)
        showing_only_scheduled = state == 'scheduled'
        
        # Create compact jobs table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("St", style="green", width=3)  # Compressed State
        table.add_column("Command", style="white")  # Let it expand
        table.add_column("T", justify="center", width=3)  # Compressed Tries
        
        if showing_only_scheduled:
            # For scheduled jobs only, show run_at time
            table.add_column("Scheduled", style="yellow", width=8)
        elif has_scheduled_jobs:
            # Mixed jobs, show both created and scheduled times
            table.add_column("Created", style="dim", width=8)
            table.add_column("Scheduled", style="yellow", width=8)
        else:
            # No scheduled jobs, just show created time
            table.add_column("Created", style="dim", width=8)
        
        for job in jobs:
            # Color code states with abbreviations
            state_abbrev = {
                'pending': ('P', 'yellow'),
                'processing': ('R', 'blue'),  # Running
                'completed': ('C', 'green'),
                'failed': ('F', 'red'),
                'dead': ('D', 'red bold'),
                'scheduled': ('S', 'yellow')
            }
            
            state_short, state_color = state_abbrev.get(job['state'], (job['state'][:1].upper(), 'white'))
            
            # Compact tries format (just the numbers)
            tries_str = f"{job['attempts']}/{job['max_retries']}"
            
            # Multi-line date/time format
            def format_datetime_compact(dt_str):
                if not dt_str:
                    return "-"
                # Extract date and time parts
                date_part = dt_str[5:10]  # MM-DD
                time_part = dt_str[11:16]  # HH:MM
                return f"{date_part}\n{time_part}"
            
            # Multi-line command format for better space usage
            def format_command_multiline(cmd, max_width=50):
                if len(cmd) <= max_width:
                    return cmd
                
                # Try to break at word boundaries
                words = cmd.split()
                lines = []
                current_line = ""
                
                for word in words:
                    if len(current_line + " " + word) <= max_width:
                        current_line += (" " + word) if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Limit to 2 lines max
                if len(lines) > 2:
                    lines = lines[:2]
                    lines[1] = lines[1][:max_width-3] + "..."
                
                return "\n".join(lines)
            
            created_compact = format_datetime_compact(job['created_at'])
            
            if showing_only_scheduled:
                # Show only scheduled time for scheduled jobs
                if job.get('run_at'):
                    scheduled_compact = format_datetime_compact(job['run_at'])
                else:
                    scheduled_compact = "-\n-"
                
                table.add_row(
                    job['id'],
                    f"[{state_color}]{state_short}[/{state_color}]",
                    format_command_multiline(job['command']),
                    tries_str,
                    scheduled_compact
                )
            elif has_scheduled_jobs:
                # Show both created and scheduled times
                if job.get('run_at'):
                    scheduled_compact = format_datetime_compact(job['run_at'])
                else:
                    scheduled_compact = "-\n-"
                
                table.add_row(
                    job['id'],
                    f"[{state_color}]{state_short}[/{state_color}]",
                    format_command_multiline(job['command']),
                    tries_str,
                    created_compact,
                    scheduled_compact
                )
            else:
                # Show only created time
                table.add_row(
                    job['id'],
                    f"[{state_color}]{state_short}[/{state_color}]",
                    format_command_multiline(job['command']),
                    tries_str,
                    created_compact
                )
        
        console.print(table)
        
        # Add state legend
        console.print(f"\n[dim]State Legend: [yellow]P[/yellow]=Pending, [blue]R[/blue]=Running, [green]C[/green]=Completed, [red]F[/red]=Failed, [red bold]D[/red bold]=Dead, [yellow]S[/yellow]=Scheduled[/dim]")
        
        # Add state-specific information
        if state:
            state_info = {
                'pending': 'Jobs ready to be processed by workers',
                'processing': 'Jobs currently being executed',
                'completed': 'Jobs that finished successfully',
                'failed': 'Jobs that failed but will be retried',
                'dead': 'Jobs that failed permanently (Dead Letter Queue)',
                'scheduled': 'Jobs waiting for their scheduled time'
            }
            if state in state_info:
                console.print(f"[dim]Showing {state} jobs: {state_info[state]}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing jobs:[/red] {e}")
        raise typer.Exit(1)


@dlq_app.command("list")
def list_dlq():
    """List jobs in Dead Letter Queue"""
    try:
        jobs = job_queue.list_jobs('dead')
        
        if not jobs:
            console.print("[yellow]No jobs in Dead Letter Queue[/yellow]")
            return
        
        table = Table(title="Dead Letter Queue", show_header=True, header_style="bold red")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Command", style="white", max_width=25)
        table.add_column("Attempts", justify="center", width=8)
        table.add_column("Last Error", style="red", max_width=30)
        table.add_column("Failed At", style="dim", width=16)
        
        for job in jobs:
            error_preview = (job.get('error', 'Unknown error')[:40] + '...' 
                           if job.get('error') and len(job.get('error', '')) > 40 
                           else job.get('error', 'Unknown error'))
            
            failed_at = job['updated_at'][:19].replace('T', ' ')
            
            table.add_row(
                job['id'],
                job['command'][:30] + ('...' if len(job['command']) > 30 else ''),
                str(job['attempts']),
                error_preview,
                failed_at
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing DLQ:[/red] {e}")
        raise typer.Exit(1)


@dlq_app.command("retry")
def retry_dlq_job(job_id: str = typer.Argument(..., help="Job ID to retry")):
    """Retry a job from Dead Letter Queue (supports partial ID matching)"""
    try:
        # First try exact match
        try:
            job_queue.retry_from_dlq(job_id)
            console.print(f"[green]OK[/green] Job [bold]{job_id}[/bold] moved back to pending queue")
            return
        except ValueError:
            # If exact match fails, try partial matching
            pass
        
        # Find jobs that match the partial ID
        dlq_jobs = job_queue.list_jobs(state='dead')
        matching_jobs = [job for job in dlq_jobs if job_id in job['id']]
        
        if not matching_jobs:
            console.print(f"[red]Error:[/red] No DLQ job found matching '{job_id}'")
            console.print("[dim]Use 'dlq list' to see available jobs[/dim]")
            raise typer.Exit(1)
        elif len(matching_jobs) == 1:
            # Exactly one match - retry it
            full_job_id = matching_jobs[0]['id']
            console.print(f"[dim]Found matching job: {full_job_id}[/dim]")
            job_queue.retry_from_dlq(full_job_id)
            console.print(f"[green]OK[/green] Job [bold]{full_job_id}[/bold] moved back to pending queue")
        else:
            # Multiple matches - show options
            console.print(f"[yellow]Multiple jobs match '{job_id}':[/yellow]")
            for i, job in enumerate(matching_jobs, 1):
                console.print(f"  {i}. {job['id']}")
            console.print("[dim]Please use a more specific job ID[/dim]")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]Error retrying job:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("set")
def set_config(key: str = typer.Argument(..., help="Configuration key"), 
               value: str = typer.Argument(..., help="Configuration value")):
    """Set configuration value"""
    try:
        # Validate configuration keys
        valid_keys = ['max-retries', 'backoff-base']
        if key not in valid_keys:
            console.print(f"[red]Error:[/red] Invalid config key")
            console.print(f"[yellow]Valid keys:[/yellow] [cyan]{', '.join(valid_keys)}[/cyan]")
            raise typer.Exit(1)
        
        # Validate values
        if key == 'max-retries':
            try:
                int_value = int(value)
                if int_value < 0:
                    raise ValueError("max-retries must be non-negative")
            except ValueError as e:
                console.print(f"[red]Error:[/red] max-retries must be a non-negative integer")
                raise typer.Exit(1)
        elif key == 'backoff-base':
            try:
                float_value = float(value)
                if float_value <= 1:
                    raise ValueError("backoff-base must be greater than 1")
            except ValueError as e:
                console.print(f"[red]Error:[/red] backoff-base must be a number greater than 1")
                raise typer.Exit(1)
        
        config.set(key, value)
        console.print(f"[green]OK[/green] Configuration updated: [bold]{key}[/bold] = {value}")
        
    except Exception as e:
        console.print(f"[red]Error setting config:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("get")
def get_config(key: str = typer.Argument(..., help="Configuration key")):
    """Get configuration value"""
    try:
        # Validate configuration key
        valid_keys = ['max-retries', 'backoff-base']
        if key not in valid_keys:
            console.print(f"[red]'{key}' is not a valid config key[/red]")
            console.print(f"[yellow]Valid keys:[/yellow] [cyan]{', '.join(valid_keys)}[/cyan]")
            console.print("[yellow]Type[/yellow] [green]'config list'[/green] [yellow]to see all available keys[/yellow]")
            raise typer.Exit(1)
        
        value = config.get(key)
        console.print(f"[cyan]{key}[/cyan] = [bold]{value}[/bold]")
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error getting config:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("list")
def list_config():
    """List all configuration values"""
    try:
        configs = config.list_all()
        
        if not configs:
            console.print("[yellow]No configuration values set[/yellow]")
            return
        
        table = Table(title="Configuration", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Description", style="dim")
        
        descriptions = {
            'max-retries': 'Maximum number of retry attempts for failed jobs',
            'backoff-base': 'Base for exponential backoff calculation (delay = base^attempts)'
        }
        
        for key, value in configs.items():
            table.add_row(key, str(value), descriptions.get(key, ''))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing config:[/red] {e}")
        raise typer.Exit(1)



@app.command("shell")
def interactive_shell():
    """Start interactive shell mode"""
    start_interactive_shell()


@app.command("dashboard")
def web_dashboard(
    host: str = typer.Option("localhost", "--host", help="Dashboard host"),
    port: int = typer.Option(8080, "--port", help="Dashboard port")
):
    """Start web dashboard for monitoring"""
    try:
        from src.web_dashboard import start_dashboard
        
        console.print(f"[#bbfa01] Starting web dashboard at http://{host}:{port}[/#bbfa01]")
        dashboard = start_dashboard(job_queue, config, host, port)
        
        console.print("[dim]Press Ctrl+C to stop the dashboard[/dim]")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dashboard.stop()
            console.print("\n[#bbfa01]Dashboard stopped[/#bbfa01]")
            
    except ImportError:
        console.print("[red]Error: Web dashboard dependencies not available[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error starting dashboard:[/red] {e}")
        raise typer.Exit(1)


@app.command("metrics")
def show_metrics(
    hours: int = typer.Option(24, "--hours", help="Hours of metrics to show")
):
    """Show system metrics and statistics"""
    try:
        metrics = job_queue.get_system_metrics(hours)
        
        console.print(f"\n[#bbfa01] System Metrics (Last {hours} hours)[/#bbfa01]")
        
        # Job counts
        table = Table(title="Job Counts", show_header=True, header_style="#bbfa01 bold")
        table.add_column("State", style="#bbfa01")
        table.add_column("Count", justify="right", style="white")
        
        for state, count in metrics['job_counts'].items():
            table.add_row(state.title(), str(count))
        
        console.print(table)
        
        # Performance metrics
        console.print(f"\n[#bbfa01]Performance:[/#bbfa01]")
        console.print(f"  Average execution time: {metrics['avg_execution_time_ms']:.0f}ms")
        console.print(f"  Jobs per hour: {metrics['jobs_per_hour']:.1f}")
        console.print(f"  Success rate: {metrics['success_rate_percent']:.1f}%")
        
    except Exception as e:
        console.print(f"[red]Error getting metrics:[/red] {e}")
        raise typer.Exit(1)



if __name__ == "__main__":
    app()