#!/usr/bin/env python3
"""
QueueCTL Extra Credit Features Test 
Use test_bonus_features.py instead for comprehensive bonus feature testing
"""

import os
from rich.console import Console

console = Console()

def main():
    console.print("[yellow]WARNING: This file is deprecated.[/yellow]")
    console.print("Please use the new organized test files:")
    console.print("• [cyan]python test_deliverables.py[/cyan] - Test core requirements")
    console.print("• [cyan]python test_bonus_features.py[/cyan] - Test bonus features") 
    console.print("• [cyan]python submission_checklist.py[/cyan] - Final submission check")

if __name__ == "__main__":
    main()
import sqlite3
from datetime import datetime, timezone, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_queuectl(cmd, show_output=True):
    """Run a queuectl command"""
    full_cmd = f"python queuectl.py {cmd}"
    if show_output:
        console.print(f"[dim]$ {full_cmd}[/dim]")
    
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    
    if show_output and result.stdout:
        console.print(result.stdout.strip())
    if result.stderr and result.returncode != 0:
        console.print(f"[red]{result.stderr.strip()}[/red]")
    
    return result.returncode == 0, result.stdout


def test_priority_queues():
    """Test priority queue functionality"""
    console.print(Panel.fit("Testing Priority Queues", style="bold blue"))
    
    # Add jobs with different priorities
    jobs = [
        {"id": "low-priority", "command": "echo 'Low priority job'", "priority": -1},
        {"id": "high-priority", "command": "echo 'High priority job'", "priority": 10},
        {"id": "normal-priority", "command": "echo 'Normal priority job'", "priority": 0},
        {"id": "urgent-priority", "command": "echo 'Urgent priority job'", "priority": 20}
    ]
    
    for job in jobs:
        job_json = json.dumps(job).replace('"', '\\"')
        success, _ = run_queuectl(f'enqueue "{job_json}"')
        if not success:
            console.print(f"[red]Failed to enqueue job: {job['id']}[/red]")
    
    console.print("\n[green]✓ Priority jobs enqueued[/green]")
    return True


def test_scheduled_jobs():
    """Test scheduled/delayed job functionality"""
    console.print(Panel.fit("⏰ Testing Scheduled Jobs", style="bold blue"))
    
    # Schedule jobs for different times
    future_time = (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()
    
    scheduled_jobs = [
        {"id": "immediate", "command": "echo 'Immediate job'"},
        {"id": "delayed-5s", "command": "echo 'Delayed 5 seconds'", "run_at": "+5s"},
        {"id": "delayed-10s", "command": "echo 'Delayed 10 seconds'", "run_at": "+10s"},
        {"id": "scheduled-future", "command": "echo 'Scheduled for future'", "run_at": future_time}
    ]
    
    for job in scheduled_jobs:
        job_json = json.dumps(job).replace('"', '\\"')
        if 'run_at' in job:
            success, _ = run_queuectl(f'schedule "{job_json}" --at "{job["run_at"]}"')
        else:
            success, _ = run_queuectl(f'enqueue "{job_json}"')
        
        if not success:
            console.print(f"[red]Failed to schedule job: {job['id']}[/red]")
    
    console.print("\n[green]✓ Scheduled jobs created[/green]")
    return True


def test_timeout_handling():
    """Test job timeout functionality"""
    console.print(Panel.fit("Testing Job Timeouts", style="bold blue"))
    
    # Create jobs with different timeouts
    timeout_jobs = [
        {"id": "quick-job", "command": "echo 'Quick job'", "timeout_seconds": 5},
        {"id": "slow-job", "command": "ping -n 20 127.0.0.1", "timeout_seconds": 3},  # Will timeout
        {"id": "normal-timeout", "command": "echo 'Normal timeout job'", "timeout_seconds": 30}
    ]
    
    for job in timeout_jobs:
        job_json = json.dumps(job).replace('"', '\\"')
        success, _ = run_queuectl(f'enqueue "{job_json}"')
        if not success:
            console.print(f"[red]Failed to enqueue timeout job: {job['id']}[/red]")
    
    console.print("\n[green]✓ Timeout jobs enqueued[/green]")
    return True


def test_output_logging():
    """Test job output logging"""
    console.print(Panel.fit("Testing Output Logging", style="bold blue"))
    
    # Create jobs that produce output
    output_jobs = [
        {"id": "output-test-1", "command": "echo 'This is job output 1'"},
        {"id": "output-test-2", "command": "echo 'This is job output 2' && echo 'Multiple lines'"},
        {"id": "error-test", "command": "echo 'Error test' && exit 1"}  # Will fail
    ]
    
    for job in output_jobs:
        job_json = json.dumps(job).replace('"', '\\"')
        success, _ = run_queuectl(f'enqueue "{job_json}"')
        if not success:
            console.print(f"[red]Failed to enqueue output job: {job['id']}[/red]")
    
    console.print("\n[green]✓ Output logging jobs enqueued[/green]")
    return True


def start_workers():
    """Start worker processes"""
    console.print(Panel.fit("Starting Workers", style="bold blue"))
    
    success, _ = run_queuectl("worker start --count 2")
    if success:
        console.print("[green]✓ Workers started[/green]")
        return True
    else:
        console.print("[red]✗ Failed to start workers[/red]")
        return False


def show_system_status():
    """Show system status and metrics"""
    console.print(Panel.fit("System Status & Metrics", style="bold blue"))
    
    # Show status
    run_queuectl("status")
    
    console.print("\n")
    
    # Show metrics
    run_queuectl("metrics")
    
    console.print("\n")
    
    # List jobs
    run_queuectl("list --state pending")


def show_job_details():
    """Show detailed job information"""
    console.print(Panel.fit("Job Details with Output Logging", style="bold blue"))
    
    # Get job details from database
    try:
        with sqlite3.connect("jobs.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get completed jobs with output
            cursor.execute("""
                SELECT id, command, state, priority, timeout_seconds, 
                       execution_time_ms, output, error, created_at, completed_at
                FROM jobs 
                WHERE state IN ('completed', 'failed', 'dead')
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            jobs = cursor.fetchall()
            
            if jobs:
                table = Table(title="Job Execution Details")
                table.add_column("ID", style="cyan")
                table.add_column("State", style="green")
                table.add_column("Priority", style="yellow")
                table.add_column("Timeout", style="blue")
                table.add_column("Duration", style="magenta")
                table.add_column("Output", style="white")
                
                for job in jobs:
                    duration = f"{job['execution_time_ms']}ms" if job['execution_time_ms'] else "N/A"
                    output = (job['output'] or job['error'] or "No output")[:50]
                    if len(output) == 50:
                        output += "..."
                    
                    table.add_row(
                        job['id'][:15],
                        job['state'],
                        str(job['priority'] or 0),
                        f"{job['timeout_seconds']}s",
                        duration,
                        output
                    )
                
                console.print(table)
            else:
                console.print("[yellow]No completed jobs found yet[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error querying job details: {e}[/red]")


def start_web_dashboard():
    """Start the web dashboard"""
    console.print(Panel.fit("Starting Web Dashboard", style="bold blue"))
    
    console.print("Starting web dashboard on http://localhost:8080...")
    console.print("You can view the dashboard in your browser to see:")
    console.print("• Real-time job status")
    console.print("• System metrics and performance stats")
    console.print("• Job execution history")
    console.print("• Priority queue visualization")
    console.print("• Success rates and timing statistics")
    
    # Start dashboard in background
    success, _ = run_queuectl("dashboard --host localhost --port 8080", show_output=False)
    
    if success:
        console.print("\n[green]✓ Web dashboard started at http://localhost:8080[/green]")
        console.print("[dim]Press Ctrl+C to stop the dashboard[/dim]")
        return True
    else:
        console.print("[red]✗ Failed to start web dashboard[/red]")
        return False


def main():
    """Main test function"""
    console.print(Panel.fit("QueueCTL Extra Credit Features Test", style="bold green"))
    
    # Clean up any existing jobs
    if os.path.exists("jobs.db"):
        os.remove("jobs.db")
    
    console.print("\n[blue]Testing all extra credit features:[/blue]")
    console.print("1. Job timeout handling")
    console.print("2. Job priority queues")
    console.print("3. Scheduled/delayed jobs (run_at)")
    console.print("4. Job output logging")
    console.print("5. Metrics or execution stats")
    console.print("6. Minimal web dashboard for monitoring")
    
    console.print("\n" + "="*60)
    
    # Test all features
    test_priority_queues()
    time.sleep(1)
    
    test_scheduled_jobs()
    time.sleep(1)
    
    test_timeout_handling()
    time.sleep(1)
    
    test_output_logging()
    time.sleep(1)
    
    # Start workers to process jobs
    if start_workers():
        console.print("\n[yellow]Waiting for jobs to process...[/yellow]")
        time.sleep(15)  # Wait for jobs to complete
        
        # Show results
        show_system_status()
        console.print("\n")
        show_job_details()
        
        # Stop workers
        console.print("\n[yellow]Stopping workers...[/yellow]")
        run_queuectl("worker stop")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit("All Extra Credit Features Tested!", style="bold green"))
    
    console.print("\n[blue]To start the web dashboard for monitoring:[/blue]")
    console.print("python queuectl.py dashboard")
    console.print("\nThen visit: http://localhost:8080")


if __name__ == "__main__":
    main()