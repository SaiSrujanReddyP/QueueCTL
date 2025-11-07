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
queuectl> enqueue {"id":"test","command":"echo hello"}     # Add simple job
queuectl> enqueue {"id":"backup","command":"backup","run_at":"+1h"}  # Schedule job
queuectl> list                                            # List all jobs (full IDs)
queuectl> list --state pending                            # Filter by state
queuectl> list --state scheduled                          # Show only scheduled jobs
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
queuectl> time                                # Show current time (local/UTC)
queuectl> exit                                # Exit shell
```

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