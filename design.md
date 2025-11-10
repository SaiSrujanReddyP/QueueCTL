# QueueCTL Design Document

## Overview

QueueCTL is a CLI-based background job queue system built with Python and SQLite. It provides reliable job processing with priority handling and monitoring capabilities through a modular architecture.

## Architecture Overview

### Job Lifecycle
Jobs flow through a simple, reliable pipeline:
```
1. Enqueue → 2. SQLite Storage → 3. Pending Queue → 4. Worker Pickup → 5. Execute → 6. Complete/Fail
```

**Detailed Flow:**
1. **Job Creation**: User adds job via CLI with command, priority, and metadata
2. **Storage**: Job stored in SQLite database with `pending` state
3. **Queue Management**: Jobs ordered by priority (higher numbers first)
4. **Worker Assignment**: Available worker picks up highest priority job
5. **Execution**: Command runs in isolated subprocess with timeout
6. **Completion**: Job marked as `completed`, `failed`, or `dead` based on result

### Data Persistence
**SQLite Database (`jobs.db`):**
- **Jobs Table**: Core job data (id, command, state, priority, timestamps)
- **Metrics Table**: Execution history and performance data
- **Config Table**: System settings and user preferences
- **ACID Compliance**: Reliable transactions prevent data corruption

**File System:**
- **Lock Files**: Prevent duplicate job processing (`locks/` directory)
- **Logs**: Worker execution output and system logs
- **Database**: Single file storage for easy backup and deployment

### Worker Logic
**Multi-Process Architecture:**
- Each worker runs as separate process for fault isolation
- Workers poll database every second for new jobs
- File-based locking prevents multiple workers processing same job
- Graceful shutdown waits for job completion before terminating

**Job Processing:**
1. **Poll**: Check database for highest priority pending job
2. **Lock**: Create lock file to claim job exclusively
3. **Execute**: Run command in subprocess with configurable timeout
4. **Monitor**: Capture stdout/stderr and track execution time
5. **Update**: Mark job as completed/failed and store results
6. **Retry**: Failed jobs retried with exponential backoff
7. **DLQ**: Jobs exceeding max retries moved to Dead Letter Queue

## Core Components

### 1. Job Queue (`src/job_queue.py`)
- SQLite-based job storage and state management
- Priority queue with atomic operations
- Job states: pending → processing → completed/failed/dead

### 2. Worker System (`src/worker.py`, `src/worker_manager.py`)
- Multi-process worker pool with configurable concurrency
- File-based locking prevents duplicate processing
- Graceful shutdown and error handling

### 3. Interactive Shell (`src/interactive_shell.py`)
- Enhanced CLI with tab completion and command history
- Rich formatting and integrated testing capabilities

### 4. Web Dashboard (`src/web_dashboard.py`)
- Flask-based monitoring interface with real-time metrics
- REST API endpoints for external integration

### 5. Banner System (`src/banner.py`)
- ASCII art banner and startup screen for enhanced UX

## Job States & Flow

### Job States
- **pending**: Ready for worker processing
- **processing**: Currently executing
- **completed**: Finished successfully  
- **failed**: Failed but will retry
- **dead**: Permanently failed (Dead Letter Queue)

### Retry Logic
- **Exponential Backoff**: Delay = backoff_base ^ attempt_number
- **Configurable Limits**: Max retries (default: 3), backoff base (default: 2)
- **Dead Letter Queue**: Failed jobs preserved for manual recovery

## Configuration & Error Handling

### Configuration Management
- **Storage**: Persistent settings in SQLite config table
- **Key Settings**: `max-retries` (3), `backoff-base` (2), worker timeouts
- **Runtime Updates**: Changes applied immediately without restart

### Error Handling & Recovery
- **Process Isolation**: Worker crashes don't affect other workers
- **Graceful Shutdown**: SIGTERM handling with job completion
- **Job Recovery**: Processing jobs returned to pending on worker crash
- **Database Integrity**: ACID transactions prevent corruption

## Design Decisions & Trade-offs

### Key Decisions
- **SQLite over Redis**: Chosen for zero-dependency deployment and ACID compliance
- **Process-based Workers**: Fault isolation over memory efficiency
- **File-based Locking**: Simple coordination without external dependencies
- **Manual Worker Control**: Explicit resource management over automatic scaling

### Simplifications
- Single SQLite database file for all persistent data
- Fixed exponential backoff retry strategy
- Shell command execution only (no Python function support)
- Local file system dependencies for locks and logs

### Suitable For
- Development and testing environments
- Small to medium production workloads (< 10,000 jobs/day)
- Batch processing tasks
- CI/CD pipeline automation

### Limitations
- Not suitable for high-throughput or distributed deployments
- Limited concurrent database access
- No built-in authentication or advanced security features
- Local file system required for coordination