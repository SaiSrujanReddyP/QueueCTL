"""
Worker Manager for handling multiple worker processes
"""

import os
import time
import multiprocessing
import threading
import subprocess
import sys
from typing import List, Dict
import signal
import logging

from .worker import worker_process


class WorkerManager:
    def __init__(self, job_queue, db_path: str = "jobs.db", lock_dir: str = "locks"):
        self.job_queue = job_queue
        self.db_path = db_path
        self.lock_dir = lock_dir
        self.workers: List[multiprocessing.Process] = []
        self.worker_pids: Dict[str, int] = {}
        
        # Ensure lock directory exists
        os.makedirs(lock_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('worker_manager')
    
    def start(self, count: int = 1):
        """Start the specified number of worker processes"""
        if self.workers:
            raise RuntimeError("Workers are already running. Stop them first.")
        
        self.logger.info(f"Starting {count} worker processes")
        
        for i in range(count):
            worker_id = f"worker_{int(time.time())}_{i}"
            
            # Use subprocess instead of multiprocessing for better Windows compatibility
            if os.name == 'nt':  # Windows
                # Create worker subprocess
                cmd = [
                    sys.executable, "-c",
                    f"from src.worker import worker_process; worker_process('{worker_id}', '{self.db_path}', '{self.lock_dir}')"
                ]
                process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                
                # Create a mock process object for compatibility
                class MockProcess:
                    def __init__(self, popen_obj, worker_id):
                        self.popen = popen_obj
                        self.pid = popen_obj.pid
                        self.name = worker_id
                        self._terminated = False
                    
                    def is_alive(self):
                        if self._terminated:
                            return False
                        return self.popen.poll() is None
                    
                    def terminate(self):
                        if not self._terminated:
                            try:
                                self.popen.terminate()
                                self._terminated = True
                            except:
                                pass
                    
                    def kill(self):
                        if not self._terminated:
                            try:
                                self.popen.kill()
                                self._terminated = True
                            except:
                                pass
                    
                    def join(self, timeout=None):
                        try:
                            self.popen.wait(timeout=timeout)
                        except:
                            pass
                
                mock_process = MockProcess(process, worker_id)
                self.workers.append(mock_process)
                self.worker_pids[worker_id] = process.pid
                
            else:  # Unix-like systems
                # Create worker process
                process = multiprocessing.Process(
                    target=worker_process,
                    args=(worker_id, self.db_path, self.lock_dir),
                    name=worker_id
                )
                
                process.start()
                self.workers.append(process)
                self.worker_pids[worker_id] = process.pid
            
            self.logger.info(f"Started worker {worker_id} (PID: {self.worker_pids[worker_id]})")
        
        # Clean up any stale lock files
        self._cleanup_stale_locks()
    
    def stop_all(self):
        """Stop all worker processes gracefully"""
        if not self.workers:
            self.logger.info("No workers to stop")
            return
        
        self.logger.info(f"Stopping {len(self.workers)} worker processes")
        
        # Send SIGTERM to all workers for graceful shutdown
        for process in self.workers:
            if process.is_alive():
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass  # Process already terminated
        
        # Wait for workers to finish gracefully
        timeout = 30  # 30 seconds timeout
        start_time = time.time()
        
        while self.workers and (time.time() - start_time) < timeout:
            self.workers = [p for p in self.workers if p.is_alive()]
            if self.workers:
                time.sleep(0.5)
        
        # Force kill any remaining workers
        for process in self.workers:
            if process.is_alive():
                self.logger.warning(f"Force killing worker {process.name}")
                try:
                    process.kill()
                    process.join(timeout=5)
                except ProcessLookupError:
                    pass
        
        # Clean up
        self.workers.clear()
        self.worker_pids.clear()
        self._cleanup_all_locks()
        
        self.logger.info("All workers stopped")
    
    def get_active_worker_count(self) -> int:
        """Get the number of currently active workers"""
        # Clean up dead processes
        self.workers = [p for p in self.workers if p.is_alive()]
        return len(self.workers)
    
    def wait_for_workers(self):
        """Wait for all worker processes to complete"""
        try:
            while self.workers:
                # Remove dead processes
                alive_workers = []
                for process in self.workers:
                    if process.is_alive():
                        alive_workers.append(process)
                    else:
                        # Process died, log it
                        self.logger.warning(f"Worker {process.name} died unexpectedly")
                
                self.workers = alive_workers
                
                if not self.workers:
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
            self.stop_all()
    
    def _cleanup_stale_locks(self):
        """Clean up lock files from dead processes"""
        if not os.path.exists(self.lock_dir):
            return
        
        try:
            for filename in os.listdir(self.lock_dir):
                if filename.endswith('.lock'):
                    lock_path = os.path.join(self.lock_dir, filename)
                    try:
                        # Try to read the worker ID from the lock file
                        with open(lock_path, 'r') as f:
                            worker_id = f.read().strip()
                        
                        # Check if the worker process is still alive
                        if worker_id in self.worker_pids:
                            pid = self.worker_pids[worker_id]
                            try:
                                # Send signal 0 to check if process exists
                                os.kill(pid, 0)
                                continue  # Process is alive, keep the lock
                            except (OSError, ProcessLookupError):
                                pass  # Process is dead, remove the lock
                        
                        # Remove stale lock file
                        os.remove(lock_path)
                        self.logger.info(f"Removed stale lock file: {filename}")
                        
                    except (IOError, OSError) as e:
                        self.logger.warning(f"Error processing lock file {filename}: {e}")
                        
        except OSError as e:
            self.logger.error(f"Error cleaning up locks: {e}")
    
    def _cleanup_all_locks(self):
        """Remove all lock files"""
        if not os.path.exists(self.lock_dir):
            return
        
        try:
            for filename in os.listdir(self.lock_dir):
                if filename.endswith('.lock'):
                    lock_path = os.path.join(self.lock_dir, filename)
                    try:
                        os.remove(lock_path)
                    except OSError:
                        pass  # Ignore errors during cleanup
        except OSError:
            pass  # Ignore errors during cleanup
    
    def get_worker_status(self) -> Dict[str, Dict]:
        """Get status information for all workers"""
        status = {}
        
        for process in self.workers:
            status[process.name] = {
                'pid': process.pid,
                'alive': process.is_alive(),
                'exitcode': process.exitcode
            }
        
        return status