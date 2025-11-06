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

### Bonus Features
- **Job Timeout Handling** - Per-job timeout configuration
- **Priority Queues** - Higher priority jobs processed first
- **Scheduled Jobs** - Delayed execution with run_at timestamps
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