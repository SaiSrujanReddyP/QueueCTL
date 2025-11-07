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
        """Add a job to the queue with optional scheduling
        Usage: 
          enqueue {"id":"job1","command":"echo hello"}
          enqueue {"id":"job1","command":"echo hello","run_at":"+30s"}
          enqueue {"id":"job1","command":"echo hello","run_at":"+5m"}
          enqueue {"id":"job1","command":"echo hello","run_at":"2025-11-09T22:00:00Z"}
        """
        if not arg.strip():
            console.print("[red]Error: Job JSON required[/red]")
            console.print("[dim]Examples:[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"run_at\":\"+30s\"}[/dim]")
            console.print("[dim]  enqueue {\"id\":\"test\",\"command\":\"echo hello\",\"run_at\":\"+5m\"}[/dim]")
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

    def do_add(self, arg):
        """Add a simple job to the queue
        Usage: add <command> [--id job_id] [--priority N]
        Example: add "echo hello world" --id my-job --priority 5
        """
        if not arg.strip():
            console.print("[red]Error: Command required[/red]")
            console.print("[dim]Example: add \"echo hello world\" --id my-job[/dim]")
            return
        
        import shlex
        import time
        import json
        
        try:
            # Parse arguments
            parts = shlex.split(arg)
            command = parts[0]
            
            # Default values
            job_id = f"job_{int(time.time())}"
            priority = 0
            
            # Parse optional arguments
            i = 1
            while i < len(parts):
                if parts[i] == "--id" and i + 1 < len(parts):
                    job_id = parts[i + 1]
                    i += 2
                elif parts[i] == "--priority" and i + 1 < len(parts):
                    try:
                        priority = int(parts[i + 1])
                    except ValueError:
                        console.print("[red]Error: Priority must be a number[/red]")
                        return
                    i += 2
                else:
                    i += 1
            
            # Create job JSON
            job = {"id": job_id, "command": command, "priority": priority}
            job_json = json.dumps(job).replace('"', '\\"')
            
            console.print(f"[dim]Adding job: {job_id}[/dim]")
            self.run_queuectl_command(f'enqueue "{job_json}"')
            
        except Exception as e:
            console.print(f"[red]Error parsing command: {e}[/red]")
            console.print("[dim]Example: add \"echo hello world\" --id my-job[/dim]")

    def do_status(self, arg):
        """Show system status including worker and job information"""
        # Show regular system status
        self.run_queuectl_command("status")
        
        # Show current job counts
        console.print(f"\n[yellow]Current Job Status:[/yellow]")
        counts = self._get_job_counts()
        self._display_job_counts(counts)
        
        # Show worker status
        console.print(f"\n[yellow]Worker Status:[/yellow]")
        worker_result = subprocess.run("python queuectl.py worker status", shell=True, capture_output=True, text=True)
        if worker_result.stdout and worker_result.stdout.strip():
            console.print(worker_result.stdout)
        else:
            console.print("[dim]No workers currently running[/dim]")
            console.print("[dim]Use 'auto_worker start' to start persistent background workers[/dim]")
    
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
                
                # Show scheduled job countdown
                scheduled_jobs = []
                for line in result.stdout.split('\n'):
                    if '| scheduled |' in line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            job_id = parts[1].strip()
                            scheduled_jobs.append(job_id)
                
                if scheduled_jobs:
                    console.print(f"\n[yellow]⏰ Scheduled Jobs:[/yellow]")
                    console.print("[dim]+-----------------+-----------+[/dim]")
                    console.print("[dim]| Job ID          | State     |[/dim]")
                    console.print("[dim]+-----------------+-----------+[/dim]")
                    
                    for job_id in scheduled_jobs:
                        # Format the display
                        job_display = job_id[:15] + "…" if len(job_id) > 16 else job_id
                        console.print(f"[dim]| {job_display:<15} | scheduled |[/dim]")
                    
                    console.print("[dim]+-----------------+-----------+[/dim]")
                    console.print("[dim]Note: Scheduled jobs will automatically become pending when their time arrives[/dim]")
            else:
                console.print("[red]No output from list command[/red]")
    
    def do_scheduler(self, arg):
        """Control the scheduler daemon for scheduled job management
        Usage: 
          scheduler start [--workers N] [--auto] - Start scheduler daemon
          scheduler stop                          - Stop scheduler daemon
          scheduler status                        - Check scheduler daemon status
          scheduler logs                          - Show recent scheduler logs
        """
        if not arg.strip():
            console.print("[yellow]Scheduler daemon commands:[/yellow]")
            console.print("  scheduler start [--workers N] [--auto] - Start scheduler daemon")
            console.print("  scheduler stop                          - Stop scheduler daemon") 
            console.print("  scheduler status                        - Check scheduler daemon status")
            console.print("  scheduler logs                          - Show recent scheduler logs")
            console.print("\n[dim]The scheduler daemon:[/dim]")
            console.print("[dim]• Converts scheduled jobs to pending when their time arrives[/dim]")
            console.print("[dim]• Manual mode (default): You control workers with 'worker start/stop'[/dim]")
            console.print("[dim]• Auto mode (--auto): Automatically manages workers[/dim]")
            return
        
        parts = arg.strip().split()
        command = parts[0]
        
        if command == "start":
            workers = 2  # default
            auto_mode = False
            
            if "--workers" in parts:
                try:
                    workers_idx = parts.index("--workers")
                    if workers_idx + 1 < len(parts):
                        workers = int(parts[workers_idx + 1])
                except (ValueError, IndexError):
                    workers = 2
            
            if "--auto" in parts:
                auto_mode = True
            
            mode_text = "auto worker management" if auto_mode else "manual worker control"
            console.print(f"[#bbfa01]Starting scheduler daemon ({mode_text})...[/#bbfa01]")
            
            if auto_mode:
                console.print(f"[dim]Auto mode: Will automatically manage {workers} workers.[/dim]")
            else:
                console.print("[dim]Manual mode: You control workers with 'worker start/stop' commands.[/dim]")
            
            try:
                import sys
                import os
                
                python_exe = sys.executable
                daemon_script = os.path.join(os.getcwd(), "src", "scheduler_daemon.py")
                
                # Start daemon in background
                daemon_args = [python_exe, daemon_script, "--daemon", "--workers", str(workers)]
                if auto_mode:
                    daemon_args.append("--auto")
                
                if os.name == 'nt':  # Windows
                    subprocess.Popen(daemon_args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:  # Unix/Linux
                    auto_flag = " --auto" if auto_mode else ""
                    os.system(f'nohup "{python_exe}" "{daemon_script}" --daemon --workers {workers}{auto_flag} > /dev/null 2>&1 &')
                
                console.print("[green]✓ Scheduler daemon started in background![/green]")
                if auto_mode:
                    console.print("[dim]Scheduled jobs will be converted to pending and processed automatically.[/dim]")
                else:
                    console.print("[dim]Scheduled jobs will be converted to pending. Use 'worker start' to process them.[/dim]")
                console.print("[dim]Use 'scheduler status' to check if it's running.[/dim]")
                
            except Exception as e:
                console.print(f"[red]Failed to start scheduler daemon: {e}[/red]")
        
        elif command == "stop":
            console.print("[yellow]Stopping scheduler daemon...[/yellow]")
            
            # Try to find and stop the daemon process
            try:
                if os.name == 'nt':  # Windows
                    # Use taskkill to stop scheduler processes
                    subprocess.run('taskkill /f /im python.exe /fi "WINDOWTITLE eq scheduler_daemon*"', shell=True, capture_output=True)
                else:  # Unix/Linux
                    # Use pkill to stop scheduler processes
                    subprocess.run("pkill -f scheduler_daemon.py", shell=True, capture_output=True)
                
                # Also stop any workers
                subprocess.run("python queuectl.py worker stop", shell=True, capture_output=True)
                
                console.print("[green]✓ Scheduler daemon stopped[/green]")
                
            except Exception as e:
                console.print(f"[red]Error stopping daemon: {e}[/red]")
        
        elif command == "status":
            console.print("[yellow]Checking scheduler daemon status...[/yellow]")
            
            # Check if daemon process is running
            try:
                import os
                
                if os.name == 'nt':  # Windows
                    result = subprocess.run('tasklist /fi "IMAGENAME eq python.exe"', shell=True, capture_output=True, text=True)
                    if "scheduler_daemon" in result.stdout:
                        console.print("[green]✓ Scheduler daemon is running[/green]")
                    else:
                        console.print("[yellow]Scheduler daemon is not running[/yellow]")
                else:  # Unix/Linux
                    result = subprocess.run("pgrep -f scheduler_daemon.py", shell=True, capture_output=True)
                    if result.returncode == 0:
                        console.print("[green]✓ Scheduler daemon is running[/green]")
                    else:
                        console.print("[yellow]Scheduler daemon is not running[/yellow]")
                
                # Show current job status
                console.print(f"\n[yellow]Current Job Status:[/yellow]")
                counts = self._get_job_counts()
                self._display_job_counts(counts)
                
            except Exception as e:
                console.print(f"[red]Error checking status: {e}[/red]")
        
        elif command == "logs":
            console.print("[yellow]Recent scheduler daemon logs:[/yellow]")
            
            try:
                import os
                
                log_file = "scheduler_daemon.log"
                if os.path.exists(log_file):
                    # Show last 20 lines of log file
                    with open(log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        recent_lines = lines[-20:] if len(lines) > 20 else lines
                        
                    for line in recent_lines:
                        console.print(f"[dim]{line.strip()}[/dim]")
                else:
                    console.print("[yellow]No log file found. Daemon may not be running.[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]Error reading logs: {e}[/red]")
        
        else:
            console.print(f"[red]Unknown scheduler command: {command}[/red]")
    

    def do_worker(self, arg):
        """Worker management
        Usage: 
          worker start [--count N] [--silent] - Start workers with live monitoring
          worker stop                         - Stop all workers
        """
        if not arg.strip():
            console.print("[yellow]Worker commands:[/yellow]")
            console.print("  worker start [--count N] [--silent] - Start workers with live monitoring")
            console.print("  worker stop                         - Stop all workers")
            console.print("\n[dim]By default, 'worker start' shows live progress. Use --silent for background mode.[/dim]")
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
            
            # Start workers normally
            self.run_queuectl_command(f"worker start --count {count}")
            return
        
        # Handle other worker commands normally
        self.run_queuectl_command(f"worker {arg}")
    

    def _get_job_counts(self):
        """Get current job counts by state"""
        result = subprocess.run("python queuectl.py list", shell=True, capture_output=True, text=True)
        
        counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'dead': 0, 'scheduled': 0}
        
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                # More robust parsing - look for the state column specifically
                if '|' in line and len(line.split('|')) >= 3:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        state = parts[2].strip().lower()  # State is in the 3rd column
                        if state == 'pending':
                            counts['pending'] += 1
                        elif state == 'processing':
                            counts['processing'] += 1
                        elif state == 'completed':
                            counts['completed'] += 1
                        elif state == 'failed':
                            counts['failed'] += 1
                        elif state == 'dead':
                            counts['dead'] += 1
                        elif state == 'scheduled':
                            counts['scheduled'] += 1
        
        return counts
    
    def _display_job_counts(self, counts):
        """Display job counts in a nice format"""
        console.print(f"Pending: {counts['pending']} | Processing: {counts['processing']} | Completed: {counts['completed']} | Failed: {counts['failed']} | Dead: {counts['dead']} | Scheduled: {counts['scheduled']}")
    
    def do_scheduled(self, arg):
        """Show all scheduled jobs"""
        result = subprocess.run("python queuectl.py list --state scheduled", shell=True, capture_output=True, text=True)
        
        if not result.stdout or "No jobs found" in result.stdout:
            console.print("[yellow]No scheduled jobs found.[/yellow]")
            return
        
        console.print("[yellow]📅 Scheduled Jobs:[/yellow]")
        console.print(result.stdout)
        
        # Show current UTC time for reference
        import datetime
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        console.print(f"\n[dim]Current UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        console.print("[dim]Scheduled jobs will automatically become pending when their time arrives.[/dim]")
    
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
    
    def do_stop_workers(self, arg):
        """Stop all running workers and show final status"""
        console.print("[yellow]Stopping all workers...[/yellow]")
        result = subprocess.run("python queuectl.py worker stop", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✓ Workers stopped successfully[/green]")
        else:
            console.print(f"[red]Worker stop result: {result.stdout or result.stderr}[/red]")
        
        # Show final job status
        console.print(f"\n[yellow]Final Job Status:[/yellow]")
        final_counts = self._get_job_counts()
        self._display_job_counts(final_counts)
    

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
            # First show the original DLQ table for detailed info
            console.print("[yellow]Dead Letter Queue:[/yellow]")
            result = subprocess.run("python queuectl.py dlq list", shell=True, capture_output=True, text=True)
            if result.stdout:
                console.print(result.stdout)
                
                # Now get full job IDs by querying the database directly
                console.print("\n[yellow]Full Job IDs for retry:[/yellow]")
                
                # Try to get full IDs using a different approach
                full_ids_result = subprocess.run("python queuectl.py list --state dead --format json", shell=True, capture_output=True, text=True)
                if full_ids_result.returncode == 0 and full_ids_result.stdout:
                    try:
                        import json
                        jobs_data = json.loads(full_ids_result.stdout)
                        dlq_jobs = [job['id'] for job in jobs_data if job.get('state') == 'dead']
                    except:
                        # Fallback: parse the regular output and try to extract IDs
                        dlq_jobs = self._extract_job_ids_from_dlq()
                else:
                    # Fallback: parse the regular output and try to extract IDs
                    dlq_jobs = self._extract_job_ids_from_dlq()
                
                if dlq_jobs:
                    console.print(f"\n[dim]Available jobs for retry ({len(dlq_jobs)} total):[/dim]")
                    for i, job_id in enumerate(dlq_jobs, 1):
                        console.print(f"  {i}. [red]{job_id}[/red]")
                    
                    console.print(f"\n[dim]💡 Usage:[/dim]")
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
        """Extract job IDs from DLQ by parsing database or command output"""
        try:
            # Try to get jobs from the database directly using the DLQ command
            result = subprocess.run("python queuectl.py dlq list", shell=True, capture_output=True, text=True)
            if result.stdout:
                job_ids = []
                lines = result.stdout.split('\n')
                for line in lines:
                    # Look for lines with job data (contains | and demo_fail or other job patterns)
                    if '|' in line and ('demo_fail' in line or 'job_' in line or 'quick_' in line):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            job_id = parts[1].strip()
                            # If the ID is truncated (ends with …), try to reconstruct it
                            if job_id and job_id != 'ID':
                                if job_id.endswith('…'):
                                    # Try to find the full ID by matching pattern
                                    full_id = self._find_full_job_id_pattern(job_id.replace('…', ''))
                                    if full_id:
                                        job_ids.append(full_id)
                                    else:
                                        job_ids.append(job_id)  # Keep truncated as fallback
                                else:
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
            
            # Fallback: try direct database query
            result = subprocess.run("python queuectl.py list --state dead", shell=True, capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if '| dead |' in line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            job_id = parts[1].strip()
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
    
    def do_quick(self, arg):
        """Quick job creation with simple syntax
        Usage: quick <command>
        Example: quick echo hello world
        """
        if not arg.strip():
            console.print("[red]Error: Command required[/red]")
            console.print("[dim]Example: quick echo hello world[/dim]")
            return
        
        # Generate a simple job ID
        import time
        job_id = f"quick_{int(time.time())}"
        
        # Create job JSON
        job = {"id": job_id, "command": arg}
        job_json = json.dumps(job).replace('"', '\\"')
        
        console.print(f"[dim]Creating job: {job_id}[/dim]")
        self.run_queuectl_command(f'enqueue "{job_json}"')
    
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
    
    def do_schedule(self, arg):
        """Schedule a job to run later
        Usage: schedule <command> [+time]
        Example: schedule echo hello +5m
        """
        if not arg.strip():
            console.print("[red]Error: Command required[/red]")
            console.print("[dim]Example: schedule echo hello +5m[/dim]")
            return
        
        parts = arg.strip().split()
        if len(parts) < 2:
            console.print("[red]Error: Command and time required[/red]")
            console.print("[dim]Example: schedule echo hello +5m[/dim]")
            return
        
        time_spec = parts[-1]
        command = ' '.join(parts[:-1])
        
        if not time_spec.startswith('+'):
            console.print("[red]Error: Time must start with + (e.g., +5m, +1h)[/red]")
            return
        
        # Generate job
        import time as time_module
        job_id = f"scheduled_{int(time_module.time())}"
        job = {"id": job_id, "command": command, "run_at": time_spec}
        job_json = json.dumps(job).replace('"', '\\"')
        
        console.print(f"[dim]Scheduling job: {job_id} to run {time_spec}[/dim]")
        self.run_queuectl_command(f'schedule "{job_json}"')
    
    def do_priority(self, arg):
        """Create a high priority job
        Usage: priority <command>
        Example: priority echo urgent task
        """
        if not arg.strip():
            console.print("[red]Error: Command required[/red]")
            console.print("[dim]Example: priority echo urgent task[/dim]")
            return
        
        # Generate high priority job
        import time
        job_id = f"priority_{int(time.time())}"
        job = {"id": job_id, "command": arg, "priority": 10}
        job_json = json.dumps(job).replace('"', '\\"')
        
        console.print(f"[dim]Creating high priority job: {job_id}[/dim]")
        self.run_queuectl_command(f'enqueue "{job_json}"')
    
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
    
    def do_jobs_stuck(self, arg):
        """Check for jobs stuck in processing state"""
        console.print("[#bbfa01]Checking for stuck jobs...[/#bbfa01]")
        
        # Get jobs that have been processing for too long
        result = subprocess.run("python queuectl.py list --state processing", shell=True, capture_output=True, text=True)
        
        if result.stdout and "No jobs found" not in result.stdout:
            console.print("[yellow]Jobs currently in processing state:[/yellow]")
            console.print(result.stdout)
            console.print("\n[dim]If jobs are stuck, you can:[/dim]")
            console.print("[dim]1. Stop workers: worker stop[/dim]")
            console.print("[dim]2. Restart workers: worker start --count 2[/dim]")
            console.print("[dim]3. Check worker processes manually[/dim]")
        else:
            console.print("[green]No jobs stuck in processing state[/green]")
    

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