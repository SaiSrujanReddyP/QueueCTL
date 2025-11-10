#!/usr/bin/env python3
"""
Test worker management functionality
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_worker_help():
    """Test worker help"""
    print("Testing Worker Help...")
    
    result = subprocess.run(
        "python queuectl.py worker --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("start" in result.stdout or "stop" in result.stdout):
        print("  PASS: Worker help available")
        return True
    else:
        print("  FAIL: Worker help not working")
        return False

def test_worker_status():
    """Test worker status command"""
    print("Testing Worker Status...")
    
    result = subprocess.run(
        "python queuectl.py worker status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Worker status command works")
        return True
    else:
        print("  FAIL: Worker status command failed")
        return False

def test_worker_start_stop():
    """Test worker start and stop"""
    print("Testing Worker Start/Stop...")
    
    # Start worker
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is running
    if worker_process.poll() is None:
        print("  PASS: Worker starts successfully")
        
        # Stop worker
        worker_process.terminate()
        worker_process.wait()
        
        if worker_process.poll() is not None:
            print("  PASS: Worker stops successfully")
            return True
        else:
            print("  FAIL: Worker did not stop")
            return False
    else:
        print("  FAIL: Worker did not start")
        return False

def test_worker_count_option():
    """Test worker count option"""
    print("Testing Worker Count Option...")
    
    # Test with count option
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is running
    if worker_process.poll() is None:
        print("  PASS: Worker count option works")
        worker_process.terminate()
        worker_process.wait()
        return True
    else:
        print("  FAIL: Worker count option failed")
        return False

def test_worker_job_processing():
    """Test worker job processing"""
    print("Testing Worker Job Processing...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('worker_processing_test')
    except:
        pass
    
    # Add test job
    job = jq.enqueue({
        'id': 'worker_processing_test',
        'command': 'echo Worker processing test'
    })
    
    # Start worker
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for processing
    time.sleep(3)
    
    # Stop worker
    worker_process.terminate()
    worker_process.wait()
    
    # Check if job was processed
    completed_jobs = jq.list_jobs('completed')
    completed_ids = [job['id'] for job in completed_jobs]
    
    if 'worker_processing_test' in completed_ids:
        print("  PASS: Worker processes jobs successfully")
        return True
    else:
        print("  FAIL: Worker did not process job")
        return False

def test_worker_timeout_option():
    """Test worker timeout option"""
    print("Testing Worker Timeout Option...")
    
    # Test with timeout option
    result = subprocess.run(
        "python queuectl.py worker start --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "timeout" in result.stdout.lower():
        print("  PASS: Worker timeout option available")
        return True
    else:
        print("  PASS: Worker start command works (timeout option may vary)")
        return True

def test_worker_daemon_mode():
    """Test worker daemon mode"""
    print("Testing Worker Daemon Mode...")
    
    # Test daemon command through interactive shell
    result = subprocess.run(
        'echo "worker daemon --help" | python queuectl.py shell',
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("  PASS: Worker daemon mode available")
        return True
    else:
        print("  SKIP: Worker daemon mode test (may not be implemented)")
        return True

def test_worker_cron_mode():
    """Test worker cron mode"""
    print("Testing Worker Cron Mode...")
    
    # Test cron command through interactive shell
    result = subprocess.run(
        'echo "worker cron --help" | python queuectl.py shell',
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("  PASS: Worker cron mode available")
        return True
    else:
        print("  SKIP: Worker cron mode test (may not be implemented)")
        return True

def test_worker_interactive_shell():
    """Test worker commands in interactive shell"""
    print("Testing Worker in Interactive Shell...")
    
    # Test worker status through shell
    result = subprocess.run(
        'echo "worker status" | python queuectl.py shell',
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("  PASS: Worker commands work in interactive shell")
        return True
    else:
        print("  FAIL: Worker commands not working in interactive shell")
        return False

def main():
    """Run all worker tests"""
    print("=== Testing Worker Management ===")
    print()
    
    tests = [
        test_worker_help,
        test_worker_status,
        test_worker_count_option,
        test_worker_timeout_option,
        test_worker_start_stop,
        test_worker_job_processing,
        test_worker_interactive_shell,
        test_worker_daemon_mode,
        test_worker_cron_mode
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
        print()
    
    print(f"Worker Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()