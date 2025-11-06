"""
Worker implementation for processing jobs
"""

import os
import time
import subprocess
import multiprocessing
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
import logging

from .job_queue import JobQueue
from .config import Config


class Worker:
    def __init__(self, worker_id: str, db_path: str = "jobs.db", lock_dir: str = "locks"):
        self.worker_id = worker_id
        self.db_path = db_path
        self.lock_dir = lock_dir
        self.job_queue = JobQueue(db_path)
        self.config = Config(db_path)
        self.running = False
        self.current_job = None
        
        # Ensure lock directory exists
        os.makedirs(lock_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format=f'[{worker_id}] %(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'worker_{worker_id}')
    
    def start(self):
        """Start the worker main loop"""
        self.running = True
        self.logger.info(f"Worker {self.worker_id} started")
        
        try:
            while self.running:
                try:
                    self._process_next_job()
                    time.sleep(1)  # Poll every second
                except Exception as e:
                    self.logger.error(f"Error in worker loop: {e}")
                    time.sleep(5)  # Wait longer on error
        except KeyboardInterrupt:
            self.logger.info("Worker interrupted")
        finally:
            self.logger.info(f"Worker {self.worker_id} stopped")
    
    def stop(self):
        """Stop the worker gracefully"""
        self.running = False
    
    def _process_next_job(self):
        """Process the next available job"""
        job = self.job_queue.get_next_job()
        if not job:
            return
        
        # Try to acquire lock for this job
        lock_file = os.path.join(self.lock_dir, f"{job['id']}.lock")
        
        try:
            # Atomic lock creation (fails if file exists)
            with open(lock_file, 'x') as f:
                f.write(self.worker_id)
        except FileExistsError:
            # Job is already being processed by another worker
            return
        
        try:
            self.current_job = job
            self._execute_job(job)
        finally:
            # Always release the lock
            try:
                os.remove(lock_file)
            except FileNotFoundError:
                pass  # Lock file might have been cleaned up already
            self.current_job = None
    
    def _execute_job(self, job: Dict[str, Any]):
        """Execute a single job with enhanced logging and metrics"""
        job_id = job['id']
        command = job['command']
        timeout_seconds = job.get('timeout_seconds', 300)
        
        self.logger.info(f"Processing job {job_id}: {command} (timeout: {timeout_seconds}s)")
        
        # Update job state to processing with start time and worker ID
        start_time = datetime.now(timezone.utc).isoformat()
        self.job_queue.update_job_state(
            job_id, 'processing',
            started_at=start_time,
            worker_id=self.worker_id
        )
        
        # Log job start metric
        self.job_queue._log_job_metric(job_id, 'started', {
            'worker_id': self.worker_id,
            'timeout_seconds': timeout_seconds
        })
        
        try:
            # Execute the command with timeout
            result = self._run_command(command, timeout_seconds)
            
            completion_time = datetime.now(timezone.utc).isoformat()
            
            if result['success']:
                # Job completed successfully
                self.job_queue.update_job_state(
                    job_id, 'completed',
                    output=result['output'],
                    completed_at=completion_time,
                    execution_time_ms=result['execution_time_ms']
                )
                
                # Log success metrics
                self.job_queue._log_job_metric(job_id, 'completed', {
                    'execution_time_ms': result['execution_time_ms'],
                    'output_length': len(result['output'])
                })
                
                self.logger.info(f"Job {job_id} completed successfully in {result['execution_time_ms']}ms")
            else:
                # Job failed, handle retry logic
                self._handle_job_failure(job, result['error'], result['execution_time_ms'])
                
        except Exception as e:
            self.logger.error(f"Error executing job {job_id}: {e}")
            self._handle_job_failure(job, str(e), 0)
    
    def _run_command(self, command: str, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Execute a shell command with configurable timeout"""
        start_time = time.time()
        
        try:
            # Use shell=True to handle complex commands
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            execution_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            return {
                'success': process.returncode == 0,
                'output': process.stdout.strip(),
                'error': process.stderr.strip() if process.stderr else 
                        (f"Command exited with code {process.returncode}" if process.returncode != 0 else ""),
                'execution_time_ms': execution_time
            }
            
        except subprocess.TimeoutExpired:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {timeout_seconds} seconds',
                'execution_time_ms': execution_time
            }
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'output': '',
                'error': f"Failed to execute command: {str(e)}",
                'execution_time_ms': execution_time
            }
    
    def _handle_job_failure(self, job: Dict[str, Any], error_message: str, execution_time_ms: int = 0):
        """Handle job failure with retry logic and enhanced logging"""
        job_id = job['id']
        new_attempts = job['attempts'] + 1
        max_retries = job['max_retries']
        
        if new_attempts >= max_retries:
            # Move to Dead Letter Queue
            completion_time = datetime.now(timezone.utc).isoformat()
            self.job_queue.update_job_state(
                job_id, 'dead',
                attempts=new_attempts,
                error=error_message,
                completed_at=completion_time,
                execution_time_ms=execution_time_ms
            )
            
            # Log DLQ metric
            self.job_queue._log_job_metric(job_id, 'moved_to_dlq', {
                'final_attempts': new_attempts,
                'error': error_message[:200]  # Truncate long errors
            })
            
            self.logger.warning(f"Job {job_id} moved to DLQ after {new_attempts} attempts")
        else:
            # Schedule retry with exponential backoff
            backoff_base = float(self.config.get('backoff-base', 2))
            delay_seconds = int(backoff_base ** new_attempts)
            
            next_retry_at = (datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)).isoformat()
            
            self.job_queue.update_job_state(
                job_id, 'failed',
                attempts=new_attempts,
                next_retry_at=next_retry_at,
                error=error_message,
                execution_time_ms=execution_time_ms
            )
            
            # Log retry metric
            self.job_queue._log_job_metric(job_id, 'retry_scheduled', {
                'attempt': new_attempts,
                'delay_seconds': delay_seconds,
                'error': error_message[:200]
            })
            
            self.logger.info(f"Job {job_id} scheduled for retry in {delay_seconds}s "
                           f"(attempt {new_attempts}/{max_retries})")


def worker_process(worker_id: str, db_path: str, lock_dir: str):
    """Worker process entry point"""
    worker = Worker(worker_id, db_path, lock_dir)
    worker.start()