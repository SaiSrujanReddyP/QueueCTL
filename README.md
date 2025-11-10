# QueueCTL

A CLI-based background job queue system built with Python and SQLite.

## Features

- Job queue management with SQLite persistence
- Multi-process worker system with configurable concurrency
- Priority queues and Dead Letter Queue handling
- Interactive CLI shell with tab completion
- Web dashboard for monitoring
- Retry mechanism with exponential backoff

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip package manager

### Installation
1. Clone the repository: `git clone <repo-url> && cd QueueCTL`
2. Install dependencies: `pip install -r requirements.txt`
3. Start QueueCTL: `python queuectl.py`

### Quick Start
```bash
python queuectl.py                    # Start interactive shell
queuectl> enqueue {"id":"test","command":"echo Hello"}
queuectl> worker start --count 2
queuectl> status
```

## Demo Video
https://drive.google.com/file/d/1ADiWSIyh_IEannJjz2NxBl5BUZTlc_cj/view?usp=sharing

## Project Structure
```
QueueCTL/
├── queuectl.py              # Main CLI entry point
├── test_runner.py           # Test suite runner
├── src/
│   ├── job_queue.py         # Core job queue logic
│   ├── worker.py            # Worker process implementation
│   ├── worker_manager.py    # Worker lifecycle management
│   ├── interactive_shell.py # Enhanced CLI shell
│   ├── web_dashboard.py     # Web monitoring interface
│   ├── config.py            # Configuration management
│   └── banner.py            # ASCII art banner and startup screen
├── tests/                   # Comprehensive test suite
│   ├── test_bonus_features.py # Advanced features testing
│   ├── test_config.py       # Configuration management tests
│   ├── test_dashboard.py    # Web dashboard tests
│   ├── test_deliverables.py # Core functionality tests
│   ├── test_dlq.py          # Dead Letter Queue tests
│   ├── test_enqueue.py      # Job enqueuing tests
│   ├── test_list.py         # Job listing tests
│   ├── test_metrics.py      # Performance metrics tests
│   ├── test_status.py       # System status tests
│   └── test_worker.py       # Worker management tests
└── jobs.db                  # SQLite database (auto-created)
```


## Architecture Overview

### Job Lifecycle
```
Enqueue → [SQLite Storage] → Schedule Check → Pending Queue → Worker → Execute → Complete/Fail
```

### Data Persistence
- **SQLite Database**: Primary storage for jobs, configuration, and metrics
- **File System**: Worker logs and lock files for coordination
- **In-Memory**: Active job processing state

### Worker Logic
- Multi-process worker pool with configurable concurrency
- Job locking prevents duplicate processing
- Graceful shutdown with SIGTERM handling
- Automatic retry with exponential backoff
- Dead letter queue for permanently failed jobs

## Usage Examples

### Basic Job Management
```bash
# Add jobs
python queuectl.py enqueue '{"id":"hello","command":"echo Hello World"}'
python queuectl.py enqueue '{"id":"ping","command":"ping google.com","priority":10}'

# List jobs
python queuectl.py list
python queuectl.py list --state pending

# Start workers
python queuectl.py worker start --count 3


### Interactive Shell Commands
```bash
python queuectl.py                    # Start interactive mode

# Core Job Management
queuectl> enqueue {"id":"job1","command":"echo Hello"}  # Add job to queue
queuectl> list                        # List all jobs
queuectl> list --state pending        # Filter jobs by state
queuectl> status                      # Show system status with job counts
queuectl> dlq list                    # View Dead Letter Queue jobs

# Worker Management
queuectl> worker start --count 2      # Start worker processes
queuectl> worker stop                 # Stop all workers
queuectl> worker status               # Check worker status

# System Configuration & Monitoring
queuectl> config list                 # Show all configuration settings
queuectl> config get <key>            # Get specific config value
queuectl> config set <key> <value>    # Set configuration value
queuectl> metrics                     # Show performance metrics
queuectl> time                        # Display current time

# Web Dashboard
queuectl> dashboard                   # Launch web monitoring interface
queuectl> dashboard_stop              # Stop web dashboard

# Testing & Demo
queuectl> demo                        # Add demonstration jobs
queuectl> test                        # Show available test options
queuectl> test_deliverables           # Test core functionality
queuectl> test_bonus_features         # Test advanced features
queuectl> verify_all                  # Complete system verification

# Utility Commands
queuectl> banner                      # Show QueueCTL ASCII banner
queuectl> clear                       # Clear screen and show banner
queuectl> help                        # Show all available commands
queuectl> help <command>              # Get help for specific command
queuectl> exit                        # Exit interactive shell
```

### Detailed Command Usage

#### List Commands - Job Filtering & Display
The `list` command provides comprehensive job viewing with multiple filtering options:

```bash
# Basic listing
queuectl> list                        # Show all jobs across all states
queuectl> list --state pending        # Show only pending jobs
queuectl> list --state processing     # Show currently executing jobs
queuectl> list --state completed      # Show successfully completed jobs
queuectl> list --state failed         # Show jobs that failed but will retry
queuectl> list --state dead           # Show permanently failed jobs

# State-specific information
queuectl> list --state pending
┌─────────────────────┬────┬─────────────────────────────────────┬───┬──────────┐
│ ID                  │ St │ Command                             │ T │ Created  │
├─────────────────────┼────┼─────────────────────────────────────┼───┼──────────┤
│ backup_job_123      │ P  │ backup database --full --compress   │0/3│ 11-10    │
│ report_job_456      │ P  │ generate monthly report             │0/3│ 11-10    │
└─────────────────────┴────┴─────────────────────────────────────┴───┴──────────┘

State Legend: P=Pending, R=Running, C=Completed, F=Failed, D=Dead
Showing pending jobs: Jobs ready for worker processing
```

**Column Explanations:**
- **ID**: Complete job identifier (no truncation)
- **St**: Job state (P/R/C/F/D)
- **Command**: Full command with multi-line support for long commands
- **T**: Retry attempts (current/max, e.g., "2/3")
- **Created**: Creation date in MM-DD format

#### Dead Letter Queue (DLQ) Management
The DLQ handles permanently failed jobs that have exceeded maximum retry attempts:

```bash
# View failed jobs
queuectl> dlq list
┌─────────────────────┬─────────────────────────────────────┬───┬──────────┬─────────────────┐
│ ID                  │ Command                             │ T │ Failed   │ Error           │
├─────────────────────┼─────────────────────────────────────┼───┼──────────┼─────────────────┤
│ broken_cmd_789      │ nonexistent_command --invalid       │3/3│ 11-10    │ Command not     │
│                     │                                     │   │ 14:30    │ found           │
└─────────────────────┴─────────────────────────────────────┴───┴──────────┴─────────────────┘

# Retry specific failed job
queuectl> dlq retry broken_cmd_789
Job 'broken_cmd_789' moved from DLQ back to pending queue
Retry attempts reset to 0/3

# Retry all DLQ jobs (use with caution)
queuectl> dlq retry --all
Moving 5 jobs from DLQ back to pending queue...
All DLQ jobs have been reset and queued for retry
```

**DLQ Features:**
- **Automatic Movement**: Jobs moved to DLQ after exceeding `max-retries`
- **Error Preservation**: Complete error messages and failure history stored
- **Manual Recovery**: Individual or bulk retry operations
- **Failure Analysis**: Detailed logs help identify recurring issues

#### Worker Management & Behavior
Workers provide intelligent job processing with user interaction for scheduling decisions:

```bash
# Start workers with detailed output
queuectl> worker start --count 2
Starting 2 worker processes...
✓ Started worker worker_1731234567_0 (PID: 12345)
✓ Started worker worker_1731234567_1 (PID: 12346)

Workers processing jobs...
[Worker 0] Processing job: backup_job_123
[Worker 1] Processing job: report_job_456

# After completing all pending jobs
┌─────────────┬───────┐
│ Status      │ Count │
├─────────────┼───────┤
│ Pending     │   0   │
│ Processing  │   0   │
│ Completed   │  25   │
│ Failed      │   2   │
│ Dead        │   0   │
└─────────────┴───────┘

Workers are now monitoring for new jobs...

# If scheduled jobs exist with long wait times
⏰ Found 3 scheduled jobs with next execution in 2 hours 15 minutes

Choose an option:
1. Keep workers running until scheduled jobs are ready (recommended for short waits)
2. Stop workers now and restart them when jobs are ready (recommended for long waits)
3. Show scheduled job details

Enter choice (1-3): 2

Workers will stop after completing current jobs.
💡 Tip: Use 'status' command to check when scheduled jobs become pending
💡 Then run 'worker start --count 2' to process them

✓ All workers stopped gracefully
```

**Worker Behavior Details:**
- **Intelligent Scheduling**: Workers detect scheduled jobs and provide user options
- **Wait Time Calculation**: Shows exact time until next scheduled job execution
- **User Choice**: Option to keep workers running or stop them for long waits
- **Resource Management**: Prevents unnecessary resource usage during long waits
- **Status Monitoring**: Clear guidance on when to restart workers

**Worker Status Monitoring:**
```bash
queuectl> worker status
┌─────────────────────────┬───────┬─────────────────┬──────────────┐
│ Worker ID               │ PID   │ Status          │ Current Job  │
├─────────────────────────┼───────┼─────────────────┼──────────────┤
│ worker_1731234567_0     │ 12345 │ Processing      │ backup_123   │
│ worker_1731234567_1     │ 12346 │ Waiting         │ None         │
└─────────────────────────┴───────┴─────────────────┴──────────────┘

Active Workers: 2 | Total Jobs Processed: 47 | Average Processing Time: 2.3s
```

## Dependencies & Technology Stack

QueueCTL is built using carefully selected Python libraries for optimal performance and user experience:

### Core Dependencies
```bash
# requirements.txt
typer==0.7.0    # Modern CLI framework with automatic help generation
rich==13.0.0    # Rich text and beautiful formatting for terminal output
click==8.1.0    # Command line interface creation toolkit (Typer dependency)
```

### Library Usage & Purpose

#### Typer (v0.7.0)
Modern CLI framework for command definitions, argument parsing, and automatic help generation.
#### Rich (v13.0.0)
Terminal formatting library for tables, progress bars, colored output, and enhanced console display.
#### Click (v8.1.0)
Core command-line interface toolkit that provides the foundation for Typer's functionality.


**Python Compatibility**: All dependencies support Python 3.7+ ensuring broad compatibility across different environments and deployment scenarios.

## Assumptions & Trade-offs

### Design Decisions
- **SQLite over Redis**: Chosen for simplicity and zero-dependency deployment
- **Multi-process workers**: Process isolation for fault tolerance over threading
- **File-based locking**: Simple coordination mechanism for job processing
- **Interactive shell**: Enhanced CLI experience with tab completion and history

### Simplifications
- Commands are shell strings (not complex job objects)
- Single SQLite database (no distributed storage)
- Basic retry strategy (exponential backoff only)
- File-based logging (not centralized logging system)

### Trade-offs
- **Simplicity vs Performance**: SQLite chosen over Redis for easier deployment
- **Features vs Complexity**: Rich CLI interface adds complexity but improves usability
- **Reliability vs Speed**: File locking ensures job safety but may impact throughput

## Testing Instructions

### Comprehensive Test Suite
```bash
# Interactive shell test commands
python queuectl.py
queuectl> test                       # Show available test options
queuectl> test test_deliverables     # Test core functionality
queuectl> test test_bonus_features   # Test advanced features
queuectl> test test_all              # Complete system verification
queuectl> test test_worker           # Test worker management
queuectl> test test_enqueue          # Test job enqueuing and scheduling
queuectl> test test_list             # Test job listing and filtering
queuectl> test test_status           # Test system status reporting
queuectl> test test_config           # Test configuration management
queuectl> test test_dlq              # Test Dead Letter Queue functionality
queuectl> test test_metrics          # Test performance metrics
queuectl> test test_dashboard        # Test web dashboard functionality
queuectl> test_deliverables      # Test core functionality
queuectl> test_bonus_features    # Test advanced features
queuectl> verify_all            # Complete verification
```

### Manual Verification
```bash
# Test basic functionality
python queuectl.py
queuectl> demo                   # Run demonstration with sample jobs
queuectl> status                 # Check system status
queuectl> metrics                # View performance data
```

## Contributing

We welcome contributions to QueueCTL! This project is designed to be extensible and maintainable, making it easy for developers to add new features and improvements.

### How to Contribute

1. **Fork the Repository**
   ```bash
   git fork https://github.com/SaiSrujanReddyP/QueueCTL.git
   cd QueueCTL
   ```

2. **Set Up Development Environment**
   ```bash
   pip install -r requirements.txt
   python queuectl.py  # Test the installation
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**
   - Follow the existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

5. **Test Your Changes**
   ```bash
   # Run the comprehensive test suite
   python queuectl.py
   queuectl> test_deliverables
   queuectl> test_bonus_features
   queuectl> verify_all
   ```

6. **Submit a Pull Request**
   - Provide a clear description of your changes
   - Include any relevant issue numbers
   - Ensure all tests pass

### Future Scope

**Core Features:**
- **Enhanced Job Types**: Support for different execution environments (Docker, virtual environments)
- **Advanced Scheduling**: Cron expression support, job dependencies
- **Improved Retry Logic**: Custom retry strategies, circuit breakers
- **Performance Optimization**: Database indexing, query optimization

**Monitoring & Observability:**
- **Enhanced Metrics**: More detailed performance statistics
- **Alerting System**: Email/webhook notifications for failures
- **Log Management**: Structured logging, log rotation
- **External Monitoring**: Prometheus/Grafana integration

**User Experience:**
- **Configuration Management**: YAML/TOML config file support
- **Interactive Improvements**: Better error messages, command suggestions
- **Documentation**: More examples, tutorials, best practices
- **Platform Support**: Windows service, systemd integration

**Scalability & Distribution:**
- **Database Options**: PostgreSQL, MySQL support
- **Message Queues**: Redis, RabbitMQ integration
- **Container Support**: Docker images, Kubernetes manifests
- **Load Balancing**: Distributed worker coordination

## License

QueueCTL is released under the MIT License. This means you are free to use, modify, and distribute this software for any purpose, including commercial use.

### MIT License

```
MIT License

Copyright (c) 2024 QueueCTL Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Third-Party Licenses

QueueCTL depends on the following open-source libraries:
- **Typer (0.7.0)**: MIT License
- **Rich (13.0.0)**: MIT License  
- **Click (8.1.0)**: BSD-3-Clause License

All dependencies are compatible with the MIT License and can be used freely in both open-source and commercial projects.

---

**QueueCTL** - A modern, reliable job queue system for Python developers.

