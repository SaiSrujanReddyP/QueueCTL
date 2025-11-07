# QueueCTL Architecture Design Document

## Overview

QueueCTL is a production-grade CLI-based job queue system built with Python that provides persistent job storage, multiple worker support, retry mechanisms, and comprehensive monitoring capabilities. The system follows a modular architecture with clear separation of concerns, designed for reliability, scalability, and ease of use.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        QueueCTL System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  CLI Interface  │    │ Interactive     │    │   Web        │ │
│  │                 │    │ Shell           │    │ Dashboard    │ │
│  │ • Commands      │    │ • Tab Complete  │    │ • Real-time  │ │
│  │ • Help System   │    │ • History       │    │ • Monitoring │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           └───────────────────────┼───────────────────────┘     │
│                                   │                             │
│  ┌─────────────────────────────────┼─────────────────────────────┐ │
│  │              Core Job Queue System                          │ │
│  │                                 │                           │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌──────────┐ │ │
│  │  │ Job Manager     │    │ Scheduler       │    │ Worker   │ │ │
│  │  │                 │    │ Daemon          │    │ Manager  │ │ │
│  │  │ • Add Jobs      │    │                 │    │          │ │ │
│  │  │ • List Jobs     │    │ • Monitor       │    │ • Start  │ │ │
│  │  │ • Update Status │    │ • Convert       │    │ • Stop   │ │ │
│  │  │ • Priority      │    │   Scheduled     │    │ • Status │ │ │
│  │  │   Handling      │    │   → Pending     │    │ • Scale  │ │ │
│  │  └─────────────────┘    │ • Manual/Auto   │    └──────────┘ │ │
│  │           │              │   Mode          │         │      │ │
│  │           │              └─────────────────┘         │      │ │
│  │           │                       │                  │      │ │
│  │  ┌─────────────────────────────────┼──────────────────┼──────┐ │ │
│  │  │                    Database Layer                       │ │ │
│  │  │                                 │                  │    │ │ │
│  │  │  ┌─────────────┐    ┌─────────────────┐    ┌──────────┐ │ │ │
│  │  │  │   Jobs      │    │   Job History   │    │  Config  │ │ │ │
│  │  │  │   Table     │    │   & Logs        │    │ Settings │ │ │ │
│  │  │  │             │    │                 │    │          │ │ │ │
│  │  │  │ • ID        │    │ • Execution     │    │ • Retry  │ │ │ │
│  │  │  │ • Command   │    │   History       │    │   Policy │ │ │ │
│  │  │  │ • State     │    │ • Output Logs   │    │ • Timeout│ │ │ │
│  │  │  │ • Priority  │    │ • Error Logs    │    │ • Workers│ │ │ │
│  │  │  │ • Scheduled │    │ • Metrics       │    │          │ │ │ │
│  │  │  └─────────────┘    └─────────────────┘    └──────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Worker Processes                         │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker N │    │ │
│  │  │          │  │          │  │          │  │          │    │ │
│  │  │ • Fetch  │  │ • Fetch  │  │ • Fetch  │  │ • Fetch  │    │ │
│  │  │ • Execute│  │ • Execute│  │ • Execute│  │ • Execute│    │ │
│  │  │ • Report │  │ • Report │  │ • Report │  │ • Report │    │ │
│  │  │ • Retry  │  │ • Retry  │  │ • Retry  │  │ • Retry  │    │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Job Lifecycle

### State Transition Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  scheduled  │───▶│   pending   │───▶│ processing  │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                   │
        │                  │                   ▼
        │                  │           ┌─────────────┐
        │                  │           │  completed  │
        │                  │           └─────────────┘
        │                  │                   │
        │                  │                   ▼
        │                  │           ┌─────────────┐
        │                  │      ┌───▶│   failed    │
        │                  │      │    └─────────────┘
        │                  │      │            │
        │                  │      │            ▼
        │                  │      │    ┌─────────────┐
        │                  └──────┼───▶│    dead     │
        │                         │    └─────────────┘
        │                         │            ▲
        │                         └────────────┘
        │
        └─────────────────────────────────────────────▶ (timeout/cancel)
```

### State Descriptions

1. **scheduled**: Job waiting for its scheduled execution time (`run_at` timestamp)
2. **pending**: Job ready to be processed by available workers (priority queue)
3. **processing**: Job currently being executed by a worker process
4. **completed**: Job finished successfully with exit code 0
5. **failed**: Job failed but will be retried (attempts < max_retries)
6. **dead**: Job failed permanently and moved to Dead Letter Queue

### Job Processing Flow

1. **Job Creation**
   - User submits job via CLI or interactive shell
   - Job assigned unique ID and stored in database
   - Initial state: `scheduled` (if `run_at` specified) or `pending`

2. **Scheduling**
   - Scheduler daemon monitors scheduled jobs every 5 seconds
   - When `run_at` time arrives, job state changes to `pending`
   - Jobs ordered by priority (higher numbers processed first)

3. **Worker Assignment**
   - Available worker fetches highest priority pending job
   - Job state changes to `processing`
   - Worker ID recorded for tracking

4. **Execution**
   - Worker executes job command in subprocess
   - stdout/stderr captured and stored
   - Execution time measured and recorded

5. **Completion Handling**
   - Success (exit code 0): Job marked as `completed`
   - Failure (non-zero exit): Job marked as `failed`, retry scheduled
   - Timeout: Job terminated and marked as `failed`

6. **Retry Logic**
   - Failed jobs retried with exponential backoff
   - Retry delay: `backoff_base ^ attempt_number` seconds
   - After max retries exceeded: Job moved to Dead Letter Queue (`dead` state)

## Data Persistence

### Database Schema

QueueCTL uses SQLite for persistent storage with ACID compliance:

#### Jobs Table
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,              -- Unique job identifier
    command TEXT NOT NULL,            -- Shell command to execute
    state TEXT DEFAULT 'pending',     -- Current job state
    attempts INTEGER DEFAULT 0,       -- Number of execution attempts
    max_retries INTEGER DEFAULT 3,    -- Maximum retry attempts
    priority INTEGER DEFAULT 0,       -- Job priority (higher = first)
    timeout_seconds INTEGER DEFAULT 300, -- Job timeout in seconds
    run_at TEXT,                      -- Scheduled execution time (ISO format)
    created_at TEXT NOT NULL,         -- Job creation timestamp
    updated_at TEXT NOT NULL,         -- Last update timestamp
    started_at TEXT,                  -- Execution start time
    completed_at TEXT,                -- Execution completion time
    next_retry_at TEXT,               -- Next retry timestamp
    output TEXT,                      -- Job stdout output
    error TEXT,                       -- Job stderr output
    execution_time_ms INTEGER DEFAULT 0, -- Execution duration
    worker_id TEXT                    -- Worker that processed the job
);
```

#### Job Metrics Table
```sql
CREATE TABLE job_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    event_type TEXT NOT NULL,         -- 'started', 'completed', 'failed'
    timestamp TEXT NOT NULL,
    execution_time_ms INTEGER,
    exit_code INTEGER,
    worker_id TEXT
);
```

#### Configuration Table
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Data Access Patterns

- **Thread-safe operations**: All database operations use connection-level locking
- **Connection pooling**: SQLite connections created per operation for simplicity
- **Transaction management**: Critical operations wrapped in transactions
- **Index optimization**: Primary keys and state columns indexed for performance

## Worker Logic

### Worker Architecture

Workers are implemented as separate processes for fault isolation:

```
┌─────────────────────────────────────────────────────────────┐
│                    Worker Process                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Job Fetcher   │    │  Job Executor   │                │
│  │                 │    │                 │                │
│  │ • Poll Database │    │ • Run Command   │                │
│  │ • Priority Sort │    │ • Capture I/O   │                │
│  │ • Lock Job      │    │ • Handle Timeout│                │
│  │ • Update State  │    │ • Record Metrics│                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           ▼                       ▼                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Retry Handler  │    │ Result Reporter │                │
│  │                 │    │                 │                │
│  │ • Backoff Calc  │    │ • Update State  │                │
│  │ • Schedule Retry│    │ • Store Output  │                │
│  │ • DLQ Movement  │    │ • Log Metrics   │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Worker Process Flow

1. **Initialization**
   - Worker process starts with unique ID
   - Database connection established
   - Lock directory created for job coordination

2. **Job Polling Loop**
   ```python
   while running:
       job = fetch_next_job()  # Priority-based selection
       if job:
           process_job(job)
       else:
           sleep(1)  # Poll interval
   ```

3. **Job Processing**
   - Acquire job lock (prevents duplicate processing)
   - Update job state to `processing`
   - Execute command in subprocess with timeout
   - Capture stdout/stderr streams
   - Record execution metrics

4. **Result Handling**
   - Success: Mark job as `completed`
   - Failure: Calculate retry delay, schedule next attempt
   - Timeout: Terminate subprocess, mark as failed
   - Max retries exceeded: Move to Dead Letter Queue

5. **Graceful Shutdown**
   - Handle SIGINT/SIGTERM signals
   - Complete current job before stopping
   - Release job locks and clean up resources

### Concurrency and Locking

- **File-based locking**: Prevents multiple workers from processing same job
- **Process isolation**: Worker failures don't affect other workers
- **Database locking**: SQLite handles concurrent access automatically
- **Atomic operations**: Job state updates are atomic transactions

## Components and Interfaces

### Core Components

#### 1. JobQueue (`src/job_queue.py`)
**Responsibilities:**
- Job CRUD operations (Create, Read, Update, Delete)
- State management and transitions
- Priority queue implementation
- Database schema management
- Metrics collection and storage

**Key Methods:**
```python
def add_job(job_data: Dict) -> str
def get_job(job_id: str) -> Optional[Dict]
def list_jobs(state: str = None, limit: int = None) -> List[Dict]
def update_job_state(job_id: str, state: str, **kwargs) -> bool
def get_next_pending_job() -> Optional[Dict]
def get_metrics(time_range: str = None) -> Dict
```

#### 2. WorkerManager (`src/worker_manager.py`)
**Responsibilities:**
- Worker process lifecycle management
- Process monitoring and health checks
- Graceful shutdown coordination
- Worker scaling operations

**Key Methods:**
```python
def start(count: int) -> None
def stop_all() -> None
def get_status() -> Dict
def scale(new_count: int) -> None
```

#### 3. Worker (`src/worker.py`)
**Responsibilities:**
- Individual job processing
- Command execution and I/O capture
- Retry logic implementation
- Error handling and reporting

**Key Methods:**
```python
def start() -> None
def process_job(job: Dict) -> None
def execute_command(command: str, timeout: int) -> Tuple[int, str, str]
def handle_job_failure(job: Dict, error: str) -> None
```

#### 4. SchedulerDaemon (`src/scheduler_daemon.py`)
**Responsibilities:**
- Scheduled job monitoring
- Automatic job state transitions
- Worker process management (auto mode)
- Background daemon operations

**Key Methods:**
```python
def start(worker_count: int, auto_mode: bool) -> None
def stop() -> None
def check_scheduled_jobs() -> None
def get_status() -> Dict
```

#### 5. Config (`src/config.py`)
**Responsibilities:**
- Configuration management
- Default value handling
- Persistent settings storage
- Runtime configuration updates

**Key Methods:**
```python
def get(key: str) -> Optional[str]
def set(key: str, value: str) -> None
def list_all() -> Dict[str, str]
def get_valid_keys() -> List[str]
```

#### 6. WebDashboard (`src/web_dashboard.py`)
**Responsibilities:**
- Real-time monitoring interface
- REST API endpoints
- Job status visualization
- System metrics display

**Key Endpoints:**
```
GET /                    # Dashboard HTML interface
GET /api/status         # System status JSON
GET /api/jobs           # Job list with filtering
GET /api/metrics        # Performance metrics
```

#### 7. InteractiveShell (`src/interactive_shell.py`)
**Responsibilities:**
- Command-line interface
- Tab completion and history
- Rich formatting and display
- User interaction management

### Interface Contracts

#### Job Data Structure
```python
{
    "id": str,                    # Unique identifier
    "command": str,               # Shell command
    "state": str,                 # Current state
    "priority": int,              # Processing priority
    "timeout_seconds": int,       # Execution timeout
    "run_at": str,               # ISO timestamp (optional)
    "max_retries": int,          # Retry limit
    "attempts": int,             # Current attempt count
    "created_at": str,           # Creation timestamp
    "output": str,               # Execution output
    "error": str,                # Error messages
    "execution_time_ms": int,    # Duration in milliseconds
    "worker_id": str             # Processing worker
}
```

#### Configuration Schema
```python
{
    "max-retries": "3",          # Default retry limit
    "backoff-base": "2",         # Exponential backoff base
    "worker-timeout": "300",     # Default job timeout
    "scheduler-interval": "5"    # Scheduler check interval
}
```

## Error Handling

### Error Categories

1. **System Errors**
   - Database connection failures
   - File system permission issues
   - Process creation failures
   - Network connectivity problems

2. **Job Execution Errors**
   - Command not found
   - Permission denied
   - Timeout exceeded
   - Resource exhaustion

3. **User Input Errors**
   - Invalid JSON format
   - Missing required fields
   - Invalid configuration values
   - Non-existent job IDs

### Error Handling Strategies

#### 1. Graceful Degradation
- System continues operating with reduced functionality
- Non-critical features disabled on component failure
- User notified of limitations with clear messaging

#### 2. Retry Mechanisms
- **Exponential Backoff**: `delay = backoff_base ^ attempt_number`
- **Maximum Attempts**: Configurable retry limit per job
- **Dead Letter Queue**: Failed jobs preserved for manual intervention

#### 3. Logging and Monitoring
- **Structured Logging**: JSON format with timestamps and context
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic cleanup of old log files
- **Metrics Collection**: Error rates and failure patterns tracked

#### 4. User Feedback
- **Rich Error Messages**: Colored output with helpful suggestions
- **Error Codes**: Consistent exit codes for scripting
- **Help Integration**: Context-sensitive help for error recovery

### Recovery Procedures

#### Database Corruption
1. Automatic backup creation before schema changes
2. Database integrity checks on startup
3. Recovery from backup with user confirmation
4. Manual repair procedures documented

#### Worker Process Failures
1. Automatic worker restart on unexpected termination
2. Job state recovery from processing to pending
3. Lock file cleanup for orphaned jobs
4. Health check monitoring with alerts

#### Scheduler Daemon Issues
1. Automatic restart with exponential backoff
2. Scheduled job state preservation
3. Manual intervention procedures
4. Fallback to manual job processing

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- **Component Isolation**: Each module tested independently
- **Mock Dependencies**: External dependencies mocked for reliability
- **Edge Cases**: Boundary conditions and error scenarios
- **Code Coverage**: Minimum 80% coverage requirement

#### 2. Integration Tests
- **End-to-End Workflows**: Complete job lifecycle testing
- **Component Interaction**: Interface contract validation
- **Database Operations**: CRUD operations and transactions
- **Process Communication**: Worker and scheduler coordination

#### 3. Performance Tests
- **Load Testing**: High job volume scenarios
- **Stress Testing**: Resource exhaustion conditions
- **Scalability Testing**: Multiple worker performance
- **Memory Profiling**: Resource usage optimization

#### 4. User Acceptance Tests
- **CLI Interface**: Command functionality and usability
- **Interactive Shell**: Tab completion and help system
- **Web Dashboard**: Real-time monitoring accuracy
- **Error Scenarios**: User-friendly error handling

### Test Implementation

#### Automated Test Suite
```bash
# Core functionality tests
python test_deliverables.py

# Advanced feature tests  
python test_bonus_features.py

# Performance benchmarks
python test_performance.py

# Integration test suite
python test_integration.py
```

#### Manual Testing Scenarios
1. **Basic Job Processing**: Add, process, and complete jobs
2. **Scheduled Jobs**: Time-based job execution
3. **Worker Management**: Start, stop, and scale workers
4. **Error Recovery**: Failed job retry and DLQ handling
5. **Configuration**: Settings management and persistence

#### Continuous Integration
- **Automated Testing**: All tests run on code changes
- **Multiple Environments**: Windows, Linux, macOS testing
- **Performance Regression**: Benchmark comparison
- **Security Scanning**: Dependency vulnerability checks

## Assumptions & Trade-offs

### Design Decisions

#### 1. SQLite Database Choice
**Assumption**: Single-node deployment with moderate job volumes (< 10,000 jobs/day)

**Trade-offs**:
-  **Pros**: Zero configuration, ACID compliance, file-based portability
-  **Cons**: Limited concurrent writes, no distributed scaling
- **Rationale**: Perfect for development, testing, and small-to-medium production workloads

#### 2. Process-based Workers
**Assumption**: Job isolation more important than memory efficiency

**Trade-offs**:
-  **Pros**: Fault isolation, resource limits, crash recovery
-  **Cons**: Higher memory usage, process creation overhead
- **Rationale**: Failed jobs don't crash other workers; better resource isolation

#### 3. Manual Worker Control (Default)
**Assumption**: Users want explicit control over resource usage

**Trade-offs**:
-  **Pros**: Predictable resource usage, explicit scaling decisions
-  **Cons**: Requires manual intervention, no automatic scaling
- **Rationale**: Prevents resource exhaustion and provides predictable behavior

#### 4. File-based Job Locking
**Assumption**: Local file system access is reliable and fast

**Trade-offs**:
-  **Pros**: Simple implementation, cross-platform compatibility
-  **Cons**: NFS issues, cleanup complexity, race conditions
- **Rationale**: Works reliably on local systems without external dependencies

#### 5. Synchronous Job Processing
**Assumption**: Most jobs are short-to-medium duration tasks (seconds to hours)

**Trade-offs**:
-  **Pros**: Simple debugging, clear execution model, easy monitoring
-  **Cons**: No async I/O benefits, blocking operations
- **Rationale**: Easier to debug, monitor, and reason about execution flow

### Simplifications Made

#### 1. Single Database File
- **Simplification**: All data in one SQLite file
- **Benefits**: Easy backup, migration, and deployment
- **Limitations**: Single point of failure, limited concurrent access

#### 2. Fixed Retry Strategy
- **Simplification**: Exponential backoff with configurable base
- **Benefits**: Simple configuration, predictable behavior
- **Limitations**: No custom retry policies, limited flexibility

#### 3. Shell Command Jobs Only
- **Simplification**: Focus on command-line execution
- **Benefits**: Universal compatibility, simple interface
- **Limitations**: No native Python function support, serialization overhead

#### 4. Basic Authentication Model
- **Simplification**: No built-in authentication for web dashboard
- **Benefits**: Zero configuration, immediate usability
- **Limitations**: Assumes trusted network, requires external auth

#### 5. Local File System Dependencies
- **Simplification**: Assumes local file system for locks and logs
- **Benefits**: No external dependencies, works offline
- **Limitations**: Not suitable for distributed deployments

### Performance Characteristics

#### Suitable For:
- **Development Environments**: Local testing and debugging
- **Small Production**: < 10,000 jobs/day, single server
- **Batch Processing**: Periodic data processing tasks
- **CI/CD Pipelines**: Build and deployment automation
- **Scheduled Tasks**: Cron job replacement with better monitoring

#### Not Optimal For:
- **High Throughput**: > 100,000 jobs/day
- **Real-time Processing**: < 100ms latency requirements
- **Distributed Systems**: Multi-server deployments
- **Complex Dependencies**: Job dependency graphs
- **Streaming Data**: Continuous data processing

### Scalability Considerations

#### Vertical Scaling
- **CPU**: More workers can be added up to CPU core count
- **Memory**: Each worker process consumes ~10-50MB RAM
- **Storage**: SQLite handles databases up to 281TB
- **I/O**: Limited by disk I/O for job logging and metrics

#### Horizontal Scaling Limitations
- **Database**: SQLite doesn't support distributed access
- **File Locks**: Local file system required for coordination
- **State Sharing**: No built-in cluster coordination
- **Load Balancing**: No automatic job distribution

#### Migration Path
For larger deployments, consider:
1. **Database Migration**: PostgreSQL or MySQL for concurrent access
2. **Message Queue**: Redis or RabbitMQ for job distribution
3. **Container Orchestration**: Kubernetes for worker scaling
4. **Monitoring**: Prometheus/Grafana for production monitoring

### Security Considerations

#### Current Security Model
- **Local Access**: Assumes trusted local environment
- **File Permissions**: Standard OS file permissions for database
- **Process Isolation**: Workers run as same user as main process
- **Network Security**: Web dashboard has no authentication

#### Security Enhancements for Production
1. **Authentication**: Add user authentication for web interface
2. **Authorization**: Role-based access control for operations
3. **Encryption**: Database encryption at rest
4. **Network Security**: HTTPS for web dashboard
5. **Audit Logging**: Security event logging and monitoring

This design document provides a comprehensive overview of QueueCTL's architecture, covering all major components, data flows, and design decisions. The system is optimized for simplicity, reliability, and ease of use while maintaining production-grade features for job processing and monitoring.