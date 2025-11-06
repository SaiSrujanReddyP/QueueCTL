"""
ASCII Banner and startup display for QueueCTL
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table

console = Console()

# QueueCTL ASCII Art Banner
QUEUECTL_BANNER = """
 ██████╗ ██╗   ██╗███████╗██╗   ██╗███████╗ ██████╗████████╗██╗     
██╔═══██╗██║   ██║██╔════╝██║   ██║██╔════╝██╔════╝╚══██╔══╝██║     
██║   ██║██║   ██║█████╗  ██║   ██║█████╗  ██║        ██║   ██║     
██║▄▄ ██║██║   ██║██╔══╝  ██║   ██║██╔══╝  ██║        ██║   ██║     
╚██████╔╝╚██████╔╝███████╗╚██████╔╝███████╗╚██████╗   ██║   ███████╗
 ╚══▀▀═╝  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝
"""

# Alternative simpler banner
QUEUECTL_SIMPLE = """
 ██████  ██    ██ ███████ ██    ██ ███████  ██████ ████████ ██      
██    ██ ██    ██ ██      ██    ██ ██      ██         ██    ██      
██    ██ ██    ██ █████   ██    ██ █████   ██         ██    ██      
██ ▄▄ ██ ██    ██ ██      ██    ██ ██      ██         ██    ██      
 ██████   ██████  ███████  ██████  ███████  ██████    ██    ███████ 
   ▀▀                                                               
"""

def show_banner():
    """Display the QueueCTL banner with branding"""
    # Create colored banner text
    banner_text = Text(QUEUECTL_SIMPLE, style="#bbfa01")
    
    # Version and tagline
    version_text = Text("v1.0.0", style="#bbfa01 bold")
    tagline_text = Text("CLI-based Background Job Queue System", style="#888888")
    
    console.print()
    console.print(banner_text, justify="center")
    console.print(version_text, justify="center")
    console.print(tagline_text, justify="center")
    console.print()


def show_quick_help():
    """Show quick help for new users"""
    
    # Quick start commands
    quick_start = Table(show_header=True, header_style="#bbfa01 bold", border_style="#bbfa01")
    quick_start.add_column("Quick Start", style="#bbfa01")
    quick_start.add_column("Command", style="white")
    
    quick_start.add_row("Interactive shell", "queuectl shell  (or queuectl -i)")
    quick_start.add_row("Add a job", 'queuectl enqueue "{\\"id\\":\\"test\\",\\"command\\":\\"echo hello\\"}"')
    quick_start.add_row("Start workers", "queuectl worker start --count 2")
    quick_start.add_row("Check status", "queuectl status")
    quick_start.add_row("List jobs", "queuectl list")
    
    # Main commands
    commands = Table(show_header=True, header_style="#bbfa01 bold", border_style="#bbfa01")
    commands.add_column("Command", style="#bbfa01")
    commands.add_column("Description", style="white")
    
    commands.add_row("enqueue <json>", "Add job to queue")
    commands.add_row("schedule <json>", "Schedule job with priority/timing")
    commands.add_row("worker start/stop", "Manage worker processes")
    commands.add_row("status", "Show system status")
    commands.add_row("list [--state]", "List jobs (all or by state)")
    commands.add_row("metrics", "Show performance metrics")
    commands.add_row("dashboard", "Start web monitoring dashboard")
    commands.add_row("dlq list/retry", "Dead Letter Queue management")
    commands.add_row("config set/get", "Configuration management")
    
    console.print(quick_start)
    console.print()
    console.print(commands)
    console.print()
    
    # Enhanced Features Panel
    features_text = (
        "[#bbfa01]New Features:[/#bbfa01]\n"
        "• Web Dashboard: [bold]queuectl dashboard[/bold] (http://localhost:8080)\n"
        "• Scheduled Jobs: Add 'run_at' field or use [bold]queuectl schedule[/bold]\n"
        "• Priority Queues: Set 'priority' field (higher = first)\n"
        "• Job Timeouts: Set 'timeout_seconds' field\n"
        "• Metrics: [bold]queuectl metrics[/bold] for performance stats\n"
        "• Interactive Shell: [bold]queuectl shell[/bold] for easier usage"
    )
    
    tips_panel = Panel(
        features_text,
        title="[#bbfa01]Enhanced Features[/#bbfa01]",
        border_style="#bbfa01",
        padding=(0, 1)
    )
    console.print(tips_panel)


def show_startup_screen():
    """Show complete startup screen with banner and help"""
    show_banner()
    show_quick_help()
    
    # Add some spacing and transition message
    console.print()
    console.print("[bold green]Starting Interactive Shell...[/bold green]")
    console.print("[dim]Type 'help' for command help, 'exit' to quit[/dim]")
    console.print()


def show_welcome_message():
    """Show a brief welcome message for command execution"""
    welcome_text = Text("QueueCTL", style="#bbfa01 bold")
    tagline_text = Text("Job Queue System", style="#888888")
    
    console.print(f"{welcome_text.plain} {tagline_text.plain}", style="dim")