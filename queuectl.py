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
def enqueue(job_json: str = typer.Argument(..., help="Job JSON string")):
    """
    Add a new job to the queue.
    
    Windows Example: queuectl enqueue "{\"id\":\"job1\",\"command\":\"echo Hello\"}"
    Linux/Mac Example: queuectl enqueue '{"id":"job1","command":"echo Hello"}'
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
        
        # Validate required fields
        if "command" not in job_data:
            raise typer.BadParameter("Job must contain 'command' field")
        
        job = job_queue.enqueue(job_data)
        console.print(f"[green]OK[/green] Job enqueued: [bold]{job['id']}[/bold]")
        console.print(f"  Command: {job['command']}")
        console.print(f"  Max retries: {job['max_retries']}")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON format: {e}")
        console.print("[dim]Example: python queuectl.py enqueue '{\"id\":\"test\",\"command\":\"echo hello\"}'[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error enqueuing job:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def add(
    command: str = typer.Argument(..., help="Command to run"),
    job_id: str = typer.Option(None, "--id", help="Job ID (auto-generated if not provided)"),
    priority: int = typer.Option(0, "--priority", help="Job priority (higher = first)"),
    max_retries: int = typer.Option(3, "--retries", help="Maximum retry attempts")
):
    """
    Add a simple job to the queue (easier than JSON).
    
    Example: queuectl add "echo Hello World" --id test1
    """
    try:
        import uuid
        
        job_data = {
            "id": job_id or f"job_{str(uuid.uuid4())[:8]}",
            "command": command,
            "priority": priority,
            "max_retries": max_retries
        }
        
        job = job_queue.enqueue(job_data)
        console.print(f"[green]OK[/green] Job added: [bold]{job['id']}[/bold]")
        console.print(f"  Command: {job['command']}")
        console.print(f"  Priority: {job['priority']}")
        console.print(f"  Max retries: {job['max_retries']}")
        
    except Exception as e:
        console.print(f"[red]Error adding job:[/red] {e}")
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
        
        # Create jobs table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Command", style="white")
        table.add_column("Attempts", justify="center")
        table.add_column("Created", style="dim")
        
        for job in jobs:
            # Color code states
            state_color = {
                'pending': 'yellow',
                'processing': 'blue',
                'completed': 'green',
                'failed': 'red',
                'dead': 'red bold'
            }.get(job['state'], 'white')
            
            attempts_str = f"{job['attempts']}/{job['max_retries']}"
            created_str = job['created_at'][:19].replace('T', ' ')  # Format datetime
            
            table.add_row(
                job['id'],
                f"[{state_color}]{job['state']}[/{state_color}]",
                job['command'][:50] + ('...' if len(job['command']) > 50 else ''),
                attempts_str,
                created_str
            )
        
        console.print(table)
        
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
        table.add_column("ID", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Attempts", justify="center")
        table.add_column("Last Error", style="red")
        table.add_column("Failed At", style="dim")
        
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
    """Retry a job from Dead Letter Queue"""
    try:
        job_queue.retry_from_dlq(job_id)
        console.print(f"[green]OK[/green] Job [bold]{job_id}[/bold] moved back to pending queue")
        
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
            console.print(f"[red]Error:[/red] Invalid config key. Valid keys: {', '.join(valid_keys)}")
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
        value = config.get(key)
        console.print(f"[cyan]{key}[/cyan] = [bold]{value}[/bold]")
        
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


@app.command("welcome")
def show_welcome():
    """Show the QueueCTL welcome screen and quick help"""
    show_startup_screen()


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
        console.print(f"\n[#bbfa01]⚡ Performance:[/#bbfa01]")
        console.print(f"  Average execution time: {metrics['avg_execution_time_ms']:.0f}ms")
        console.print(f"  Jobs per hour: {metrics['jobs_per_hour']:.1f}")
        console.print(f"  Success rate: {metrics['success_rate_percent']:.1f}%")
        
    except Exception as e:
        console.print(f"[red]Error getting metrics:[/red] {e}")
        raise typer.Exit(1)


@app.command("schedule")
def schedule_job(
    job_json: str = typer.Argument(..., help="Job JSON string"),
    run_at: str = typer.Option(None, "--at", help="When to run (ISO format or +5m, +1h, etc.)")
):
    """Schedule a job to run at a specific time"""
    try:
        job_data = json.loads(job_json.strip().strip("'\""))
        
        if run_at:
            job_data['run_at'] = run_at
        
        job = job_queue.enqueue(job_data)
        
        if job['state'] == 'scheduled':
            console.print(f"[green]OK[/green] Job scheduled: [bold]{job['id']}[/bold]")
            console.print(f"  Will run at: {job['run_at']}")
        else:
            console.print(f"[green]OK[/green] Job enqueued: [bold]{job['id']}[/bold]")
        
        console.print(f"  Command: {job['command']}")
        console.print(f"  Priority: {job['priority']}")
        
    except Exception as e:
        console.print(f"[red]Error scheduling job:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()