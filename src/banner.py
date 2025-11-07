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
    """Show command help for users"""
    
    # Main commands
    commands = Table(show_header=True, header_style="#bbfa01 bold", border_style="#bbfa01")
    commands.add_column("Command", style="#bbfa01")
    commands.add_column("Description", style="white")
    
    commands.add_row("enqueue <json>", "Add job to queue with scheduling/priority")
    commands.add_row("worker start/stop", "Manage worker processes")
    commands.add_row("scheduler start/stop", "Manage scheduler daemon")
    commands.add_row("status", "Show system status with job counts")
    commands.add_row("list [--state]", "List jobs with full IDs (pending/dead/scheduled)")
    commands.add_row("metrics", "Show performance metrics and statistics")
    commands.add_row("dashboard", "Start web monitoring dashboard")
    commands.add_row("dlq list/retry", "Dead Letter Queue management")
    commands.add_row("config set/get", "Configuration management")
    commands.add_row("shell", "Interactive shell mode")
    
    console.print(commands)
    console.print()
    
    # Enhanced Features Panel
    features_text = (
        "[#bbfa01]Recent Improvements:[/#bbfa01]\n"
        "• Full Job IDs: Complete job IDs displayed in all list commands\n"
        "• Compact Display: Optimized table layout (Tries/Created columns)\n"
        "• Enhanced Errors: Colored error messages with helpful suggestions\n"
        "• Scheduler Daemon: Background processing for scheduled jobs\n"
        "• Priority Queues: Set 'priority' field (higher = processed first)\n"
        "• Scheduled Jobs: Use 'run_at' field (+30s, +5m, ISO format)\n"
        "• Web Dashboard: [bold]queuectl dashboard[/bold] (http://localhost:8080)\n"
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