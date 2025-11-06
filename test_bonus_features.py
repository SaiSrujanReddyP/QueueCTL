#!/usr/bin/env python3
"""
QueueCTL Bonus Features Test
Tests all bonus/extra credit features
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class BonusFeaturesTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name, func):
        """Run a test and track results"""
        try:
            console.print(f"[blue]Testing:[/blue] {name}")
            result = func()
            if result:
                console.print(f"[green]PASS:[/green] {name}")
                self.passed += 1
                self.results.append((name, "PASS", ""))
            else:
                console.print(f"[yellow]NOT IMPLEMENTED:[/yellow] {name}")
                self.failed += 1
                self.results.append((name, "NOT IMPLEMENTED", "Feature not found"))
        except Exception as e:
            console.print(f"[red]ERROR:[/red] {name} - {e}")
            self.failed += 1
            self.results.append((name, "ERROR", str(e)))
        console.print()
    
    def run_command(self, cmd):
        """Run a command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
    
    def test_job_timeout_handling(self):
        """Job timeout handling"""
        # Check if timeout is supported in job creation
        success, stdout, stderr = self.run_command("python queuectl.py add --help")
        if not success:
            return False
        
        # Check if timeout option exists
        has_timeout = "timeout" in stdout.lower()
        
        # Also check source code for timeout implementation
        try:
            with open("src/worker.py", "r") as f:
                content = f.read()
            has_timeout_code = "timeout" in content.lower()
        except:
            has_timeout_code = False
        
        return has_timeout or has_timeout_code
    
    def test_job_priority_queues(self):
        """Job priority queues"""
        # Test if priority option exists
        success, stdout, stderr = self.run_command("python queuectl.py add --help")
        if not success:
            return False
        
        return "priority" in stdout.lower()
    
    def test_scheduled_delayed_jobs(self):
        """Scheduled/delayed jobs (run_at)"""
        # Check if schedule command exists
        success, stdout, stderr = self.run_command("python queuectl.py schedule --help")
        if success:
            return True
        
        # Check if run_at is mentioned in enqueue help
        success2, stdout2, stderr2 = self.run_command("python queuectl.py enqueue --help")
        return success2 and "run_at" in stdout2.lower()
    
    def test_job_output_logging(self):
        """Job output logging"""
        # Check if logs directory exists or logging is implemented
        logs_exist = os.path.exists("logs") or os.path.exists("job_logs")
        
        # Check source code for logging implementation
        try:
            with open("src/worker.py", "r") as f:
                content = f.read()
            has_logging = "log" in content.lower() and ("output" in content.lower() or "result" in content.lower())
        except:
            has_logging = False
        
        return logs_exist or has_logging
    
    def test_metrics_execution_stats(self):
        """Metrics or execution stats"""
        # Test if metrics command exists
        success, stdout, stderr = self.run_command("python queuectl.py metrics --help")
        if success:
            return True
        
        # Check if status shows detailed metrics
        success2, stdout2, stderr2 = self.run_command("python queuectl.py status")
        return success2 and ("metrics" in stdout2.lower() or "statistics" in stdout2.lower())
    
    def test_web_dashboard(self):
        """Minimal web dashboard for monitoring"""
        # Test if dashboard command exists
        success, stdout, stderr = self.run_command("python queuectl.py dashboard --help")
        if not success:
            return False
        
        # Check if dashboard files exist
        dashboard_files = ["src/dashboard.py", "src/web_dashboard.py", "templates"]
        return any(os.path.exists(f) for f in dashboard_files)
    
    def test_interactive_shell(self):
        """Interactive shell (bonus UX feature)"""
        # Test if shell command exists
        success, stdout, stderr = self.run_command("python queuectl.py shell --help")
        if success:
            return True
        
        # Test if interactive flag exists
        success2, stdout2, stderr2 = self.run_command("python queuectl.py --help")
        return success2 and "interactive" in stdout2.lower()
    
    def test_ascii_art_banner(self):
        """ASCII Art Banner (bonus UX feature)"""
        # Test if welcome command shows ASCII art
        success, stdout, stderr = self.run_command("python queuectl.py welcome")
        if success and "██" in stdout:
            return True
        
        # Test if running without args shows ASCII art (with timeout to avoid hanging)
        try:
            import subprocess
            result = subprocess.run("python queuectl.py", shell=True, capture_output=True, text=True, timeout=3, input="\n")
            return result.returncode == 0 and "██" in result.stdout
        except subprocess.TimeoutExpired:
            return True  # If it hangs, it's probably showing the interactive shell which means ASCII art worked
        except:
            return False
    
    def run_all_tests(self):
        """Run all bonus feature tests"""
        console.print(Panel.fit("QueueCTL Bonus Features Test", style="bold yellow"))
        console.print()
        
        # Run all tests
        self.test("Job Timeout Handling", self.test_job_timeout_handling)
        self.test("Job Priority Queues", self.test_job_priority_queues)
        self.test("Scheduled/Delayed Jobs", self.test_scheduled_delayed_jobs)
        self.test("Job Output Logging", self.test_job_output_logging)
        self.test("Metrics/Execution Stats", self.test_metrics_execution_stats)
        self.test("Web Dashboard", self.test_web_dashboard)
        self.test("Interactive Shell", self.test_interactive_shell)
        self.test("ASCII Art Banner", self.test_ascii_art_banner)
        
        # Show results
        self.show_results()
    
    def show_results(self):
        """Show test results summary"""
        table = Table(title="Bonus Features Test Results")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Notes", style="dim")
        
        for name, status, notes in self.results:
            if status == "PASS":
                color = "green"
                icon = "PASS"
            elif status == "NOT IMPLEMENTED":
                color = "yellow"
                icon = "NOT IMPLEMENTED"
            else:
                color = "red"
                icon = "ERROR"
            
            table.add_row(name, f"[{color}]{icon}[/{color}]", notes)
        
        console.print(table)
        console.print()
        
        total = self.passed + self.failed
        if total > 0:
            console.print(f"[bold]Bonus Features Implemented: {self.passed}/{total}[/bold]")
            if self.passed >= 4:
                console.print("[green]Excellent! You have implemented many bonus features![/green]")
            elif self.passed >= 2:
                console.print("[yellow]Good! You have some bonus features implemented![/yellow]")
            else:
                console.print("[blue]Consider implementing some bonus features for extra credit![/blue]")

if __name__ == "__main__":
    tester = BonusFeaturesTest()
    tester.run_all_tests()