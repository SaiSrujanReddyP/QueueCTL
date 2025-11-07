# QueueCTL - Production-Grade CLI Job Queue System

```
 ██████  ██    ██ ███████ ██    ██ ███████  ██████ ████████ ██      
██    ██ ██    ██ ██      ██    ██ ██      ██         ██    ██      
██    ██ ██    ██ █████   ██    ██ █████   ██         ██    ██      
██ ▄▄ ██ ██    ██ ██      ██    ██ ██      ██         ██    ██      
 ██████   ██████  ███████  ██████  ███████  ██████    ██    ███████ 
   ▀▀                                                              
                                v1.0.0
                CLI-based Background Job Queue System
```

QueueCTL is a robust, production-ready job queue system built with Python. It provides persistent job storage, multiple worker support, retry mechanisms with exponential backoff, Dead Letter Queue functionality, and a comprehensive CLI interface.

## Features

### Core Features
- **Persistent Job Storage** - SQLite database with ACID compliance
- **Multiple Worker Support** - Concurrent job processing with multiprocessing
- **Retry Mechanism** - Exponential backoff with configurable parameters
- **Dead Letter Queue** - Failed job management and recovery
- **Configuration Management** - Persistent settings and customization
- **Clean CLI Interface** - Rich formatting with comprehensive help

### Advanced Features
- **Job Timeout Handling** - Per-job timeout configuration
- **Priority Queues** - Higher priority jobs processed first
- **Scheduled Jobs** - Delayed execution with run_at timestamps
- **Scheduler Daemon** - Automatic scheduled job management
- **Manual Worker Control** - Strict control over worker processes
- **Job Output Logging** - Complete stdout/stderr capture
- **Metrics & Stats** - Performance monitoring and analytics
- **Web Dashboard** - Real-time monitoring interface
- **Interactive Shell** - Tab completion and command history
- **ASCII Art Banner** - Beautiful startup experience

### Recent UI/UX Improvements
- **Full Job ID Display** - Complete job IDs shown without truncation
- **Optimized Table Layout** - Compact "Tries" and "Created" columns for better space usage
- **Enhanced Error Messages** - Colored error styling with helpful suggestions
- **Improved Readability** - Better contrast and visual hierarchy in all outputs

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SaiSrujanReddyP/QueueCTL.git
   cd QueueCTL
   ```

   **Or download ZIP:**
   ```bash
   # Download ZIP from GitHub, extract files, then:
   cd QueueCTL
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start QueueCTL:**
   ```bash
   python queuectl.py
   ```

   This will start an **interactive terminal** where you can use commands directly without the `python queuectl.py` prefix.

4. **Get started:**
   ```bash
   # In the interactive shell, type:
   help
   
   # Try the demo:
   demo
   
   # Check the README for more examples
   ```

## Project Structure

QueueCTL follows a modular architecture with clear separation of concerns:

```
QueueCTL/
├── src/                             # Core application modules
│   ├── __init__.py                  # Package initialization
│   ├── job_queue.py                 # Job queue implementation with SQLite persistence
│   ├── worker_manager.py            # Worker process management and coordination
│   ├── worker.py                    # Individual worker implementation for job processing
│   ├── scheduler_daemon.py          # Background daemon for scheduled job management
│   ├── config.py                    # Configuration management and persistence
│   ├── web_dashboard.py             # Real-time web monitoring interface
│   ├── interactive_shell.py         # Interactive CLI with tab completion
│   └── banner.py                    # ASCII art banner and startup screen
│
├── locks/                           # Job locking directory (auto-created)
│   └── *.lock                       # Worker coordination lock files
│
├── .vscode/                         # VS Code configuration
│   └── settings.json                # Editor settings and preferences
│
├── queuectl.py                      # Main CLI entry point and command interface
├── jobs.db                          # SQLite database (auto-created)
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package installation configuration
├── Makefile                         # Build and development commands
├── design.md                        # Architecture and design documentation
├── README.md                        # This comprehensive guide
├── .gitignore                       # Git ignore patterns
│
├── test_deliverables.py             # Core functionality test suite
├── test_bonus_features.py           # Advanced features test suite
├── submission_checklist.py          # Project validation checklist
├── DELIVERABLES_CHECKLIST.md        # Requirements verification document
│
└── queuectl-easy.bat                # Windows batch file for easy startup
```

### Core Modules Description

#### **src/job_queue.py**
- **Purpose**: Central job management and persistence layer
- **Key Features**: SQLite database operations, job state management, priority queues
- **Responsibilities**: Job CRUD operations, metrics collection, database schema management
- **Database Tables**: `jobs`, `job_metrics`, `system_metrics`

#### **src/worker_manager.py**
- **Purpose**: Worker process lifecycle management
- **Key Features**: Process spawning, health monitoring, graceful shutdown
- **Responsibilities**: Start/stop workers, process coordination, resource cleanup
- **Platform Support**: Windows (subprocess) and Unix (multiprocessing) compatibility

#### **src/worker.py**
- **Purpose**: Individual job processing and execution
- **Key Features**: Command execution, I/O capture, timeout handling, retry logic
- **Responsibilities**: Job fetching, subprocess management, error handling, metrics reporting
- **Isolation**: Each worker runs in separate process for fault tolerance

#### **src/scheduler_daemon.py**
- **Purpose**: Background daemon for scheduled job management
- **Key Features**: Time-based job conversion, automatic worker management (optional)
- **Responsibilities**: Monitor scheduled jobs, convert to pending, daemon lifecycle
- **Operation Modes**: Manual (user controls workers) or Auto (daemon manages workers)

#### **src/config.py**
- **Purpose**: Configuration management and persistence
- **Key Features**: SQLite-backed settings, default values, runtime updates
- **Responsibilities**: Get/set configuration, validation, persistent storage
- **Settings**: `max-retries`, `backoff-base`, timeout values

#### **src/web_dashboard.py**
- **Purpose**: Real-time web monitoring interface
- **Key Features**: HTTP server, REST API, real-time job status, metrics visualization
- **Responsibilities**: Serve dashboard HTML, provide JSON APIs, handle web requests
- **Endpoints**: `/`, `/api/status`, `/api/jobs`, `/api/metrics`

#### **src/interactive_shell.py**
- **Purpose**: Interactive command-line interface
- **Key Features**: Tab completion, command history, rich formatting, help system
- **Responsibilities**: Command parsing, user interaction, output formatting
- **Commands**: All QueueCTL operations available in interactive mode

#### **src/banner.py**
- **Purpose**: Startup experience and branding
- **Key Features**: ASCII art banner, welcome messages, version display
- **Responsibilities**: Visual presentation, startup screen, branding elements

### Main Entry Points

#### **queuectl.py**
- **Purpose**: Main CLI application and command router
- **Key Features**: Typer-based CLI, rich formatting, command organization
- **Responsibilities**: Command parsing, argument validation, component coordination
- **Commands**: `enqueue`, `list`, `status`, `worker`, `dlq`, `config`, `dashboard`, `metrics`

#### **jobs.db**
- **Purpose**: SQLite database for persistent storage
- **Auto-created**: Generated on first run with proper schema
- **Tables**: Jobs, metrics, configuration, system data
- **ACID Compliance**: Reliable data persistence with transaction support

### Testing and Validation

#### **test_deliverables.py**
- **Purpose**: Core functionality validation
- **Coverage**: Job processing, worker management, basic operations
- **Usage**: `python test_deliverables.py`

#### **test_bonus_features.py**
- **Purpose**: Advanced features testing
- **Coverage**: Scheduling, priorities, DLQ, web dashboard, metrics
- **Usage**: `python test_bonus_features.py`

#### **submission_checklist.py**
- **Purpose**: Automated project validation
- **Coverage**: File structure, dependencies, functionality checks
- **Usage**: Validates project completeness and requirements

### Development Files

#### **requirements.txt**
```
typer>=0.9.0          # CLI framework with rich formatting
rich>=13.0.0          # Terminal formatting and tables
```

#### **setup.py**
- **Purpose**: Package installation and distribution
- **Features**: Entry points, dependencies, metadata
- **Usage**: `pip install -e .` for development installation

#### **Makefile**
- **Purpose**: Development automation and build commands
- **Commands**: Testing, linting, packaging, deployment helpers
- **Usage**: `make test`, `make clean`, `make install`

#### **queuectl-easy.bat**
- **Purpose**: Windows convenience launcher
- **Features**: One-click startup for Windows users
- **Usage**: Double-click to start QueueCTL interactive shell

### Runtime Directories

#### **locks/**
- **Purpose**: Worker coordination and job locking
- **Auto-created**: Generated when workers start
- **Contents**: `<job_id>.lock` files for preventing duplicate processing
- **Cleanup**: Automatically cleaned on worker shutdown

#### **.vscode/**
- **Purpose**: VS Code editor configuration
- **Contents**: Python interpreter settings, debugging configuration
- **Optional**: Only needed for development in VS Code

This modular structure ensures clean separation of concerns, making the codebase maintainable, testable, and extensible. Each module has a single responsibility and well-defined interfaces for interaction with other components.

## Quick Start

### 1. Start QueueCTL Interactive Shell
```bash
python queuectl.py
```
This displays the beautiful ASCII banner and starts the interactive shell where you can use commands directly.

### 2. Add Your First Job
```bash
# In the interactive shell:
queuectl> enqueue {"id":"hello","command":"echo Hello World"}
✓ Job added successfully: hello
```

### 3. Start Workers
```bash
queuectl> worker start --count 2
Starting 2 worker processes...
✓ Started worker worker_123_0 (PID: 1234)
✓ Started worker worker_123_1 (PID: 1235)
```

### 4. Check Status
```bash
queuectl> status
# Shows system status with job counts and worker information
```

### 5. View Jobs with Enhanced Display
```bash
queuectl> list
# Shows jobs with state legend and multi-line commands
State Legend: P=Pending, R=Running, C=Completed, F=Failed, D=Dead, S=Scheduled
```

### 6. Get Help
```bash
queuectl> help
# Shows all available commands

queuectl> help enqueue
# Shows specific command help
```

## Usage Examples

### Basic Job Management

**Add a simple job:**
```bash
$ python queuectl.py enqueue '{"id":"hello","command":"echo Hello World"}'
✓ Job added successfully: hello
  Command: echo Hello World
  State: pending
  Priority: 0 (default)
```

**Add a job with priority and scheduling:**
```bash
$ python queuectl.py enqueue '{"id":"ping","command":"ping google.com","priority":10,"run_at":"+5m"}'
✓ Job scheduled successfully: ping
  Command: ping google.com
  Priority: 10
  Scheduled for: 2025-11-10 19:25:00 UTC
```

**Start workers:**
```bash
$ python queuectl.py worker start --count 3
Starting 3 worker processes...
✓ Started worker worker_123_0 (PID: 1234)
✓ Started worker worker_123_1 (PID: 1235)  
✓ Started worker worker_123_2 (PID: 1236)
Press Ctrl+C to stop workers gracefully

Workers processing jobs...
[Worker 1] Processing job: hello
[Worker 2] Processing job: ping
```

## Architecture Overview

QueueCTL follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        QueueCTL Architecture                    │
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
│  │           │             │   Mode          │         │       │ │
│  │           │             └─────────────────┘         │       │ │
│  │           │                       │                 │       │ │
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
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### **1. CLI Interface & Interactive Shell**
- **Command Processing**: Handles all user commands and arguments
- **Interactive Mode**: Provides tab completion, command history, and rich formatting
- **Help System**: Comprehensive help and usage information

#### **2. Scheduler Daemon**
- **Scheduled Job Management**: Monitors and converts scheduled jobs to pending
- **Two Operation Modes**:
  - **Manual Mode** (Default): Only converts scheduled → pending, user controls workers
  - **Auto Mode** (Optional): Also automatically manages worker processes
- **Background Operation**: Runs as a daemon process, checking every 5 seconds
- **Logging**: Comprehensive activity logging to `scheduler_daemon.log`

#### **3. Job Manager**
- **Job Lifecycle**: Manages jobs from creation to completion
- **State Management**: pending → processing → completed/failed/dead
- **Priority Handling**: Higher priority jobs processed first
- **Dead Letter Queue**: Failed jobs moved to DLQ for manual intervention

#### **4. Worker Manager**
- **Process Management**: Start, stop, and monitor worker processes
- **Concurrency**: Multiple workers process jobs in parallel
- **Graceful Shutdown**: Workers finish current jobs before stopping
- **Locking**: Prevents duplicate job processing

#### **5. Database Layer**
- **Persistent Storage**: SQLite database with ACID compliance
- **Job Storage**: Complete job information and metadata
- **History Tracking**: Execution history and performance metrics
- **Configuration**: System settings and user preferences

## Scheduler Daemon

The scheduler daemon is a key component that provides automatic scheduled job management:

### Features
- **Automatic Conversion**: Scheduled jobs → Pending jobs when time arrives
- **Two Operation Modes**: Manual worker control (default) or automatic worker management
- **Background Operation**: Runs continuously as a daemon process
- **Comprehensive Logging**: All activities logged with timestamps
- **Configurable Intervals**: Customizable check frequency (default: 5 seconds)

### Usage

**Start scheduler in manual mode (default):**
```bash
# Interactive shell
queuectl> scheduler start --workers 2

# Direct command
python queuectl.py shell -c "scheduler start --workers 2"
```

**Start scheduler in auto mode:**
```bash
queuectl> scheduler start --workers 2 --auto
```

**Check scheduler status:**
```bash
queuectl> scheduler status
```

**View scheduler logs:**
```bash
queuectl> scheduler logs
```

**Stop scheduler:**
```bash
queuectl> scheduler stop
```

### Manual vs Auto Mode

#### **Manual Mode (Default - Recommended)**
```bash
queuectl> scheduler start --workers 2

# What happens:
# ✅ Scheduled jobs → Pending (automatic)
# 🎮 Worker management (manual control)

# Your workflow:
queuectl> demo                    # Add jobs
queuectl> worker start --count 2  # Start workers manually
queuectl> worker stop             # Stop workers manually
```

#### **Auto Mode (Optional)**
```bash
queuectl> scheduler start --workers 2 --auto

# What happens:
# ✅ Scheduled jobs → Pending (automatic)
# 🤖 Worker management (automatic)

# Your workflow:
queuectl> demo                    # Add jobs
# Workers start/stop automatically
```

## Worker Management

QueueCTL provides comprehensive worker management with strict manual control:

### Manual Worker Control

**Start workers:**
```bash
queuectl> worker start --count 3
```

**Stop workers:**
```bash
queuectl> worker stop
```

**Check worker status:**
```bash
queuectl> worker status
```

### Worker Features
- **Parallel Processing**: Multiple workers process jobs concurrently
- **Job Locking**: Prevents duplicate processing of the same job
- **Graceful Shutdown**: Workers finish current jobs before stopping
- **Process Isolation**: Each worker runs in a separate process
- **Automatic Retry**: Failed jobs are retried with exponential backoff
- **Timeout Handling**: Jobs that exceed timeout are terminated

## Scheduled Jobs

QueueCTL supports delayed job execution with flexible scheduling:

### Adding Scheduled Jobs

**Using relative time:**
```bash
queuectl> enqueue {"id":"backup_job","command":"backup database","run_at":"+1h"}
queuectl> enqueue {"id":"report_job","command":"send report","run_at":"+30m"}
queuectl> enqueue {"id":"cleanup_job","command":"cleanup logs","run_at":"+1d"}
```
### Viewing Scheduled Jobs

**List all scheduled jobs:**
```bash
queuectl> list --state scheduled
```

### How Scheduled Jobs Work

1. **Creation**: Jobs are created with `scheduled` state and `run_at` timestamp
2. **Monitoring**: Scheduler daemon checks every 5 seconds for due jobs
3. **Conversion**: When time arrives, jobs automatically become `pending`
4. **Processing**: Pending jobs are processed by active workers
5. **Completion**: Jobs move to `completed`, `failed`, or `dead` states
## Interactive Shell Commands

QueueCTL provides a rich interactive shell with tab completion and command history. When you run `python queuectl.py`, you enter this interactive mode where you can use commands directly.

### Current Available Commands

**Core Job Management:**
```bash
enqueue <json>          # Add job to queue with scheduling/priority
list [--state <state>]  # List jobs with full IDs and multi-line commands  
status                  # Show system status with job counts
dlq list                # List Dead Letter Queue jobs
dlq retry <job_id>      # Retry failed job from DLQ
```

**Worker & Scheduler Management:**
```bash
worker start --count N  # Start N worker processes
worker stop             # Stop all workers
scheduler start         # Start scheduler daemon (manual mode)
scheduler stop          # Stop scheduler daemon
stop_workers           # Stop all workers with final status
```

**System Information & Configuration:**
```bash
config list             # Show all configuration settings
config get <key>        # Get configuration value
config set <key> <value># Set configuration value
metrics                 # Show performance metrics and statistics
time                   # Show current time (local/UTC)
```

**Web Dashboard:**
```bash
dashboard              # Start web monitoring dashboard
dashboard_stop         # Stop web dashboard
```

**Testing & Demo:**
```bash
demo                   # Add demo jobs for testing
test_deliverables      # Test core functionality
test_bonus_features    # Test advanced features  
verify_all             # Complete system verification
```

**Utility Commands:**
```bash
help [<command>]       # Show help for commands
clear                  # Clear screen and show banner
banner                 # Show QueueCTL ASCII banner
exit                   # Exit interactive shell
```

**Recent UI Improvements:**
- **State Legend**: Shows what P, R, C, F, D, S mean after each list command
- **Multi-line Commands**: Long commands wrap to next line for full visibility
- **Compact Layout**: Optimized column widths (St=3, T=3, dates=8 chars)
- **Smart Filtering**: State-specific help text for filtered lists

**Example Enhanced Output:**
```bash
queuectl> list --state scheduled

┌─────────────────────┬────┬─────────────────────────────────────┬───┬──────────┐
│ ID                  │ St │ Command                             │ T │ Scheduled│
├─────────────────────┼────┼─────────────────────────────────────┼───┼──────────┤
│ backup_job_123      │ S  │ backup database --full --compress   │0/3│ 11-10    │
│                     │    │ --encrypt --output /backups/daily   │   │ 02:00    │
└─────────────────────┴────┴─────────────────────────────────────┴───┴──────────┘

State Legend: P=Pending, R=Running, C=Completed, F=Failed, D=Dead, S=Scheduled
Showing scheduled jobs: Jobs waiting for their scheduled time
```

### Getting Started in Interactive Shell

1. **Start QueueCTL**: `python queuectl.py`
2. **Get help**: `help` (shows all commands)
3. **Try demo**: `demo` (adds sample jobs)
4. **Start workers**: `worker start --count 2`
5. **Check status**: `status`
6. **List jobs**: `list` (with enhanced display)
7. **Exit**: `exit`

**Pro Tips:**
- Use `help <command>` for specific command help
- All commands have tab completion
- No need for `python queuectl.py` prefix in interactive mode
- Commands show helpful legends and state information

## User Interface Enhancements

QueueCTL features a modern, user-friendly interface with recent improvements:

### Enhanced Table Display

**Full Job ID Visibility:**
```bash
$ queuectl> list --state dead
┌─────────────────────────────────────────────────────────────────────────────┐
│ ID                    │ State │ Command           │ Tries │ Created          │
├───────────────────────┼───────┼───────────────────┼───────┼──────────────────┤
│ demo_fail_1762684661  │ dead  │ nonexistent_comm… │  2/2  │ 11-09 10:37      │
│ demo_fail_1762680721  │ dead  │ nonexistent_comm… │  2/2  │ 11-09 10:32      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Optimized Column Layout:**
- **Full Job IDs**: No more truncation with `…` - complete IDs always visible
- **Compact "Tries"**: Shows `0/3`, `1/2` format in minimal space (6 chars vs 10)
- **Compact "Created"**: Shows `MM-DD HH:MM` format (11 chars vs 18)
- **Smart Spacing**: More room for important information

### Enhanced Error Messages

**Before (hard to read):**
```bash
queuectl> config get backoff
'backoff' is not a valid config key
Valid keys: max-retries, backoff-base
Type 'config list' to see all available keys
```

**After (colored and clear):**
```bash
queuectl> config get backoff
'backoff' is not a valid config key
Valid keys: backoff-base, max-retries
Type 'config list' to see all available keys
```

**Color Coding:**
- **Red**: Error messages and invalid inputs
- **Yellow**: Instructions and helpful text
- **Cyan**: Valid options and key names
- **Green**: Commands to run and success messages

### Interactive Shell Improvements

**Removed deprecated commands:**
- Removed `quick` command (use `enqueue` instead)
- Streamlined command set for better usability

**Enhanced help system:**
- Updated welcome screen with recent improvements
- Better command descriptions reflecting current functionality
- Focus on essential commands and features

## Configuration

QueueCTL supports persistent configuration management:

### View Configuration
```bash
python queuectl.py config list
```

### Update Configuration
```bash
python queuectl.py config set max-retries 5
python queuectl.py config set backoff-base 2
```

### Configuration Options
- `max-retries`: Default maximum retry attempts (default: 3)
- `backoff-base`: Base retry delay in seconds (default: 2)

### Enhanced Error Handling
Configuration commands now provide helpful error messages:
```bash
queuectl> config set invalid-key value
'invalid-key' is not a valid config key
Valid keys: backoff-base, max-retries
Type 'config list' to see all available keys
```

## Job States and Lifecycle

Jobs in QueueCTL follow a well-defined lifecycle:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  scheduled  │───▶│   pending   │───▶│ processing  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           │                   ▼
                           │           ┌─────────────┐
                           │           │  completed  │
                           │           └─────────────┘
                           │                   │
                           │                   ▼
                           │           ┌─────────────┐
                           │      ┌───▶│   failed    │
                           │      │    └─────────────┘
                           │      │            │
                           │      │            ▼
                           │      │    ┌─────────────┐
                           └──────┼───▶│    dead     │
                                  │    └─────────────┘
                                  │            ▲
                                  └────────────┘
```

### State Descriptions
- **scheduled**: Job waiting for its scheduled time
- **pending**: Job ready to be processed by workers
- **processing**: Job currently being executed by a worker
- **completed**: Job finished successfully
- **failed**: Job failed but will be retried
- **dead**: Job failed permanently (moved to Dead Letter Queue)

## Dead Letter Queue (DLQ)

Failed jobs that exceed maximum retry attempts are moved to the Dead Letter Queue:

### View DLQ Jobs
```bash
python queuectl.py dlq list
```

### Retry DLQ Job
```bash
python queuectl.py dlq retry <job_id>
```

### DLQ Features
- **Automatic Movement**: Jobs moved to DLQ after max retries exceeded
- **Manual Recovery**: Individual jobs can be retried from DLQ
- **Failure Analysis**: Complete error logs and retry history preserved
- **Bulk Operations**: Multiple DLQ jobs can be managed together

## Monitoring and Metrics

QueueCTL provides comprehensive monitoring capabilities:

### System Metrics
```bash
python queuectl.py metrics
```

### Web Dashboard
```bash
python queuectl.py dashboard
# Opens web interface at http://localhost:5000
```

### Available Metrics
- **Job Counts**: Total jobs by state (pending, processing, completed, failed, dead)
- **Processing Times**: Average, min, max execution times
- **Success Rates**: Job completion and failure rates
- **Worker Utilization**: Active workers and processing capacity
- **Queue Depth**: Number of jobs waiting to be processed

## Best Practices

### Production Deployment

1. **Use Manual Worker Control**:
   ```bash
   # Recommended for production
   queuectl> scheduler start --workers 4
   queuectl> worker start --count 4
   ```

2. **Monitor System Health**:
   ```bash
   # Regular health checks
   queuectl> status
   queuectl> scheduler status
   queuectl> metrics
   ```

3. **Handle Failed Jobs**:
   ```bash
   # Check and retry failed jobs
   queuectl> dlq list
   queuectl> dlq retry <job_id>
   ```

### Development and Testing

1. **Use Demo Jobs**:
   ```bash
   queuectl> demo
   ```

2. **Auto Mode for Development**:
   ```bash
   queuectl> scheduler start --workers 2 --auto
   ```

3. **Monitor Logs**:
   ```bash
   queuectl> scheduler logs
   ```

### Performance Tuning

1. **Adjust Worker Count**: Based on CPU cores and job characteristics
2. **Configure Timeouts**: Set appropriate timeouts for different job types
3. **Monitor Queue Depth**: Ensure workers can keep up with job creation rate
4. **Optimize Retry Policy**: Balance between reliability and performance

## Assumptions & Trade-offs

### Design Decisions

**1. SQLite Database Choice**
- **Assumption**: Single-node deployment with moderate job volumes
- **Trade-off**: Simplicity and zero-configuration vs. distributed scalability
- **Rationale**: Perfect for development, testing, and small-to-medium production workloads

**2. Manual Worker Control (Default)**
- **Assumption**: Users want explicit control over resource usage
- **Trade-off**: Manual management vs. automatic scaling
- **Rationale**: Prevents resource exhaustion and provides predictable behavior

**3. Process-based Workers**
- **Assumption**: Job isolation is more important than memory efficiency
- **Trade-off**: Process overhead vs. fault isolation
- **Rationale**: Failed jobs don't crash other workers; better resource isolation

**4. Synchronous Job Processing**
- **Assumption**: Most jobs are short-to-medium duration tasks
- **Trade-off**: Simplicity vs. async complexity
- **Rationale**: Easier to debug, monitor, and reason about

**5. File-based Logging**
- **Assumption**: Local file system access is available
- **Trade-off**: Simple logging vs. centralized log management
- **Rationale**: Works out-of-the-box without external dependencies

### Simplifications Made

**1. Single Database File**
- All data stored in one SQLite file for simplicity
- Easy backup and migration
- No complex database setup required

**2. Fixed Retry Strategy**
- Exponential backoff with configurable base delay
- Simple but effective for most use cases
- No complex retry policies or custom strategies

**3. Basic Authentication**
- No built-in authentication for web dashboard
- Assumes trusted network environment
- Can be extended with reverse proxy authentication

**4. Limited Job Types**
- Focus on shell command execution
- No built-in support for Python functions or complex job types
- Extensible through command-line interface

### Performance Characteristics

**Suitable For:**
- Development and testing environments
- Small to medium production workloads (< 10,000 jobs/day)
- Single-server deployments
- Jobs with execution times from seconds to hours

**Not Optimal For:**
- High-throughput systems (> 100,000 jobs/day)
- Distributed deployments across multiple servers
- Real-time processing requirements (< 100ms latency)
- Jobs requiring complex dependency management

### Testing Strategy

The system includes comprehensive testing for reliability:
- Unit tests for core components
- Integration tests for end-to-end workflows
- Bonus feature tests for advanced functionality
- Manual testing scenarios for edge cases

## Testing Instructions

### Automated Testing

**Run the complete test suite:**
```bash
python test_bonus_features.py
```

**Expected output:**
```bash
QueueCTL Bonus Features Test Suite
==================================

✓ Job Scheduling & Priorities
✓ Dead Letter Queue Management  
✓ Configuration Management
✓ Metrics/Execution Stats
✓ Web Dashboard
✓ Interactive Shell
✓ ASCII Art Banner

All tests passed! 🎉
```

### Manual Testing Scenarios

**1. Basic Job Processing:**
```bash
# Start interactive shell
python queuectl.py

# Add test jobs
queuectl> demo

# Start workers
queuectl> worker start --count 2

# Monitor progress
queuectl> status
queuectl> list

# Stop workers
queuectl> worker stop
```

**2. Scheduled Job Testing:**
```bash
# Add scheduled jobs
queuectl> enqueue {"id":"test_30s","command":"echo hello","run_at":"+30s"}

# Start scheduler
queuectl> scheduler start --workers 2

# Monitor scheduled jobs
queuectl> list --state scheduled
queuectl> scheduler status

# Wait and check conversion to pending
queuectl> list --state pending
```

**3. Error Handling Testing:**
```bash
# Test invalid commands
queuectl> config get invalid-key
queuectl> config set invalid-key value

# Test job failures
queuectl> enqueue {"id":"fail_test","command":"nonexistent_command"}
queuectl> worker start --count 1

# Check dead letter queue
queuectl> dlq list
queuectl> dlq retry fail_test
```

**4. UI/UX Testing:**
```bash
# Test full job ID display
queuectl> demo
queuectl> list --state dead

# Test table formatting
queuectl> list
queuectl> status

# Test error message styling
queuectl> config get backoff
```

### Verification Checklist

- [ ] Jobs can be added and processed successfully
- [ ] Workers start, process jobs, and stop gracefully
- [ ] Scheduled jobs are converted to pending at the right time
- [ ] Failed jobs are retried and eventually moved to DLQ
- [ ] Configuration can be viewed and updated
- [ ] Web dashboard displays real-time information
- [ ] Interactive shell provides tab completion and help
- [ ] Error messages are clear and helpful
- [ ] Job IDs are displayed in full without truncation
- [ ] Table layout is optimized and readable

## Troubleshooting

### Common Issues

**Scheduler not starting:**
```bash
# Check if already running
queuectl> scheduler status

# Check logs for errors
queuectl> scheduler logs

# Stop and restart
queuectl> scheduler stop
queuectl> scheduler start --workers 2
```

**Workers not processing jobs:**
```bash
# Check worker status
queuectl> worker status

# Check if jobs are pending
queuectl> list --state pending

# Restart workers
queuectl> worker stop
queuectl> worker start --count 2
```

**Jobs stuck in processing:**
```bash
# Check for timeout issues
queuectl> list --state processing

# Stop and restart workers
queuectl> worker stop
queuectl> worker start --count 2
```

### Log Files
- **Scheduler Logs**: `scheduler_daemon.log`
- **Worker Logs**: Displayed in worker output
- **Job Output**: Stored in database, viewable via dashboard

## API Reference

### Command Line Interface

**Basic Commands:**
```bash
python queuectl.py --help                     # Show help
python queuectl.py --version                  # Show version
python queuectl.py shell                      # Start interactive shell
```

**Job Management:**
```bash
python queuectl.py enqueue '{"id":"job_id","command":"command"}'  # Add job
python queuectl.py list --state pending       # Filter by state
```

**Worker Management:**
```bash
python queuectl.py worker start --count N     # Start N workers
python queuectl.py worker stop                # Stop workers
python queuectl.py worker status              # Worker status
```

**System Commands:**
```bash
python queuectl.py status                     # System status
python queuectl.py metrics                    # Performance metrics
python queuectl.py config list                # Show configuration
```

## Contributing

QueueCTL is designed to be extensible and maintainable. Key areas for contribution:

1. **New Job Types**: Support for different job execution environments
2. **Enhanced Monitoring**: Additional metrics and alerting capabilities
3. **Scalability**: Distributed worker support and load balancing
4. **Integration**: Plugins for popular frameworks and services
5. **Documentation**: Examples, tutorials, and best practices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the command help: `python queuectl.py --help`
3. Use the interactive shell help: `queuectl> help`
4. Check the logs: `queuectl> scheduler logs`

---

**QueueCTL v1.0.0** - Production-Grade CLI Job Queue System