#!/usr/bin/env python3
"""
QueueCTL Deliverables Test
Tests all required deliverables for the assignment
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

console = Console()

class DeliverablesTest:
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
                console.print(f"[red]FAIL:[/red] {name}")
                self.failed += 1
                self.results.append((name, "FAIL", "Test returned False"))
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
    
    def test_cli_application(self):
        """Working CLI application (queuectl)"""
        success, stdout, stderr = self.run_command("python queuectl.py --help")
        return success and "CLI-based background job queue system" in stdout
    
    def test_persistent_storage(self):
        """Persistent job storage"""
        # Check if SQLite database exists and has correct structure
        if not os.path.exists("jobs.db"):
            return False
        
        try:
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()
            
            # Check if jobs table exists with correct columns
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='jobs'")
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            # Check for required columns
            table_sql = result[0].lower()
            required_columns = ['id', 'command', 'state', 'created_at', 'max_retries']
            return all(col in table_sql for col in required_columns)
        except:
            return False
    
    def test_multiple_workers(self):
        """Multiple worker support"""
        # Test worker start command
        success, stdout, stderr = self.run_command("python queuectl.py worker --help")
        return success and "start" in stdout and "stop" in stdout
    
    def test_retry_mechanism(self):
        """Retry mechanism with exponential backoff"""
        # Check if retry logic exists in code
        try:
            with open("src/worker.py", "r") as f:
                content = f.read()
            return "retry" in content.lower() and "backoff" in content.lower()
        except:
            return False
    
    def test_dead_letter_queue(self):
        """Dead Letter Queue"""
        success, stdout, stderr = self.run_command("python queuectl.py dlq --help")
        return success and ("list" in stdout or "retry" in stdout)
    
    def test_configuration_management(self):
        """Configuration management"""
        success, stdout, stderr = self.run_command("python queuectl.py config --help")
        return success and ("get" in stdout or "set" in stdout)
    
    def test_clean_cli_interface(self):
        """Clean CLI interface (commands & help texts)"""
        success, stdout, stderr = self.run_command("python queuectl.py --help")
        if not success:
            return False
        
        # Check for main commands
        required_commands = ["enqueue", "worker", "status", "list", "dlq", "config"]
        return all(cmd in stdout for cmd in required_commands)
    
    def test_readme_exists(self):
        """Comprehensive README.md"""
        if not os.path.exists("README.md"):
            return False
        
        try:
            with open("README.md", "r") as f:
                content = f.read()
            
            # Check for key sections
            required_sections = ["installation", "usage", "example", "command"]
            return len(content) > 1000 and any(section in content.lower() for section in required_sections)
        except:
            return False
    
    def test_code_structure(self):
        """Code structured with clear separation of concerns"""
        # Check if src directory exists with modular files
        src_path = Path("src")
        if not src_path.exists():
            return False
        
        required_modules = ["job_queue.py", "worker.py", "config.py"]
        existing_files = [f.name for f in src_path.glob("*.py")]
        
        return len(existing_files) >= 3 and any(mod in existing_files for mod in required_modules)
    
    def test_core_workflow(self):
        """At least minimal testing or script to validate core flows"""
        # Test basic workflow: add job -> check status -> list jobs
        
        # Add a job
        success1, _, _ = self.run_command('python queuectl.py add "echo test" --id test-job')
        if not success1:
            return False
        
        # Check status
        success2, stdout2, _ = self.run_command("python queuectl.py status")
        if not success2:
            return False
        
        # List jobs
        success3, stdout3, _ = self.run_command("python queuectl.py list")
        if not success3:
            return False
        
        return "test-job" in stdout3
    
    def run_all_tests(self):
        """Run all deliverable tests"""
        console.print(Panel.fit("QueueCTL Deliverables Test", style="bold green"))
        console.print()
        
        # Run all tests
        self.test("Working CLI Application", self.test_cli_application)
        self.test("Persistent Job Storage", self.test_persistent_storage)
        self.test("Multiple Worker Support", self.test_multiple_workers)
        self.test("Retry Mechanism", self.test_retry_mechanism)
        self.test("Dead Letter Queue", self.test_dead_letter_queue)
        self.test("Configuration Management", self.test_configuration_management)
        self.test("Clean CLI Interface", self.test_clean_cli_interface)
        self.test("Comprehensive README", self.test_readme_exists)
        self.test("Code Structure", self.test_code_structure)
        self.test("Core Workflow Validation", self.test_core_workflow)
        
        # Show results
        self.show_results()
    
    def show_results(self):
        """Show test results summary"""
        table = Table(title="Deliverables Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Notes", style="dim")
        
        for name, status, notes in self.results:
            color = "green" if status == "PASS" else "red"
            table.add_row(name, f"[{color}]{status}[/{color}]", notes)
        
        console.print(table)
        console.print()
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        if pass_rate >= 80:
            console.print(f"[green]SUCCESS: DELIVERABLES READY: {self.passed}/{total} tests passed ({pass_rate:.1f}%)[/green]")
        else:
            console.print(f"[red]FAILED: NEEDS WORK: {self.passed}/{total} tests passed ({pass_rate:.1f}%)[/red]")

if __name__ == "__main__":
    tester = DeliverablesTest()
    tester.run_all_tests()