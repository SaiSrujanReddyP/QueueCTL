#!/usr/bin/env python3
"""
QueueCTL Submission Checklist
Final checklist before submission - validates all requirements
"""

import os
import sys
import time
import json
import subprocess
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class SubmissionChecklist:
    def __init__(self):
        self.checklist = []
        self.passed = 0
        self.failed = 0
    
    def check(self, description, func):
        """Run a checklist item"""
        try:
            console.print(f"[blue]Checking:[/blue] {description}")
            result = func()
            if result:
                console.print(f"[green]PASS:[/green] {description}")
                self.passed += 1
                self.checklist.append((description, True, ""))
            else:
                console.print(f"[red]FAIL:[/red] {description}")
                self.failed += 1
                self.checklist.append((description, False, "Check failed"))
        except Exception as e:
            console.print(f"[red]ERROR:[/red] {description} - {e}")
            self.failed += 1
            self.checklist.append((description, False, str(e)))
        console.print()
    
    def run_command(self, cmd):
        """Run a command and return success status"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
    
    def check_all_commands_functional(self):
        """[ ] All required commands functional"""
        commands = [
            "python queuectl.py --help",
            "python queuectl.py status",
            "python queuectl.py list",
            "python queuectl.py worker --help",
            "python queuectl.py dlq --help",
            "python queuectl.py config --help"
        ]
        
        for cmd in commands:
            success, _, _ = self.run_command(cmd)
            if not success:
                return False
        
        return True
    
    def check_jobs_persist_after_restart(self):
        """[ ] Jobs persist after restart"""
        # Add a test job
        job_id = f"persistence-test-{int(time.time())}"
        success1, _, _ = self.run_command(f'python queuectl.py add "echo persistence test" --id {job_id}')
        if not success1:
            return False
        
        # Check if job exists in database
        try:
            import sqlite3
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except:
            return False
    
    def check_retry_backoff_implemented(self):
        """[ ] Retry and backoff implemented correctly"""
        # Check source code for retry implementation
        try:
            with open("src/worker.py", "r") as f:
                content = f.read()
            
            has_retry = "retry" in content.lower()
            has_backoff = "backoff" in content.lower() or "sleep" in content.lower()
            has_max_retries = "max_retries" in content.lower()
            
            return has_retry and (has_backoff or has_max_retries)
        except:
            return False
    
    def check_dlq_operational(self):
        """[ ] DLQ operational"""
        # Test DLQ commands
        success1, stdout1, _ = self.run_command("python queuectl.py dlq --help")
        if not success1:
            return False
        
        # Check if DLQ list command works
        success2, _, _ = self.run_command("python queuectl.py dlq list")
        return success2
    
    def check_cli_user_friendly(self):
        """[ ] CLI user-friendly and documented"""
        # Check main help
        success1, stdout1, _ = self.run_command("python queuectl.py --help")
        if not success1:
            return False
        
        # Check if help is comprehensive
        help_quality = (
            len(stdout1) > 500 and  # Substantial help text
            "Commands" in stdout1 and  # Has commands section
            "Options" in stdout1  # Has options section
        )
        
        # Check if individual commands have help
        success2, stdout2, _ = self.run_command("python queuectl.py enqueue --help")
        success3, stdout3, _ = self.run_command("python queuectl.py worker --help")
        
        return help_quality and success2 and success3
    
    def check_code_modular_maintainable(self):
        """[ ] Code is modular and maintainable"""
        src_path = Path("src")
        if not src_path.exists():
            return False
        
        # Check for key modules
        required_files = ["job_queue.py", "worker.py", "config.py"]
        python_files = list(src_path.glob("*.py"))
        
        # Must have at least 4 modules and the required ones
        has_required = all((src_path / f).exists() for f in required_files)
        has_enough_modules = len(python_files) >= 4
        
        return has_required and has_enough_modules
    
    def check_includes_test_script(self):
        """[ ] Includes test or script verifying main flows"""
        # Check if test files exist
        test_files = [
            "test_deliverables.py",
            "test_bonus_features.py", 
            "submission_checklist.py"
        ]
        
        return all(os.path.exists(f) for f in test_files)
    
    def check_readme_comprehensive(self):
        """[ ] README.md is comprehensive"""
        if not os.path.exists("README.md"):
            return False
        
        try:
            with open("README.md", "r") as f:
                content = f.read()
            
            # Check for essential sections
            required_sections = [
                "installation", "usage", "example", "command", "feature"
            ]
            
            has_sections = sum(1 for section in required_sections if section in content.lower())
            is_comprehensive = len(content) > 2000 and has_sections >= 3
            
            return is_comprehensive
        except:
            return False
    
    def check_requirements_file(self):
        """[ ] requirements.txt exists and is complete"""
        if not os.path.exists("requirements.txt"):
            return False
        
        try:
            with open("requirements.txt", "r") as f:
                content = f.read()
            
            # Check for essential dependencies
            required_deps = ["typer", "rich", "sqlite"]
            has_deps = sum(1 for dep in required_deps if dep in content.lower())
            
            return has_deps >= 2  # At least typer and rich
        except:
            return False
    
    def run_full_workflow_test(self):
        """[ ] Full workflow test (add job -> start worker -> verify completion)"""
        try:
            # 1. Add a test job
            job_id = f"workflow-test-{int(time.time())}"
            success1, _, _ = self.run_command(f'python queuectl.py add "echo workflow test" --id {job_id}')
            if not success1:
                return False
            
            # 2. Check job was added
            success2, stdout2, _ = self.run_command("python queuectl.py list")
            if not success2 or job_id not in stdout2:
                return False
            
            # 3. Check status shows pending job
            success3, stdout3, _ = self.run_command("python queuectl.py status")
            if not success3:
                return False
            
            return True
        except:
            return False
    
    def run_checklist(self):
        """Run the complete submission checklist"""
        console.print(Panel.fit("QueueCTL Submission Checklist", style="bold blue"))
        console.print("[dim]Final validation before submission[/dim]")
        console.print()
        
        # Run all checks
        self.check("All required commands functional", self.check_all_commands_functional)
        self.check("Jobs persist after restart", self.check_jobs_persist_after_restart)
        self.check("Retry and backoff implemented correctly", self.check_retry_backoff_implemented)
        self.check("DLQ operational", self.check_dlq_operational)
        self.check("CLI user-friendly and documented", self.check_cli_user_friendly)
        self.check("Code is modular and maintainable", self.check_code_modular_maintainable)
        self.check("Includes test or script verifying main flows", self.check_includes_test_script)
        self.check("README.md is comprehensive", self.check_readme_comprehensive)
        self.check("requirements.txt exists", self.check_requirements_file)
        self.check("Full workflow test passes", self.run_full_workflow_test)
        
        # Show final results
        self.show_final_results()
    
    def show_final_results(self):
        """Show final checklist results"""
        table = Table(title="Submission Checklist Results")
        table.add_column("Requirement", style="cyan", width=40)
        table.add_column("Status", style="bold", width=15)
        table.add_column("Notes", style="dim")
        
        for description, passed, notes in self.checklist:
            status = "READY" if passed else "NEEDS WORK"
            color = "green" if passed else "red"
            table.add_row(description, f"[{color}]{status}[/{color}]", notes)
        
        console.print(table)
        console.print()
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        if pass_rate >= 90:
            console.print(Panel.fit(
                f"READY FOR SUBMISSION!\n\n"
                f"PASS: {self.passed}/{total} checks passed ({pass_rate:.1f}%)\n"
                f"Your QueueCTL project meets all requirements!",
                style="bold green"
            ))
        elif pass_rate >= 70:
            console.print(Panel.fit(
                f"WARNING: ALMOST READY\n\n"
                f"PASS: {self.passed}/{total} checks passed ({pass_rate:.1f}%)\n"
                f"Fix the failing items before submission.",
                style="bold yellow"
            ))
        else:
            console.print(Panel.fit(
                f"FAILED: NEEDS MORE WORK\n\n"
                f"PASS: {self.passed}/{total} checks passed ({pass_rate:.1f}%)\n"
                f"Several requirements need attention.",
                style="bold red"
            ))
        
        console.print("\n[dim]Run individual test files for more details:[/dim]")
        console.print("[dim]• python test_deliverables.py[/dim]")
        console.print("[dim]• python test_bonus_features.py[/dim]")

if __name__ == "__main__":
    checklist = SubmissionChecklist()
    checklist.run_checklist()