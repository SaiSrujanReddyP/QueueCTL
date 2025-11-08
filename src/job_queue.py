"""
Job Queue implementation with SQLite persistence
"""

import sqlite3
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import threading


class JobQueue:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database and create tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Enhanced jobs table with new features
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    state TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    priority INTEGER DEFAULT 0,
                    timeout_seconds INTEGER DEFAULT 300,
                    run_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    next_retry_at TEXT,
                    output TEXT,
                    error TEXT,
                    execution_time_ms INTEGER DEFAULT 0,
                    worker_id TEXT
                )
            """)
            
            # Job metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            """)
            
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Add new columns to existing tables if they don't exist
            self._migrate_database(conn)
            
            # Create indexes for efficient querying (after migration)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_job ON job_metrics(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
            conn.commit()
    
    def _migrate_database(self, conn):
        """Add new columns to existing database"""
        new_columns = [
            ("priority", "INTEGER DEFAULT 0"),
            ("timeout_seconds", "INTEGER DEFAULT 300"),
            ("run_at", "TEXT"),
            ("started_at", "TEXT"),
            ("completed_at", "TEXT"),
            ("execution_time_ms", "INTEGER DEFAULT 0"),
            ("worker_id", "TEXT")
        ]
        
        for column_name, column_def in new_columns:
            try:
                conn.execute(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_def}")
            except sqlite3.OperationalError:
                # Column already exists
                pass
        
        # Create indexes after ensuring columns exist
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_state_priority ON jobs(state, priority DESC, created_at)")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_run_at ON jobs(run_at)")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_next_retry ON jobs(next_retry_at)")
        except sqlite3.OperationalError:
            pass
    
    def enqueue(self, job_data: Dict[str, Any], force_replace: bool = False) -> Dict[str, Any]:
        """Add a new job to the queue with enhanced features"""
        with self._lock:
            job_id = job_data.get('id', str(uuid.uuid4()))
            now = datetime.now(timezone.utc).isoformat()
            
            # Check if job already exists
            existing_job = self.get_job(job_id)
            if existing_job and not force_replace:
                raise ValueError(f"Job with ID '{job_id}' already exists. Use force_replace=True to overwrite.")
            
            # Handle scheduled jobs
            run_at = job_data.get('run_at')
            if run_at:
                if isinstance(run_at, str):
                    # Parse ISO format or relative time
                    if run_at.startswith('+'):
                        # Relative time like "+5m", "+1h", "+30s"
                        run_at = self._parse_relative_time(run_at)
                    # else assume it's already ISO format
                else:
                    run_at = run_at.isoformat() if hasattr(run_at, 'isoformat') else str(run_at)
            
            job = {
                'id': job_id,
                'command': job_data['command'],
                'state': 'scheduled' if run_at and run_at > now else 'pending',
                'attempts': 0,
                'max_retries': job_data.get('max_retries', 3),
                'priority': job_data.get('priority', 0),
                'timeout_seconds': job_data.get('timeout_seconds', 300),
                'run_at': run_at,
                'created_at': now,
                'updated_at': now,
                'started_at': None,
                'completed_at': None,
                'next_retry_at': None,
                'output': None,
                'error': None,
                'execution_time_ms': 0,
                'worker_id': None
            }
            
            with sqlite3.connect(self.db_path) as conn:
                if existing_job and force_replace:
                    # Update existing job
                    conn.execute("""
                        UPDATE jobs SET command = ?, state = ?, attempts = 0, max_retries = ?, 
                                      priority = ?, timeout_seconds = ?, run_at = ?, updated_at = ?,
                                      started_at = NULL, completed_at = NULL, next_retry_at = NULL,
                                      output = NULL, error = NULL, execution_time_ms = 0, worker_id = NULL
                        WHERE id = ?
                    """, (
                        job['command'], job['state'], job['max_retries'], job['priority'],
                        job['timeout_seconds'], job['run_at'], job['updated_at'], job['id']
                    ))
                else:
                    # Insert new job
                    conn.execute("""
                        INSERT INTO jobs (id, command, state, attempts, max_retries, priority,
                                        timeout_seconds, run_at, created_at, updated_at, started_at,
                                        completed_at, next_retry_at, output, error, execution_time_ms, worker_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        job['id'], job['command'], job['state'], job['attempts'],
                        job['max_retries'], job['priority'], job['timeout_seconds'],
                        job['run_at'], job['created_at'], job['updated_at'],
                        job['started_at'], job['completed_at'], job['next_retry_at'],
                        job['output'], job['error'], job['execution_time_ms'], job['worker_id']
                    ))
                conn.commit()
            
            # Log job creation metric
            action = 'replaced' if existing_job and force_replace else 'created'
            self._log_job_metric(job_id, action, {'priority': job['priority'], 'scheduled': bool(run_at)})
            
            return job
    
    def _parse_relative_time(self, relative_time: str) -> str:
        """Parse relative time strings like '+5m', '+1h', '+30s'"""
        import re
        
        match = re.match(r'\+(\d+)([smhd])', relative_time.lower())
        if not match:
            raise ValueError(f"Invalid relative time format: {relative_time}")
        
        amount, unit = match.groups()
        amount = int(amount)
        
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        seconds = amount * multipliers[unit]
        
        future_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        return future_time.isoformat()
    
    def _log_job_metric(self, job_id: str, event_type: str, data: Dict = None):
        """Log job metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO job_metrics (job_id, event_type, timestamp, data)
                    VALUES (?, ?, ?, ?)
                """, (job_id, event_type, datetime.now(timezone.utc).isoformat(), 
                     json.dumps(data) if data else None))
                conn.commit()
        except Exception:
            pass  # Don't fail job operations due to metrics logging
    
    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get the next job to process with priority and scheduling support"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()
                
                # First, check for scheduled jobs that are ready to run
                cursor.execute("""
                    UPDATE jobs 
                    SET state = 'pending', updated_at = ?
                    WHERE state = 'scheduled' AND run_at <= ?
                """, (now, now))
                
                # Get next job with priority ordering
                cursor.execute("""
                    SELECT * FROM jobs 
                    WHERE (state = 'pending' OR 
                           (state = 'failed' AND (next_retry_at IS NULL OR next_retry_at <= ?)))
                    ORDER BY priority DESC, created_at ASC 
                    LIMIT 1
                """, (now,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    def update_job_state(self, job_id: str, state: str, **kwargs) -> bool:
        """Update job state and additional fields"""
        with self._lock:
            now = datetime.now(timezone.utc).isoformat()
            
            # Build dynamic update query
            update_fields = ['state = ?', 'updated_at = ?']
            values = [state, now]
            
            for field in ['attempts', 'next_retry_at', 'output', 'error']:
                if field in kwargs:
                    update_fields.append(f'{field} = ?')
                    values.append(kwargs[field])
            
            values.append(job_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE jobs SET {', '.join(update_fields)}
                    WHERE id = ?
                """, values)
                conn.commit()
                return cursor.rowcount > 0
    
    def get_status(self) -> Dict[str, int]:
        """Get count of jobs by state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state, COUNT(*) FROM jobs GROUP BY state")
            
            status = {
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'dead': 0
            }
            
            for state, count in cursor.fetchall():
                status[state] = count
            
            return status
    
    def list_jobs(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List jobs, optionally filtered by state"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if state:
                cursor.execute("""
                    SELECT * FROM jobs WHERE state = ? 
                    ORDER BY created_at DESC
                """, (state,))
            else:
                cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def retry_from_dlq(self, job_id: str) -> bool:
        """Move a job from DLQ back to pending state"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if job exists in DLQ
                cursor.execute("SELECT id FROM jobs WHERE id = ? AND state = 'dead'", (job_id,))
                if not cursor.fetchone():
                    raise ValueError(f"Job {job_id} not found in Dead Letter Queue")
                
                # Reset job to pending state
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    UPDATE jobs 
                    SET state = 'pending', attempts = 0, next_retry_at = NULL, 
                        updated_at = ?, error = NULL
                    WHERE id = ?
                """, (now, job_id))
                
                conn.commit()
                return cursor.rowcount > 0
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job from the queue"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    def get_job_metrics(self, job_id: str) -> List[Dict[str, Any]]:
        """Get metrics for a specific job"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM job_metrics 
                WHERE job_id = ? 
                ORDER BY timestamp ASC
            """, (job_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get system metrics for the last N hours"""
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Job counts by state
            cursor.execute("""
                SELECT state, COUNT(*) as count 
                FROM jobs 
                WHERE created_at >= ?
                GROUP BY state
            """, (since,))
            job_counts = dict(cursor.fetchall())
            
            # Average execution time
            cursor.execute("""
                SELECT AVG(execution_time_ms) as avg_execution_time
                FROM jobs 
                WHERE state = 'completed' AND created_at >= ?
            """, (since,))
            avg_execution = cursor.fetchone()[0] or 0
            
            # Jobs per hour
            cursor.execute("""
                SELECT COUNT(*) as total_jobs
                FROM jobs 
                WHERE created_at >= ?
            """, (since,))
            total_jobs = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN state = 'completed' THEN 1 ELSE 0 END) as completed,
                    COUNT(*) as total
                FROM jobs 
                WHERE created_at >= ? AND state IN ('completed', 'dead')
            """, (since,))
            result = cursor.fetchone()
            success_rate = (result[0] / result[1] * 100) if result[1] > 0 else 0
            
            return {
                'job_counts': job_counts,
                'avg_execution_time_ms': avg_execution,
                'jobs_per_hour': total_jobs / hours,
                'success_rate_percent': success_rate,
                'period_hours': hours
            }
    
    def log_system_metric(self, metric_name: str, value: float):
        """Log a system metric"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO system_metrics (metric_name, metric_value, timestamp)
                    VALUES (?, ?, ?)
                """, (metric_name, value, datetime.now(timezone.utc).isoformat()))
                conn.commit()
        except Exception:
            pass  # Don't fail operations due to metrics logging