#!/usr/bin/env python3
"""
QueueCTL Scheduler Daemon

This daemon runs in the background and automatically:
1. Converts scheduled jobs to pending when their time arrives
2. Processes pending jobs automatically
3. Handles job lifecycle management

Like a serverless function/lambda that triggers on schedule.
"""

import time
import datetime
import subprocess
import json
import threading
import signal
import sys
import os
from pathlib import Path

class SchedulerDaemon:
    def __init__(self, check_interval=5, worker_count=2, auto_mode=False):
        self.check_interval = check_interval  # Check every 5 seconds
        self.worker_count = worker_count
        self.auto_mode = auto_mode  # If True, automatically manage workers
        self.running = False
        self.worker_process = None
        self.log_file = Path("scheduler_daemon.log")
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        # Also write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def get_job_counts(self):
        """Get current job counts by state"""
        try:
            result = subprocess.run(
                "python queuectl.py list", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'dead': 0, 'scheduled': 0}
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if '|' in line and len(line.split('|')) >= 3:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            state = parts[2].strip().lower()
                            if state in counts:
                                counts[state] += 1
            
            return counts
        except Exception as e:
            self.log(f"Error getting job counts: {e}")
            return {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'dead': 0, 'scheduled': 0}
    
    def check_pending_jobs(self):
        """Check for pending jobs and log status (no auto-worker management)"""
        try:
            counts = self.get_job_counts()
            
            if counts['pending'] > 0:
                self.log(f"Found {counts['pending']} pending jobs waiting for workers")
                
            return counts['pending']
                
        except Exception as e:
            self.log(f"Error checking pending jobs: {e}")
            return 0
    
    def ensure_workers_running(self):
        """Ensure workers are running to process pending jobs (auto mode only)"""
        try:
            # Check if workers are already running
            result = subprocess.run(
                "python queuectl.py worker status", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if "No workers" in result.stdout or not result.stdout.strip():
                # No workers running, start them
                self.log(f"Auto mode: Starting {self.worker_count} workers...")
                
                # Start workers in background
                self.worker_process = subprocess.Popen(
                    f"python queuectl.py worker start --count {self.worker_count}",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                self.log(f"Workers started (PID: {self.worker_process.pid})")
                return True
            else:
                # Workers already running
                return True
                
        except Exception as e:
            self.log(f"Error managing workers: {e}")
            return False
    
    def process_scheduled_jobs(self):
        """Check for scheduled jobs that should become pending"""
        try:
            # Get scheduled jobs
            result = subprocess.run(
                "python queuectl.py list --state scheduled", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.stdout and "No jobs found" not in result.stdout:
                scheduled_count = 0
                for line in result.stdout.split('\n'):
                    if '| scheduled |' in line:
                        scheduled_count += 1
                
                if scheduled_count > 0:
                    self.log(f"Found {scheduled_count} scheduled jobs - they will auto-convert to pending when ready")
            
        except Exception as e:
            self.log(f"Error processing scheduled jobs: {e}")
    
    def daemon_loop(self):
        """Main daemon loop - handles scheduled job conversion"""
        mode_text = "auto worker management" if self.auto_mode else "manual worker control"
        self.log(f"Scheduler daemon started ({mode_text} mode)")
        self.log(f"Check interval: {self.check_interval} seconds")
        
        if not self.auto_mode:
            self.log("Workers must be started manually using 'worker start' command")
        else:
            self.log(f"Will automatically manage {self.worker_count} workers")
        
        while self.running:
            try:
                # Check for stop file
                if os.path.exists("scheduler_daemon.stop"):
                    self.log("Stop file detected, shutting down...")
                    os.remove("scheduler_daemon.stop")
                    break
                
                # Get current job status
                counts = self.get_job_counts()
                
                # Log status periodically (every 12 checks = 1 minute if check_interval=5)
                if hasattr(self, 'check_counter'):
                    self.check_counter += 1
                else:
                    self.check_counter = 1
                
                if self.check_counter % 12 == 0:
                    self.log(f"Status: Pending={counts['pending']}, Processing={counts['processing']}, Scheduled={counts['scheduled']}")
                
                # Process scheduled jobs (they auto-convert in QueueCTL)
                if counts['scheduled'] > 0:
                    self.process_scheduled_jobs()
                
                # Handle pending jobs based on mode
                if counts['pending'] > 0:
                    if self.auto_mode:
                        # Auto mode: start workers automatically
                        self.ensure_workers_running()
                    else:
                        # Manual mode: just log pending jobs
                        self.check_pending_jobs()
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Error in daemon loop: {e}")
                time.sleep(self.check_interval)
        
        self.log("Scheduler daemon stopped")
    
    def start(self):
        """Start the daemon"""
        if self.running:
            self.log("Daemon is already running")
            return
        
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.log(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start daemon loop
        self.daemon_loop()
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        
        # Stop workers if we started them
        if self.worker_process:
            try:
                subprocess.run("python queuectl.py worker stop", shell=True, timeout=5)
                self.log("Stopped workers")
            except:
                pass
        
        self.log("Daemon shutdown complete")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="QueueCTL Scheduler Daemon")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
    parser.add_argument("--workers", type=int, default=2, help="Number of workers to maintain (default: 2)")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--auto", action="store_true", help="Auto mode: automatically start/manage workers")
    
    args = parser.parse_args()
    
    daemon = SchedulerDaemon(check_interval=args.interval, worker_count=args.workers, auto_mode=args.auto)
    
    if args.daemon:
        # Run as background daemon (detached)
        if os.name == 'nt':  # Windows
            # Use subprocess to detach
            subprocess.Popen([
                sys.executable, __file__, 
                "--interval", str(args.interval),
                "--workers", str(args.workers)
            ], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            print("Scheduler daemon started in background")
        else:  # Unix/Linux
            # Fork to background
            if os.fork() == 0:
                daemon.start()
            else:
                print("Scheduler daemon started in background")
    else:
        # Run in foreground
        daemon.start()

if __name__ == "__main__":
    main()