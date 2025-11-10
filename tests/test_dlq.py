#!/usr/bin/env python3
"""
Test Dead Letter Queue (DLQ) functionality
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_dlq_creation():
    """Test that failed jobs go to DLQ"""
    print("Testing DLQ Creation...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('dlq_test_fail')
    except:
        pass
    
    # Add a job that will fail
    job = jq.enqueue({
        'id': 'dlq_test_fail',
        'command': 'nonexistent_command_that_will_fail',
        'max_retries': 1  # Fail quickly
    })
    
    print(f"  Added failing job: {job['id']}")
    
    # Start worker to process the failing job
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for processing and retries
    time.sleep(5)
    
    # Stop worker
    worker_process.terminate()
    worker_process.wait()
    
    # Check if job is in DLQ
    dead_jobs = jq.list_jobs('dead')
    dead_ids = [job['id'] for job in dead_jobs]
    
    if 'dlq_test_fail' in dead_ids:
        print("  PASS: Failed job moved to DLQ")
        return True
    else:
        print("  FAIL: Failed job not in DLQ")
        return False

def test_dlq_list():
    """Test listing DLQ jobs"""
    print("Testing DLQ List...")
    
    result = subprocess.run(
        "python queuectl.py dlq list",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: DLQ list command works")
        return True
    else:
        print("  FAIL: DLQ list command failed")
        return False

def test_dlq_retry():
    """Test retrying DLQ jobs"""
    print("Testing DLQ Retry...")
    
    # First ensure we have a job in DLQ
    jq = JobQueue()
    dead_jobs = jq.list_jobs('dead')
    
    if not dead_jobs:
        print("  SKIP: No jobs in DLQ to retry")
        return True
    
    # Get first dead job ID
    dead_job_id = dead_jobs[0]['id']
    
    # Test retry command
    result = subprocess.run(
        f"python queuectl.py dlq retry {dead_job_id}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: DLQ retry command works")
        return True
    else:
        print("  FAIL: DLQ retry command failed")
        return False

def test_dlq_retry_all():
    """Test retrying all DLQ jobs"""
    print("Testing DLQ Retry All...")
    
    result = subprocess.run(
        "python queuectl.py dlq retry --all",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: DLQ retry all command works")
        return True
    else:
        print("  FAIL: DLQ retry all command failed")
        return False

def test_dlq_help():
    """Test DLQ help"""
    print("Testing DLQ Help...")
    
    result = subprocess.run(
        "python queuectl.py dlq --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("list" in result.stdout or "retry" in result.stdout):
        print("  PASS: DLQ help available")
        return True
    else:
        print("  FAIL: DLQ help not working")
        return False

def test_dlq_statistics():
    """Test DLQ statistics in status"""
    print("Testing DLQ Statistics...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("Dead" in result.stdout or "Failed" in result.stdout):
        print("  PASS: DLQ statistics shown in status")
        return True
    else:
        print("  FAIL: DLQ statistics not in status")
        return False

def main():
    """Run all DLQ tests"""
    print("=== Testing Dead Letter Queue ===")
    print()
    
    tests = [
        test_dlq_help,
        test_dlq_list,
        test_dlq_statistics,
        test_dlq_creation,
        test_dlq_retry,
        test_dlq_retry_all
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
    
    print(f"DLQ Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()