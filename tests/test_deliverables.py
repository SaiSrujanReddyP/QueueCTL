#!/usr/bin/env python3
"""
Test core deliverable requirements
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_job_enqueuing():
    """Test basic job enqueuing"""
    print("Testing Job Enqueuing...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('deliverable_test')
    except:
        pass
    
    # Test enqueuing
    job = jq.enqueue({
        'id': 'deliverable_test',
        'command': 'echo Deliverable test job'
    })
    
    if job and job['id'] == 'deliverable_test':
        print("  PASS: Job enqueuing works")
        return True
    else:
        print("  FAIL: Job enqueuing failed")
        return False

def test_job_processing():
    """Test job processing by workers"""
    print("Testing Job Processing...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('processing_test')
    except:
        pass
    
    # Add test job
    job = jq.enqueue({
        'id': 'processing_test',
        'command': 'echo Processing test'
    })
    
    # Start worker briefly to process job
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for processing
    time.sleep(3)
    
    # Stop worker
    worker_process.terminate()
    worker_process.wait()
    
    # Check if job was processed
    completed_jobs = jq.list_jobs('completed')
    completed_ids = [job['id'] for job in completed_jobs]
    
    if 'processing_test' in completed_ids:
        print("  PASS: Job processing works")
        return True
    else:
        print("  FAIL: Job was not processed")
        return False

def test_job_states():
    """Test different job states"""
    print("Testing Job States...")
    
    jq = JobQueue()
    
    # Test pending state
    pending_jobs = jq.list_jobs('pending')
    print(f"  Pending jobs: {len(pending_jobs)}")
    
    # Test completed state
    completed_jobs = jq.list_jobs('completed')
    print(f"  Completed jobs: {len(completed_jobs)}")
    
    # Test failed state
    failed_jobs = jq.list_jobs('failed')
    print(f"  Failed jobs: {len(failed_jobs)}")
    
    # Test dead state
    dead_jobs = jq.list_jobs('dead')
    print(f"  Dead jobs: {len(dead_jobs)}")
    
    print("  PASS: All job states accessible")
    return True

def test_cli_interface():
    """Test CLI interface"""
    print("Testing CLI Interface...")
    
    # Test main help
    result = subprocess.run(
        "python queuectl.py --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "QueueCTL" in result.stdout:
        print("  PASS: CLI help works")
    else:
        print("  FAIL: CLI help not working")
        return False
    
    # Test status command
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Status command works")
    else:
        print("  FAIL: Status command not working")
        return False
    
    return True

def test_worker_management():
    """Test worker management"""
    print("Testing Worker Management...")
    
    # Test worker help
    result = subprocess.run(
        "python queuectl.py worker --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "start" in result.stdout:
        print("  PASS: Worker commands available")
    else:
        print("  FAIL: Worker commands not working")
        return False
    
    # Test worker status
    result = subprocess.run(
        "python queuectl.py worker status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Worker status works")
    else:
        print("  FAIL: Worker status not working")
        return False
    
    return True

def test_job_listing():
    """Test job listing functionality"""
    print("Testing Job Listing...")
    
    # Test list all jobs
    result = subprocess.run(
        "python queuectl.py list",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Job listing works")
    else:
        print("  FAIL: Job listing not working")
        return False
    
    # Test list by state
    result = subprocess.run(
        "python queuectl.py list --state pending",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: State filtering works")
    else:
        print("  FAIL: State filtering not working")
        return False
    
    return True

def main():
    """Run all deliverable tests"""
    print("=== Testing Core Deliverables ===")
    print()
    
    tests = [
        test_job_enqueuing,
        test_job_processing,
        test_job_states,
        test_cli_interface,
        test_worker_management,
        test_job_listing
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
    
    print(f"Core Deliverables Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()