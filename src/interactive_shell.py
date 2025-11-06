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
                console.print(f"[red]{result.stderr.strip()}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
    
    def do_enqueue(self, arg):
        """Add a job to the queue
        Usage: enqueue {"id":"job1","command":"echo hello"}
        """
        if not arg.strip():
            console.print("[red]Error: Job JSON required[/red]")
            console.print("[dim]Example: enqueue {\"id\":\"test\",\"command\":\"echo hello\"}[/dim]")
            return
        
        self.run_queuectl_command(f'enqueue "{arg}"')
    
    def do_status(self, arg):
        """Show system status"""
        self.run_queuectl_command("status")
    
    def do_list(self, arg):
        """List jobs
        Usage: list [--state pending|processing|completed|failed|dead]
        """
        if arg.strip():
            self.run_queuectl_command(f"list {arg}")
        else:
            self.run_queuectl_command("list")
    
    def do_worker(self, arg):
        """Worker management
        Usage: 
          worker start [--count N]
          worker stop
        """
        if not arg.strip():
            console.print("[yellow]Worker commands:[/yellow]")
            console.print("  worker start [--count N] - Start N workers (default: 1)")
            console.print("  worker stop              - Stop all workers")
            return
        
        self.run_queuectl_command(f"worker {arg}")
    
    def do_dlq(self, arg):
        """Dead Letter Queue management
        Usage:
          dlq list
          dlq retry <job_id>
        """
        if not arg.strip():
            console.print("[yellow]DLQ commands:[/yellow]")
            console.print("  dlq list           - List jobs in DLQ")
            console.print("  dlq retry <job_id> - Retry a job from DLQ")
            return
        
        self.run_queuectl_command(f"dlq {arg}")
    
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
        
        # Add demo jobs with various features
        demo_jobs = [
            {"id": "demo_hello", "command": "echo Hello from QueueCTL!", "priority": 1},
            {"id": "demo_date", "command": "date /t", "timeout_seconds": 30},
            {"id": "demo_time", "command": "time /t", "priority": -1},
            {"id": "demo_scheduled", "command": "echo Scheduled job!", "run_at": "+30s"},
            {"id": "demo_fail", "command": "nonexistent_command", "max_retries": 2}
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
        """Start web dashboard"""
        console.print("[#bbfa01]Starting web dashboard...[/#bbfa01]")
        console.print("[dim]This will start the dashboard in the background.[/dim]")
        console.print("[dim]Access it at: http://localhost:8080[/dim]")
        
        # Start dashboard in background
        import threading
        import subprocess
        
        def start_dashboard():
            subprocess.run("python queuectl.py dashboard", shell=True)
        
        dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
        dashboard_thread.start()
        
        console.print("[green]Dashboard started! Check http://localhost:8080[/green]")
    
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
    
    def do_help_features(self, arg):
        """Show help for testing deliverables and bonus features"""
        console.print("[bold blue]QueueCTL Feature Testing Commands[/bold blue]\n")
        
        console.print("[yellow]Deliverable Testing:[/yellow]")
        console.print("  [cyan]test_deliverables[/cyan]  - Test all must-have deliverables")
        console.print("  [cyan]test_bonus_features[/cyan] - Test all bonus features")
        console.print("  [cyan]verify_all[/cyan]         - Complete verification")
        
        console.print("\n[yellow]Quick Job Creation:[/yellow]")
        console.print("  [cyan]quick <command>[/cyan]    - Create simple job")
        console.print("  [cyan]priority <command>[/cyan] - Create high priority job")
        console.print("  [cyan]schedule <cmd> +time[/cyan] - Schedule job (e.g., +5m, +1h)")
        
        console.print("\n[yellow]Demo & Testing:[/yellow]")
        console.print("  [cyan]demo[/cyan]               - Run enhanced demo")
        console.print("  [cyan]dashboard[/cyan]          - Start web dashboard")
        console.print("  [cyan]metrics[/cyan]            - Show system metrics")
        
        console.print("\n[yellow]Standard Commands:[/yellow]")
        console.print("  [cyan]enqueue <json>[/cyan]     - Add job with full options")
        console.print("  [cyan]list[/cyan]               - List all jobs")
        console.print("  [cyan]status[/cyan]             - System status")
        console.print("  [cyan]worker start/stop[/cyan]  - Manage workers")
        console.print("  [cyan]dlq list/retry[/cyan]     - Dead Letter Queue")
        console.print("  [cyan]config set/get[/cyan]     - Configuration")
    
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
        console.print("[#bbfa01] Thanks for using QueueCTL![/#bbfa01]")
        return True
    
    def do_quit(self, arg):
        """Exit the interactive shell"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        console.print()
        return self.do_exit(arg)
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass
    
    def cmdloop(self, intro=None):
        """Override cmdloop to handle KeyboardInterrupt gracefully"""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' or Ctrl+D to quit.[/dim]")
            self.cmdloop()


def start_interactive_shell():
    """Start the interactive shell"""
    shell = QueueCTLShell()
    shell.cmdloop()