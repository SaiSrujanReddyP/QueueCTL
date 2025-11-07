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

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone or download the project:**
   ```bash
   # If using git
   git clone <repository-url>
   cd queuectl
   
   # Or download and extract the ZIP file
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python queuectl.py --help
   ```

### Quick Setup (Alternative)
```bash
# Run the setup script
python setup.py

# Or install manually
pip install typer rich sqlite3 flask requests
```## Quick Start

### 1. First Run - See the ASCII Art
```bash
python queuectl.py
```
This displays the beautiful ASCII banner and automatically starts the interactive shell.

### 2. Add Your First Job
```bash
# Easy way (recommended for beginners)
python queuectl.py add "echo Hello World" --id my-first-job

# Advanced way with JSON
python queuectl.py enqueue '{"id":"test","command":"echo Hello","priority":5}'
```

### 3. Start Workers
```bash
python queuectl.py worker start --count 2
```

### 4. Check Status
```bash
python queuectl.py status
```

### 5. View Jobs
```bash
python queuectl.py list
```

## Usage Examples

### Basic Job Management

**Add a simple job:**
```bash
$ python queuectl.py add "echo Hello World" --id hello
 Job added: hello
  Command: echo Hello World
  Priority: 0
  Max retries: 3
```

**Add a job with priority:**
```bash
$ python queuectl.py add "ping google.com" --id ping --priority 10 --retries 5
 Job added: ping
  Command: ping google.com
  Priority: 10
  Max retries: 5
```

**Start workers:**
```bash
$ python queuectl.py worker start --count 3
INFO: Starting 3 worker processes
   Started worker worker_123_0 (PID: 1234)
   Started worker worker_123_1 (PID: 1235)  
   Started worker worker_123_2 (PID: 1236)
Press Ctrl+C to stop workers gracefully
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
queuectl> schedule "backup database" "+1h"
queuectl> schedule "send report" "+30m"
queuectl> schedule "cleanup logs" "+1d"
```

**Using absolute time:**
```bash
queuectl> schedule "daily backup" "2025-11-10 02:00:00"
```

### Viewing Scheduled Jobs

**List all scheduled jobs:**
```bash
queuectl> scheduled
```

**View all jobs (including scheduled):**
```bash
queuectl> list
```

### How Scheduled Jobs Work

1. **Creation**: Jobs are created with `scheduled` state and `run_at` timestamp
2. **Monitoring**: Scheduler daemon checks every 5 seconds for due jobs
3. **Conversion**: When time arrives, jobs automatically become `pending`
4. **Processing**: Pending jobs are processed by active workers
5. **Completion**: Jobs move to `completed`, `failed`, or `dead` states
## Inter
active Shell Commands

QueueCTL provides a rich interactive shell with tab completion and command history:

### Job Management
```bash
queuectl> add "echo hello" --id test          # Add simple job
queuectl> schedule "backup" "+1h"             # Schedule job
queuectl> list                                # List all jobs
queuectl> list --state pending                # Filter by state
queuectl> scheduled                           # Show only scheduled jobs
```

### Worker Management
```bash
queuectl> worker start --count 2              # Start 2 workers
queuectl> worker stop                         # Stop all workers
queuectl> worker status                       # Check worker status
```

### Scheduler Management
```bash
queuectl> scheduler start --workers 2         # Start scheduler (manual mode)
queuectl> scheduler start --workers 2 --auto  # Start scheduler (auto mode)
queuectl> scheduler status                    # Check scheduler status
queuectl> scheduler logs                      # View scheduler logs
queuectl> scheduler stop                      # Stop scheduler
```

### System Information
```bash
queuectl> status                              # System status
queuectl> time                                # Current time (local/UTC)
queuectl> metrics                             # Performance metrics
queuectl> config                              # Configuration settings
```

### Utility Commands
```bash
queuectl> demo                                # Add demo jobs for testing
queuectl> help                                # Show all commands
queuectl> exit                                # Exit shell
```

## Configuration

QueueCTL supports persistent configuration management:

### View Configuration
```bash
python queuectl.py config show
```

### Update Configuration
```bash
python queuectl.py config set max_retries 5
python queuectl.py config set timeout_seconds 300
python queuectl.py config set worker_count 4
```

### Configuration Options
- `max_retries`: Default maximum retry attempts (default: 3)
- `timeout_seconds`: Default job timeout (default: 300)
- `worker_count`: Default number of workers (default: 2)
- `retry_delay`: Base retry delay in seconds (default: 2)
- `max_retry_delay`: Maximum retry delay (default: 300)

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
python queuectl.py add "command" --id job_id  # Add job
python queuectl.py list                       # List jobs
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
python queuectl.py config show                # Show configuration
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