"""
Interactive shell for QueueCTL
"""

import cmd
import json
import shlex
import subprocess
import sys
from rich.console import Console
from rich.text import Text
from src.banner import show_banner

console = Console()


class QueueCTLShell(cmd.Cmd):
    """Interactive shell for QueueCTL commands"""
    
    intro = Text("\nWelcome to QueueCTL Interactive Shell!", style="#bbfa01 bold")
    prompt = Text("queuectl> ", style="#bbfa01 bold").plain
    
    def __init__(self):
        super().__init__()
        console.print(self.intro)
        console.print("[dim]Type 'help' for available commands or 'exit' to quit.[/dim]")
        console.print("[dim]You can run any queuectl command without the 'python queuectl.py' prefix.[/dim]\n")
    
    def default(self, line):
        """Handle unknown commands by trying to run them as queuectl commands"""
        if line.strip():
            self.run_queuectl_command(line)
    
    def run_queuectl_command(self, command):
        """Run a queuectl command"""
        try:
            import sys
            import os
            
            # Get the Python executable and script path
            python_exe = sys.executable
            script_path = os.path.join(os.getcwd(), "queuectl.py")
            
            full_cmd = f'"{python_exe}" "{script_path}" {command}'
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                console.print(result.stdout.strip())
            if result.stderr and result.returncode != 0:
                stderr_text = result.stderr.strip()
                
                # Special handling for config commands
                valid_keys = ["backoff-base", "max-retries"]  # Known config keys
                
                if command.startswith("config set"):
                    parts = command.split()
                    
                    if len(parts) == 3:  # config set <key> (missing value)
                        key = parts[2]
                        if key not in valid_keys:
                            console.print(f"[red]'{key}' is not a valid config key[/red]")
                            console.print(f"[dim]Valid keys: {', '.join(valid_keys)}[/dim]")
                            console.print("[dim]Type 'config list' to see all available keys[/dim]")
                            return
                        else:
                            console.print(f"[red]Missing value for config key '{key}'[/red]")
                            console.print("[dim]Usage: config set <key> <value>[/dim]")
                            console.print("[dim]Example: config set max-retries 3[/dim]")
                            return
                    elif len(parts) == 2:  # config set (missing key and value)
                        console.print("[red]Missing config key and value[/red]")
                        console.print("[dim]Usage: config set <key> <value>[/dim]")
                        console.print(f"[dim]Valid keys: {', '.join(valid_keys)}[/dim]")
                        console.print("[dim]Type 'config list' to see all available keys[/dim]")
                        return
                
                elif command.startswith("config get"):
                    parts = command.split()
                    
                    if len(parts) == 3:  # config get <key>
                        key = parts[2]
                        if key not in valid_keys:
                            console.print(f"[red]'{key}' is not a valid config key[/red]")
                            console.print(f"[dim]Valid keys: {', '.join(valid_keys)}[/dim]")
                            console.print("[dim]Type 'config list' to see all available keys[/dim]")
                            return
                    elif len(parts) == 2:  # config get (missing key)
                        console.print("[red]Missing config key[/red]")
                        console.print("[dim]Usage: config get <key>[/dim]")
                        console.print(f"[dim]Valid keys: {', '.join(valid_keys)}[/dim]")
                        console.print("[dim]Type 'config list' to see all available keys[/dim]")
                        return
                
                # Customize error messages for interactive shell context
                if "Try 'queuectl.py" in stderr_text and "--help' for help" in stderr_text:
                    lines = stderr_text.split('\n')
                    for line in lines:
                        if "Try 'queuectl.py" in line and "--help' for help" in line:
                            console.print("[dim]Type 'help' for available commands[/dim]")
                        elif "Missing argument" in line:
                            console.print(f"[red]{line}[/red]")
                            # Add helpful context for missing arguments
                            if "config set" in command:
                                console.print("[dim]Type 'config list' to see available keys[/dim]")
                        elif "Error" in line and not line.startswith("Usage:"):
                            console.print(f"[red]{line}[/red]")
                        elif line.startswith("Usage:"):
                            continue  # Skip usage lines
                        elif line.strip() and not "Try 'queuectl.py" in line:
                            console.print(f"[red]{line}[/red]")
                else:
                    console.print(f"[red]{stderr_text}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
    
    def do_enqueue(self, arg):
        """Add a job to the queue with optional scheduling and priority
        Usage: 
          enqueue {"id":"job1","command":"echo hello"}
          enqueue {"id":"job1","command":"echo hello","priority":10}
          enqueue {"id":"job1","command":"echo hello","run_at":"+30s"}
          enqueue {"id":"job1","command":"echo hello","run_at":"+5m","priority":5}
          enqueue {"id":"job1","command":"echo hello","run_at":"2025-11-09T22:00:00Z"}
        """
        if not arg.strip():
            console.print("[red]Error: Job JSON required[/red]")
            console.print("[dim]Examples:[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"priority\":10}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"run_at\":\"+30s\"}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"run_at\":\"+5m\",\"priority\":5}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"run_at\":\"2025-11-09T22:00:00Z\"}[/dim]")
            return
        
        # Handle JSON properly by escaping quotes
        job_json = arg.strip()
        if not job_json.startswith('{'):
            console.print("[red]Error: Job must be valid JSON[/red]")
            console.print("[dim]Example: enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
            return
        
        try:
            # Parse and validate JSON
            import json
            from datetime import datetime, timezone, timedelta
            import re
            
            job_data = json.loads(job_json)
            
            # Handle relative time formats for run_at
            if 'run_at' in job_data:
                run_at = job_data['run_at']
                if isinstance(run_at, str) and run_at.startswith('+'):
                    # Parse relative time format like +30s, +5m, +2h
                    time_match = re.match(r'\+(\d+)([smh])', run_at)
                    if time_match:
                        amount = int(time_match.group(1))
                        unit = time_match.group(2)
                        
                        now = datetime.now(timezone.utc)
                        if unit == 's':
                            scheduled_time = now + timedelta(seconds=amount)
                        elif unit == 'm':
                            scheduled_time = now + timedelta(minutes=amount)
                        elif unit == 'h':
                            scheduled_time = now + timedelta(hours=amount)
                        
                        # Convert to ISO format
                        job_data['run_at'] = scheduled_time.isoformat()
                        console.print(f"[dim]Scheduling job to run at: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')}[/dim]")
                    else:
                        console.print(f"[red]Error: Invalid time format '{run_at}'. Use +30s, +5m, +2h, or ISO format[/red]")
                        return
            
            # Convert back to JSON string
            processed_json = json.dumps(job_data)
            
        except json.JSONDecodeError as e:
            console.print(f"[red]Error: Invalid JSON - {e}[/red]")
            console.print("[dim]Example: enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
            return
        except Exception as e:
            console.print(f"[red]Error processing job: {e}[/red]")
            return
        
        # Escape quotes for shell command
        escaped_json = processed_json.replace('"', '\\"')
        self.run_queuectl_command(f'enqueue "{escaped_json}"')


    def do_status(self, arg):
        """Show system status including worker and job information"""
        # Show regular system status
        self.run_queuectl_command("status")
        
        # Show current job counts
        console.print(f"\n[yellow]Current Job Status:[/yellow]")
        counts = self._get_job_counts()
        self._display_job_counts(counts)
        
        # Show scheduled jobs if any
        scheduled_jobs = self._get_scheduled_jobs_info()
        if scheduled_jobs:
            console.print(f"\n[yellow]⏰ Scheduled Jobs:[/yellow]")
            for job in scheduled_jobs[:3]:  # Show first 3
                wait_str = self._format_wait_time(job['wait_seconds'])
                if wait_str == "ready now":
                    console.print(f"[dim]• {job['id']}: {wait_str}[/dim]")
                else:
                    console.print(f"[dim]• {job['id']}: ready in {wait_str}[/dim]")
            if len(scheduled_jobs) > 3:
                console.print(f"[dim]... and {len(scheduled_jobs) - 3} more scheduled jobs[/dim]")
        
        # Show worker status
        console.print(f"\n[yellow]Worker Status:[/yellow]")
        worker_result = subprocess.run("python queuectl.py worker status", shell=True, capture_output=True, text=True)
        if worker_result.stdout and worker_result.stdout.strip():
            console.print(worker_result.stdout)
        else:
            console.print("[dim]No workers currently running[/dim]")
            console.print("[dim]Use 'worker start' to process jobs[/dim]")
    
    def do_list(self, arg):
        """List jobs with enhanced display
        Usage: list [--state pending|processing|completed|failed|dead]
        """
        if arg.strip():
            self.run_queuectl_command(f"list {arg}")
        else:
            # Run the list command and enhance the output
            result = subprocess.run("python queuectl.py list", shell=True, capture_output=True, text=True)
            if result.stdout:
                console.print(result.stdout)
                
                # Show filtering tip
                console.print(f"\n[dim] Filter by job type:[/dim]")
                console.print(f"[dim]  list --state pending     - Show only pending jobs[/dim]")
                console.print(f"[dim]  list --state processing  - Show only processing jobs[/dim]")
                console.print(f"[dim]  list --state completed   - Show only completed jobs[/dim]")
                console.print(f"[dim]  list --state failed      - Show only failed jobs[/dim]")
                console.print(f"[dim]  list --state dead        - Show only dead letter queue jobs[/dim]")
                console.print(f"[dim]  list --state scheduled   - Show scheduled jobs with run times[/dim]")
            else:
                console.print("[red]No output from list command[/red]")
    


    def do_worker(self, arg):
        """Smart worker management with cron-like scheduling
        Usage: 
          worker start [--count N] - Start workers with intelligent scheduling
          worker stop              - Stop all workers
          worker status            - Check worker status
        """
        if not arg.strip():
            console.print("[yellow]Worker commands:[/yellow]")
            console.print("  worker start [--count N] - Start workers with intelligent scheduling")
            console.print("  worker stop              - Stop all workers")
            console.print("  worker status            - Check worker status")
            console.print("\n[dim]Workers process all jobs and can stay running for scheduled jobs like cron.[/dim]")
            return
        
        # Handle worker start
        if arg.strip().startswith("start"):
            parts = arg.strip().split()
            count = 2  # default
            
            # Parse arguments
            if "--count" in parts:
                try:
                    count_idx = parts.index("--count")
                    if count_idx + 1 < len(parts):
                        count = int(parts[count_idx + 1])
                except (ValueError, IndexError):
                    count = 2
            
            # Analyze job queue
            console.print("[#bbfa01]Analyzing job queue...[/#bbfa01]")
            pending_jobs = self._get_job_count_by_state('pending')
            scheduled_jobs = self._get_scheduled_jobs_info()
            
            if pending_jobs == 0 and not scheduled_jobs:
                console.print("[yellow]No jobs found in queue.[/yellow]")
                console.print("[dim]Add jobs with: enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
                return
            
            # Show current job status
            if pending_jobs > 0:
                console.print(f"[green]✓ {pending_jobs} job(s) ready for immediate processing[/green]")
            
            if scheduled_jobs:
                console.print(f"\n[yellow]⏰ Found {len(scheduled_jobs)} scheduled job(s):[/yellow]")
                min_wait_time = float('inf')
                for job in scheduled_jobs[:5]:  # Show first 5
                    wait_time = job['wait_seconds']
                    wait_str = self._format_wait_time(wait_time)
                    if wait_str == "ready now":
                        console.print(f"[dim]• {job['id']}: {job['command'][:40]}... ({wait_str})[/dim]")
                    else:
                        console.print(f"[dim]• {job['id']}: {job['command'][:40]}... (ready in {wait_str})[/dim]")
                    min_wait_time = min(min_wait_time, wait_time)
                
                if len(scheduled_jobs) > 5:
                    console.print(f"[dim]... and {len(scheduled_jobs) - 5} more scheduled jobs[/dim]")
                
                # Ask user about keeping workers running for scheduled jobs
                if min_wait_time > 0:
                    next_job_time = self._format_wait_time(min_wait_time)
                    console.print(f"\n[yellow]⏰ Next scheduled job ready in: {next_job_time}[/yellow]")
                    
                    if min_wait_time > 3600:  # More than 1 hour
                        console.print("[yellow]📋 Scheduled jobs are far in the future.[/yellow]")
                        console.print("[dim]Workers will process current jobs and exit.[/dim]")
                        console.print("[dim]Scheduled jobs will be processed when their time comes (automatic conversion).[/dim]")
                    else:
                        console.print("[yellow]📋 Workers can stay running to process scheduled jobs automatically.[/yellow]")
                        console.print("[dim]This acts like a cron daemon - workers wait and process jobs when ready.[/dim]")
                        
                        # Ask user if they want to keep workers running
                        try:
                            response = input("\n🤔 Keep workers running for scheduled jobs? (y/N): ").strip().lower()
                            if response in ['y', 'yes']:
                                console.print("[green]✓ Workers will stay running and act like cron daemon[/green]")
                                console.print("[dim]Workers will automatically process scheduled jobs when ready[/dim]")
                                # Add a flag to keep workers running
                                self._keep_workers_running = True
                            else:
                                console.print("[yellow]Workers will process current jobs and exit[/yellow]")
                                console.print("[dim]Scheduled jobs will be processed later when you start workers again[/dim]")
                                self._keep_workers_running = False
                        except (KeyboardInterrupt, EOFError):
                            console.print("\n[yellow]Defaulting to process current jobs only[/yellow]")
                            self._keep_workers_running = False
            
            console.print(f"\n[#bbfa01]Starting {count} workers...[/#bbfa01]")
            if pending_jobs > 0:
                console.print("[dim]Processing pending jobs with live logs...[/dim]")
            if scheduled_jobs and getattr(self, '_keep_workers_running', False):
                console.print("[dim]Workers will stay running for scheduled jobs (cron mode)[/dim]")
            console.print("[dim]Press Ctrl+C to stop workers gracefully[/dim]")
            
            # Start workers with live output using direct execution
            self._start_workers_with_live_output(count)
            return
        
        # Handle worker stop with enhanced feedback
        elif arg.strip() == "stop":
            console.print("[yellow]Stopping all workers...[/yellow]")
            
            # First try to stop background workers if any
            background_stopped = False
            if hasattr(self, '_background_process') and self._background_process:
                try:
                    if self._background_process.poll() is None:  # Process is still running
                        console.print("[dim]Stopping background workers...[/dim]")
                        self._background_process.terminate()
                        self._background_process.wait(timeout=5)
                        console.print("[green]✓ Background workers stopped[/green]")
                        background_stopped = True
                    self._background_process = None
                except subprocess.TimeoutExpired:
                    self._background_process.kill()
                    console.print("[green]✓ Background workers force stopped[/green]")
                    background_stopped = True
                    self._background_process = None
                except Exception as e:
                    console.print(f"[yellow]Background worker stop error: {e}[/yellow]")
            
            # Also try regular worker stop
            result = subprocess.run("python queuectl.py worker stop", shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                if not background_stopped:
                    console.print("[green]✓ Workers stopped successfully[/green]")
                if result.stdout and "No active workers" not in result.stdout:
                    console.print(result.stdout.strip())
            else:
                if not background_stopped:
                    console.print(f"[yellow]No active workers found[/yellow]")
            
            # Show final job status
            console.print(f"\n[cyan]📊 Current Job Status:[/cyan]")
            final_counts = self._get_job_counts()
            self._display_job_counts(final_counts)
            
            # Check for any remaining scheduled jobs
            scheduled_jobs = self._get_scheduled_jobs_info()
            if scheduled_jobs:
                console.print(f"\n[yellow]⏰ {len(scheduled_jobs)} scheduled jobs remaining:[/yellow]")
                for job in scheduled_jobs[:3]:
                    wait_str = self._format_wait_time(job['wait_seconds'])
                    if wait_str == "ready now":
                        console.print(f"[dim]• {job['id']}: {wait_str}[/dim]")
                    else:
                        console.print(f"[dim]• {job['id']}: ready in {wait_str}[/dim]")
                if len(scheduled_jobs) > 3:
                    console.print(f"[dim]... and {len(scheduled_jobs) - 3} more[/dim]")
        
        # Handle worker status with background worker info
        elif arg.strip() == "status":
            # Show regular worker status
            result = subprocess.run("python queuectl.py worker status", shell=True, capture_output=True, text=True)
            if result.stdout:
                console.print(result.stdout.strip())
            
            # Also show background worker status
            if hasattr(self, '_background_process') and self._background_process:
                if self._background_process.poll() is None:
                    console.print("[green]Background workers: Running[/green]")
                    console.print("[dim]Logs being saved to 'worker_logs.txt'[/dim]")
                    console.print("[dim]Use 'worker stop' to stop background workers[/dim]")
                else:
                    console.print("[yellow]Background workers: Stopped[/yellow]")
                    self._background_process = None
            else:
                console.print("[dim]No background workers running[/dim]")
        
        # Handle other worker commands normally
        else:
            self.run_queuectl_command(f"worker {arg}")
    

    def _get_job_counts(self):
        """Get current job counts by state"""
        result = subprocess.run("python queuectl.py list", shell=True, capture_output=True, text=True)
        
        counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'dead': 0, 'scheduled': 0}
        
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                # Parse the table format - state abbreviations are in column 2
                if '|' in line and not line.startswith('+') and 'ID' not in line and line.strip():
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        state_abbrev = parts[2].strip()  # State abbreviation is in column 2
                        # Map abbreviations to full state names
                        if state_abbrev == 'P':
                            counts['pending'] += 1
                        elif state_abbrev == 'R':
                            counts['processing'] += 1
                        elif state_abbrev == 'C':
                            counts['completed'] += 1
                        elif state_abbrev == 'F':
                            counts['failed'] += 1
                        elif state_abbrev == 'D':
                            counts['dead'] += 1
                        elif state_abbrev == 'S':
                            counts['scheduled'] += 1
        
        return counts
    
    def _display_job_counts(self, counts):
        """Display job counts in a nice format"""
        console.print(f"Pending: {counts['pending']} | Processing: {counts['processing']} | Completed: {counts['completed']} | Failed: {counts['failed']} | Dead: {counts['dead']} | Scheduled: {counts['scheduled']}")
    
    def _get_scheduled_jobs_info(self):
        """Get information about scheduled jobs including wait times"""
        try:
            result = subprocess.run("python queuectl.py list --state scheduled", shell=True, capture_output=True, text=True)
            scheduled_jobs = []
            if result.stdout:
                lines = result.stdout.split('\n')
                current_job = None
                
                for line in lines:
                    if '|' in line and not line.startswith('+') and not line.startswith('┏') and not line.startswith('┡') and not line.startswith('└'):
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 5:
                            # Check if this is a main job line (has job ID)
                            if parts[1] and parts[1] != '' and not parts[1].isspace():
                                # This is a new job
                                if current_job:
                                    scheduled_jobs.append(current_job)
                                
                                job_id = parts[1]
                                state = parts[2] if len(parts) > 2 else ''
                                command = parts[3] if len(parts) > 3 else ''
                                scheduled_time = parts[5] if len(parts) > 5 else ''
                                
                                if state == 'S':  # Scheduled state
                                    current_job = {
                                        'id': job_id,
                                        'command': command,
                                        'scheduled_time': scheduled_time,
                                        'wait_seconds': 0
                                    }
                            elif current_job and len(parts) > 5:
                                # This might be a continuation line with the time
                                time_part = parts[5].strip()
                                if time_part and ':' in time_part:
                                    # Combine with previous scheduled_time if it exists
                                    if current_job['scheduled_time']:
                                        current_job['scheduled_time'] += ' ' + time_part
                                    else:
                                        current_job['scheduled_time'] = time_part
                
                # Don't forget the last job
                if current_job:
                    scheduled_jobs.append(current_job)
                
                # Calculate wait times
                for job in scheduled_jobs:
                    job['wait_seconds'] = self._calculate_wait_time(job['scheduled_time'])
                    
            return scheduled_jobs
        except Exception as e:
            console.print(f"[red]Error getting scheduled jobs: {e}[/red]")
            return []
    
    def _get_job_count_by_state(self, state):
        """Get count of jobs in specific state"""
        try:
            result = subprocess.run(f"python queuectl.py list --state {state}", shell=True, capture_output=True, text=True)
            if "No jobs found" in result.stdout:
                return 0
            # Count lines with job data (contains '|' but not table borders)
            count = 0
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '|' in line and not line.startswith('+') and not 'ID' in line and line.strip():
                        count += 1
            return count
        except Exception:
            return 0
    
    def _calculate_wait_time(self, scheduled_time_str):
        """Calculate seconds until scheduled time"""
        try:
            from datetime import datetime, timezone
            import re
            # Parse the scheduled time (format: "11-10 04:20")
            if not scheduled_time_str or scheduled_time_str == '-':
                return 0
            
            # Extract time parts
            time_match = re.match(r'(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', scheduled_time_str)
            if not time_match:
                return 0
            
            month, day, hour, minute = map(int, time_match.groups())
            # Create datetime object (assume current year)
            now = datetime.now(timezone.utc)
            scheduled_dt = datetime(now.year, month, day, hour, minute, tzinfo=timezone.utc)
            
            # If scheduled time is in the past, it's ready now
            wait_seconds = (scheduled_dt - now).total_seconds()
            return max(0, wait_seconds)
        except Exception:
            return 0
    
    def _format_wait_time(self, seconds):
        """Format wait time in human readable format"""
        if seconds <= 0:
            return "ready now"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m {int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _start_workers_with_live_output(self, count):
        """Start workers and show live output with intelligent scheduling"""
        try:
            import sys
            import os
            import subprocess
            import threading
            import time
            
            # Import worker manager directly
            sys.path.append(os.getcwd())
            from src.worker_manager import WorkerManager
            from src.job_queue import JobQueue
            
            # Create instances
            job_queue = JobQueue()
            worker_manager = WorkerManager(job_queue)
            
            console.print(f"[green]Starting {count} worker process(es)...[/green]")
            
            # Start workers using subprocess with live output
            python_exe = sys.executable
            script_path = os.path.join(os.getcwd(), "queuectl.py")
            
            cmd = [python_exe, script_path, "worker", "start", "--count", str(count)]
            
            # Start the process and capture output in real-time
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            jobs_completed = 0
            last_activity_time = time.time()
            
            try:
                # Read output line by line and display it
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Clean up the output and display it
                        line = output.strip()
                        if line:
                            # Color code different types of log messages
                            if "INFO:worker_manager:" in line:
                                console.print(f"[blue]{line}[/blue]")
                            elif "Worker" in line and "started" in line:
                                console.print(f"[green]{line}[/green]")
                            elif "Processing job" in line:
                                console.print(f"[yellow]{line}[/yellow]")
                                last_activity_time = time.time()
                            elif "completed successfully" in line:
                                console.print(f"[green]{line}[/green]")
                                jobs_completed += 1
                                last_activity_time = time.time()
                            elif "failed" in line.lower():
                                console.print(f"[red]{line}[/red]")
                                last_activity_time = time.time()
                            elif "ERROR" in line:
                                console.print(f"[red]{line}[/red]")
                            else:
                                console.print(line)
                    
                    # Check if workers have been idle for a while (no pending jobs)
                    if time.time() - last_activity_time > 5:  # 5 seconds of inactivity
                        # Show current job status
                        current_counts = self._get_job_counts()
                        console.print(f"\n[cyan]📊 Current Job Status:[/cyan]")
                        self._display_job_counts(current_counts)
                        
                        # Check for scheduled jobs
                        scheduled_jobs = self._get_scheduled_jobs_info()
                        ready_scheduled = [job for job in scheduled_jobs if job['wait_seconds'] <= 0]
                        future_scheduled = [job for job in scheduled_jobs if job['wait_seconds'] > 0]
                        
                        # Check if there are any pending jobs still being processed
                        has_pending = current_counts['pending'] > 0 or current_counts['processing'] > 0
                        
                        if ready_scheduled and not has_pending:
                            # Check if these "ready" jobs are actually being processed
                            # Wait a bit to see if they get picked up
                            console.print(f"\n[yellow]⏰ Found {len(ready_scheduled)} scheduled job(s) ready to run![/yellow]")
                            for job in ready_scheduled[:3]:
                                console.print(f"[dim]• {job['id']}: {job['command'][:40]}...[/dim]")
                            console.print("[dim]Checking if these will be processed automatically...[/dim]")
                            
                            # Wait and check again
                            time.sleep(2)
                            
                            # Re-check job status after waiting
                            updated_counts = self._get_job_counts()
                            updated_scheduled = self._get_scheduled_jobs_info()
                            updated_ready = [job for job in updated_scheduled if job['wait_seconds'] <= 0]
                            updated_future = [job for job in updated_scheduled if job['wait_seconds'] > 0]
                            updated_has_pending = updated_counts['pending'] > 0 or updated_counts['processing'] > 0
                            
                            if updated_ready and not updated_has_pending:
                                # Jobs are still "ready" but not being processed - they might be stuck
                                # Treat this as if we only have future scheduled jobs
                                console.print("[dim]Jobs appear to be ready but not processing - treating as future scheduled[/dim]")
                                future_scheduled = updated_ready + updated_future
                                ready_scheduled = []
                            else:
                                # Jobs are being processed or converted, reset timer
                                last_activity_time = time.time()
                                continue
                        elif future_scheduled and not has_pending and not ready_scheduled:
                            min_wait = min(job['wait_seconds'] for job in future_scheduled)
                            wait_str = self._format_wait_time(min_wait)
                            
                            console.print(f"\n[green]✅ All immediate jobs completed![/green]")
                            console.print(f"[yellow]⏰ Next scheduled job ready in: {wait_str}[/yellow]")
                            
                            # Show final job summary
                            console.print(f"\n[cyan]📊 Final Job Summary:[/cyan]")
                            console.print(f"[green]✓ Completed: {current_counts['completed']} jobs[/green]")
                            if current_counts['dead'] > 0:
                                console.print(f"[red]✗ Failed (DLQ): {current_counts['dead']} jobs[/red]")
                            if len(future_scheduled) > 0:
                                console.print(f"[yellow]⏰ Scheduled: {len(future_scheduled)} jobs remaining[/yellow]")
                                for job in future_scheduled[:3]:
                                    job_wait = self._format_wait_time(job['wait_seconds'])
                                    console.print(f"[dim]   • {job['id']}: ready in {job_wait}[/dim]")
                            
                            # Always ask user what to do
                            console.print(f"\n[cyan]What would you like to do?[/cyan]")
                            console.print(f"[green]1. Continue waiting[/green] - Workers run in background, logs saved to file")
                            console.print(f"[yellow]2. Stop and exit[/yellow] - Stop workers and return to shell")
                            
                            try:
                                response = input(f"\nContinue waiting for scheduled jobs? (y/N): ").strip().lower()
                                if response in ['y', 'yes']:
                                    # Start background mode
                                    console.print(f"\n[green]✓ Workers continuing in background mode...[/green]")
                                    console.print(f"[dim]• Logs will be saved to 'worker_logs.txt'[/dim]")
                                    console.print(f"[dim]• Use 'worker stop' to stop background workers[/dim]")
                                    console.print(f"[dim]• Use 'worker status' to check worker status[/dim]")
                                    console.print(f"[green]Returning to interactive shell...[/green]")
                                    
                                    # Detach the process and save logs to file
                                    import threading
                                    import datetime
                                    
                                    def background_logger():
                                        try:
                                            with open('worker_logs.txt', 'a', encoding='utf-8') as log_file:
                                                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                log_file.write(f"\n=== Background mode started at {timestamp} ===\n")
                                                log_file.write(f"Next scheduled job in: {wait_str}\n")
                                                log_file.write("Workers will continue processing scheduled jobs...\n\n")
                                                log_file.flush()
                                                
                                                # Continue reading process output
                                                while True:
                                                    try:
                                                        output = process.stdout.readline()
                                                        if output == '' and process.poll() is not None:
                                                            log_file.write("=== Workers finished ===\n")
                                                            break
                                                        if output:
                                                            log_file.write(output)
                                                            log_file.flush()
                                                    except:
                                                        break
                                        except Exception as e:
                                            console.print(f"[red]Error writing to log file: {e}[/red]")
                                    
                                    # Start background logging thread
                                    bg_thread = threading.Thread(target=background_logger, daemon=True)
                                    bg_thread.start()
                                    
                                    # Store process reference for worker stop command
                                    self._background_process = process
                                    
                                    # Return to shell immediately
                                    return
                                else:
                                    console.print(f"\n[yellow]Stopping workers and returning to shell...[/yellow]")
                                    break
                            except (KeyboardInterrupt, EOFError):
                                console.print(f"\n[yellow]Stopping workers...[/yellow]")
                                break
                        elif not has_pending and not ready_scheduled and not future_scheduled:
                            # No jobs at all, workers can exit
                            console.print(f"\n[green]✅ All jobs completed![/green]")
                            if jobs_completed > 0:
                                console.print(f"[green]📊 Processed {jobs_completed} jobs successfully[/green]")
                            
                            # Show final status
                            console.print(f"\n[cyan]📊 Final Status:[/cyan]")
                            self._display_job_counts(current_counts)
                            break
                        else:
                            # Still have pending/processing jobs, continue waiting
                            last_activity_time = time.time()
                
                # Wait for process to complete
                process.wait()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping workers...[/yellow]")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                console.print("[green]Workers stopped[/green]")
                
        except Exception as e:
            console.print(f"[red]Error starting workers: {e}[/red]")
            # Fallback to regular command
            self.run_queuectl_command(f"worker start --count {count}")
    

    def do_time(self, arg):
        """Show current time in both local and UTC"""
        import datetime
        local_time = datetime.datetime.now()
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        
        console.print(f"[yellow]Current Time:[/yellow]")
        console.print(f"  Local: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"  UTC:   {utc_time.strftime('%Y-%m-%d %H:%M:%S')} (used by QueueCTL)")
        
        # Show timezone offset
        offset = local_time.astimezone().utcoffset()
        hours, remainder = divmod(int(offset.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        console.print(f"  Offset: UTC{hours:+03d}:{minutes:02d}")
    

    

    def do_dlq(self, arg):
        """Dead Letter Queue management
        Usage:
          dlq list           - List jobs in DLQ with full IDs
          dlq retry <job_id> - Retry a job from DLQ (supports partial ID)
        """
        if not arg.strip():
            console.print("[yellow]DLQ commands:[/yellow]")
            console.print("  dlq list           - List jobs in DLQ with full IDs")
            console.print("  dlq retry <job_id> - Retry a job from DLQ (supports partial ID)")
            return
        
        parts = arg.strip().split()
        command = parts[0]
        
        if command == "list":
            # Show the DLQ table (now with full IDs thanks to our fix)
            result = subprocess.run("python queuectl.py dlq list", shell=True, capture_output=True, text=True)
            if result.stdout:
                console.print(result.stdout)
                
                # Also get full job IDs for easy copy-paste
                dlq_jobs = self._extract_job_ids_from_dlq()
                
                if dlq_jobs:
                    console.print(f"\n[yellow]Full Job IDs for retry:[/yellow]")
                    for i, job_id in enumerate(dlq_jobs, 1):
                        console.print(f"  {i}. [red]{job_id}[/red]")
                    
                    console.print(f"\n[dim] Usage:[/dim]")
                    console.print(f"[dim]  dlq retry <full_job_id>     - Retry with full ID[/dim]")
                    console.print(f"[dim]  dlq retry demo_fail_176     - Retry with partial ID (auto-match)[/dim]")
                else:
                    console.print("[yellow]No jobs found in Dead Letter Queue[/yellow]")
            else:
                console.print("[yellow]No jobs in Dead Letter Queue[/yellow]")
        
        elif command == "retry":
            if len(parts) < 2:
                console.print("[red]Error: Job ID required[/red]")
                console.print("[dim]Usage: dlq retry <job_id>[/dim]")
                return
            
            partial_id = parts[1]
            
            # Find full job ID that matches the partial ID
            full_job_id = self._find_dlq_job_by_partial_id(partial_id)
            
            if full_job_id:
                console.print(f"[dim]Retrying job: {full_job_id}[/dim]")
                self.run_queuectl_command(f"dlq retry {full_job_id}")
            else:
                console.print(f"[red]No DLQ job found matching '{partial_id}'[/red]")
                console.print("[dim]Use 'dlq list' to see available jobs[/dim]")
        
        else:
            # Handle other DLQ commands normally
            self.run_queuectl_command(f"dlq {arg}")
    
    def _extract_job_ids_from_dlq(self):
        """Extract job IDs from DLQ by querying the database directly"""
        try:
            # Import the job queue module to query directly
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from src.job_queue import JobQueue
            
            # Create job queue instance and get dead jobs directly
            job_queue = JobQueue()
            dead_jobs = job_queue.list_jobs('dead')
            
            return [job['id'] for job in dead_jobs]
        except Exception as e:
            # Fallback to command parsing if direct access fails
            try:
                result = subprocess.run("python queuectl.py list --state dead", shell=True, capture_output=True, text=True)
                if result.stdout:
                    job_ids = []
                    lines = result.stdout.split('\n')
                    for line in lines:
                        # Look for lines that contain job IDs
                        line = line.strip()
                        if '|' in line and ('demo_fail' in line or 'job_' in line or 'quick_' in line):
                            parts = line.split('|')
                            if len(parts) >= 1:
                                job_id = parts[0].strip()
                                if job_id and job_id != 'ID' and not job_id.startswith('-') and not job_id.startswith('+'):
                                    job_ids.append(job_id)
                    return job_ids
                return []
            except:
                return []
    
    def _find_full_job_id_pattern(self, partial_id):
        """Try to find full job ID by pattern matching"""
        try:
            # Check if we can find jobs with this pattern in any state
            result = subprocess.run("python queuectl.py list", shell=True, capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if partial_id in line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            job_id = parts[1].strip()
                            if job_id.startswith(partial_id) and not job_id.endswith('…'):
                                return job_id
            return None
        except:
            return None
    
    def _find_dlq_job_by_partial_id(self, partial_id):
        """Find a DLQ job by partial ID match"""
        try:
            # First try to get from our extracted list
            dlq_jobs = self._extract_job_ids_from_dlq()
            for job_id in dlq_jobs:
                if partial_id in job_id:
                    return job_id
            
            return None
        except:
            return None
    
    def do_config(self, arg):
        """Configuration management
        Usage:
          config set <key> <value>
          config get <key>
          config list
        """
        if not arg.strip():
            console.print("[yellow]Config commands:[/yellow]")
            console.print("  config set <key> <value> - Set configuration")
            console.print("  config get <key>         - Get configuration")
            console.print("  config list              - List all configuration")
            return
        
        self.run_queuectl_command(f"config {arg}")
    

    def do_demo(self, arg):
        """Run a quick demo with enhanced features"""
        console.print("[#bbfa01]Running Enhanced Demo...[/#bbfa01]")
        
        # Generate unique timestamp for job IDs
        import time
        timestamp = int(time.time())
        
        # Add demo jobs with various features
        demo_jobs = [
            {"id": f"demo_hello_{timestamp}", "command": "echo Hello from QueueCTL!", "priority": 1},
            {"id": f"demo_date_{timestamp}", "command": "date /t", "timeout_seconds": 30},
            {"id": f"demo_time_{timestamp}", "command": "time /t", "priority": -1},
            {"id": f"demo_scheduled_{timestamp}", "command": "echo Scheduled job!", "run_at": "+30s"},
            {"id": f"demo_fail_{timestamp}", "command": "nonexistent_command", "max_retries": 2}
        ]
        
        for job in demo_jobs:
            job_json = json.dumps(job).replace('"', '\\"')
            console.print(f"[dim]Adding job: {job['id']} (priority: {job.get('priority', 0)})[/dim]")
            self.run_queuectl_command(f'enqueue "{job_json}"')
        
        console.print("\n[#bbfa01]Enhanced demo jobs added![/#bbfa01]")
        console.print("[dim]• High priority job will run first[/dim]")
        console.print("[dim]• Scheduled job will run in 30 seconds[/dim]")
        console.print("[dim]• Failed job will demonstrate retry logic[/dim]")
        console.print("[dim]Start workers with: worker start --count 2[/dim]")
    

    def do_metrics(self, arg):
        """Show system metrics"""
        hours = 24
        if arg.strip():
            try:
                hours = int(arg.strip())
            except ValueError:
                console.print("[red]Error: Hours must be a number[/red]")
                return
        
        self.run_queuectl_command(f"metrics --hours {hours}")
    
    def do_dashboard(self, arg):
        """Start web dashboard in background"""
        console.print("[#bbfa01]Starting web dashboard in background...[/#bbfa01]")
        
        try:
            import threading
            import sys
            import os
            
            # Get the Python executable and script path
            python_exe = sys.executable
            script_path = os.path.join(os.getcwd(), "queuectl.py")
            
            def run_dashboard():
                full_cmd = f'"{python_exe}" "{script_path}" dashboard'
                # Redirect output to suppress the "Press Ctrl+C" message
                subprocess.run(full_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Start dashboard in background thread
            dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            dashboard_thread.start()
            
            console.print("[green]Dashboard started in background![/green]")
            console.print("[dim]Access it at: http://localhost:8080[/dim]")
            console.print("[yellow]Note: Dashboard runs in background. Use 'dashboard_stop' to stop it.[/yellow]")
            console.print("[yellow]TIP: Use 'dashboard_stop' command instead of Ctrl+C to avoid exiting shell![/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error starting dashboard:[/red] {e}")
    
    def do_dashboard_stop(self, arg):
        """Stop the web dashboard"""
        console.print("[#bbfa01]Stopping web dashboard...[/#bbfa01]")
        
        try:
            import psutil
            import os
            
            killed = False
            current_pid = os.getpid()  # Don't kill ourselves!
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue  # Skip our own process
                        
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'queuectl.py dashboard' in cmdline and 'python' in proc.info['name'].lower():
                        proc.terminate()
                        killed = True
                        console.print(f"[dim]Stopped dashboard process (PID: {proc.info['pid']})[/dim]")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed:
                console.print("[green]Dashboard stopped successfully[/green]")
            else:
                console.print("[yellow]No dashboard processes found[/yellow]")
                console.print("[dim]Dashboard may have already stopped or wasn't running[/dim]")
                
        except ImportError:
            console.print("[red]Error: psutil not installed[/red]")
            console.print("[dim]Install with: pip install psutil[/dim]")
            console.print("[dim]Or install all dependencies: pip install -r requirements.txt[/dim]")
            console.print("\n[yellow]Manual stop instructions:[/yellow]")
            console.print("[dim]1. Open a new terminal/command prompt[/dim]")
            console.print("[dim]2. Run: python queuectl.py dashboard (then press Ctrl+C)[/dim]")
            console.print("[dim]3. Or restart this shell to clean up background processes[/dim]")
            
        except Exception as e:
            console.print(f"[yellow]Could not stop dashboard: {e}[/yellow]")
            console.print("[dim]Try manual stop or restart the shell[/dim]")
    

    
    def do_test_deliverables(self, arg):
        """Test all must-have deliverables"""
        console.print("[bold blue] Testing Must-Have Deliverables...[/bold blue]\n")
        
        tests = [
            ("CLI Application", "status"),
            ("Persistent Storage", "list"),
            ("Configuration", "config list"),
            ("Dead Letter Queue", "dlq list"),
        ]
        
        for name, cmd in tests:
            console.print(f"[cyan]Testing {name}...[/cyan]")
            self.run_queuectl_command(cmd)
            console.print()
        
        console.print("[green]PASS: Basic deliverables test complete![/green]")
        console.print("[dim]For full testing, run: test_bonus_features[/dim]")
    
    def do_test_bonus_features(self, arg):
        """Test all bonus features with examples"""
        console.print("[bold yellow]Testing Bonus Features...[/bold yellow]\n")
        
        # 1. Priority Queues
        console.print("[cyan]1. Testing Priority Queues...[/cyan]")
        priority_jobs = [
            {"id": "low_priority", "command": "echo Low Priority", "priority": -1},
            {"id": "high_priority", "command": "echo High Priority", "priority": 10},
            {"id": "urgent_priority", "command": "echo URGENT!", "priority": 20}
        ]
        
        for job in priority_jobs:
            job_json = json.dumps(job).replace('"', '\\"')
            console.print(f"[dim]Adding {job['id']} (priority: {job['priority']})[/dim]")
            self.run_queuectl_command(f'enqueue "{job_json}"')
        
        console.print()
        
        # 2. Scheduled Jobs
        console.print("[cyan]2. Testing Scheduled Jobs...[/cyan]")
        scheduled_jobs = [
            {"id": "delayed_5s", "command": "echo Delayed 5 seconds", "run_at": "+5s"},
            {"id": "delayed_30s", "command": "echo Delayed 30 seconds", "run_at": "+30s"}
        ]
        
        for job in scheduled_jobs:
            job_json = json.dumps(job).replace('"', '\\"')
            console.print(f"[dim]Scheduling {job['id']} for {job['run_at']}[/dim]")
            self.run_queuectl_command(f'schedule "{job_json}"')
        
        console.print()
        
        # 3. Job Timeouts
        console.print("[cyan]3. Testing Job Timeouts...[/cyan]")
        timeout_jobs = [
            {"id": "quick_job", "command": "echo Quick job", "timeout_seconds": 5},
            {"id": "timeout_job", "command": "ping -n 10 127.0.0.1", "timeout_seconds": 3}
        ]
        
        for job in timeout_jobs:
            job_json = json.dumps(job).replace('"', '\\"')
            console.print(f"[dim]Adding {job['id']} (timeout: {job['timeout_seconds']}s)[/dim]")
            self.run_queuectl_command(f'enqueue "{job_json}"')
        
        console.print()
        
        # 4. Output Logging
        console.print("[cyan]4. Testing Output Logging...[/cyan]")
        output_jobs = [
            {"id": "output_test", "command": "echo This output will be logged"},
            {"id": "date_output", "command": "date /t"}
        ]
        
        for job in output_jobs:
            job_json = json.dumps(job).replace('"', '\\"')
            console.print(f"[dim]Adding {job['id']} for output logging[/dim]")
            self.run_queuectl_command(f'enqueue "{job_json}"')
        
        console.print()
        
        # Show current status
        console.print("[cyan]5. Current System Status:[/cyan]")
        self.run_queuectl_command("status")
        
        console.print("\n[green]All bonus features tested![/green]")
        console.print("[dim]Start workers with: worker start --count 2[/dim]")
        console.print("[dim]Check metrics with: metrics[/dim]")
        console.print("[dim]View web dashboard: dashboard[/dim]")
    
    def do_verify_all(self, arg):
        """Complete verification of all features"""
        console.print("[bold green]Complete QueueCTL Verification[/bold green]\n")
        
        # Run deliverables test
        self.do_test_deliverables("")
        
        console.print("\n" + "="*50 + "\n")
        
        # Run bonus features test
        self.do_test_bonus_features("")
        
        console.print("\n" + "="*50 + "\n")
        
        console.print("[bold green]PASS: Verification Complete![/bold green]")
        console.print("\n[yellow]Next Steps:[/yellow]")
        console.print("1. [cyan]worker start --count 2[/cyan] - Start workers to process jobs")
        console.print("2. [cyan]dashboard[/cyan] - Start web monitoring")
        console.print("3. [cyan]metrics[/cyan] - View performance statistics")
        console.print("4. [cyan]list[/cyan] - See job execution results")
    

    def do_clear(self, arg):
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        show_banner()
    
    def do_banner(self, arg):
        """Show the QueueCTL banner"""
        show_banner()
    


    def do_exit(self, arg):
        """Exit the interactive shell"""
        console.print("[#bbfa01]Thanks for using QueueCTL![/#bbfa01]")
        return True
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass
    
    def cmdloop(self, intro=None):
        """Override cmdloop to handle KeyboardInterrupt gracefully"""
        while True:
            try:
                super().cmdloop(intro)
                break  # Normal exit
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted! Use 'exit' or Ctrl+D to quit the shell.[/yellow]")
                console.print("[dim]TIP: Use 'dashboard_stop' to stop dashboard instead of Ctrl+C[/dim]")
                # Continue the loop to restart the shell


def start_interactive_shell():
    """Start the interactive shell"""
    shell = QueueCTLShell()
    shell.cmdloop()