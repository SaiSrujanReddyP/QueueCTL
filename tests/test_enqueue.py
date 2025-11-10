#!/usr/bin/env python3
"""
Test job enqueuing functionality
"""

import sys
import os
import subprocess
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_basic_enqueue():
    """Test basic job enqueuing"""
    print("Testing Basic Enqueue...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('basic_enqueue_test')
    except:
        pass
    
    # Test basic enqueue
    job = jq.enqueue({
        'id': 'basic_enqueue_test',
        'command': 'echo Basic enqueue test'
    })
    
    if job and job['id'] == 'basic_enqueue_test':
        print("  PASS: Basic enqueue works")
        return True
    else:
        print("  FAIL: Basic enqueue failed")
        return False

def test_enqueue_with_priority():
    """Test enqueuing with priority"""
    print("Testing Enqueue with Priority...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('priority_enqueue_test')
    except:
        pass
    
    # Test enqueue with priority
    job = jq.enqueue({
        'id': 'priority_enqueue_test',
        'command': 'echo Priority test',
        'priority': 8
    })
    
    if job and job['priority'] == 8:
        print("  PASS: Priority enqueue works")
        return True
    else:
        print("  FAIL: Priority enqueue failed")
        return False

def test_enqueue_scheduled():
    """Test enqueuing scheduled jobs"""
    print("Testing Scheduled Enqueue...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('scheduled_enqueue_test')
    except:
        pass
    
    # Test scheduled enqueue
    from datetime import datetime, timezone, timedelta
    future_time = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    
    job = jq.enqueue({
        'id': 'scheduled_enqueue_test',
        'command': 'echo Scheduled test',
        'run_at': future_time
    })
    
    if job and job.get('run_at'):
        print("  PASS: Scheduled enqueue works")
        return True
    else:
        print("  FAIL: Scheduled enqueue failed")
        return False

def test_enqueue_cli():
    """Test CLI enqueue command"""
    print("Testing CLI Enqueue...")
    
    # Test CLI enqueue
    job_data = {
        'id': 'cli_enqueue_test',
        'command': 'echo CLI enqueue test'
    }
    
    result = subprocess.run(
        f'python queuectl.py enqueue \'{json.dumps(job_data)}\'',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "enqueued" in result.stdout.lower():
        print("  PASS: CLI enqueue works")
        return True
    else:
        print("  FAIL: CLI enqueue failed")
        return False

def test_enqueue_with_timeout():
    """Test enqueuing with custom timeout"""
    print("Testing Enqueue with Timeout...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('timeout_enqueue_test')
    except:
        pass
    
    # Test enqueue with timeout
    job = jq.enqueue({
        'id': 'timeout_enqueue_test',
        'command': 'echo Timeout test',
        'timeout': 60
    })
    
    if job and job.get('timeout') == 60:
        print("  PASS: Timeout enqueue works")
        return True
    else:
        print("  FAIL: Timeout enqueue failed")
        return False

def test_enqueue_with_retries():
    """Test enqueuing with custom retry count"""
    print("Testing Enqueue with Retries...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('retry_enqueue_test')
    except:
        pass
    
    # Test enqueue with retries
    job = jq.enqueue({
        'id': 'retry_enqueue_test',
        'command': 'echo Retry test',
        'max_retries': 5
    })
    
    if job and job.get('max_retries') == 5:
        print("  PASS: Retry enqueue works")
        return True
    else:
        print("  FAIL: Retry enqueue failed")
        return False

def test_enqueue_validation():
    """Test enqueue input validation"""
    print("Testing Enqueue Validation...")
    
    jq = JobQueue()
    
    # Test missing command
    try:
        job = jq.enqueue({
            'id': 'invalid_test'
            # Missing command
        })
        print("  FAIL: Should reject job without command")
        return False
    except:
        print("  PASS: Properly validates required fields")
        return True

def test_enqueue_duplicate_id():
    """Test enqueuing with duplicate ID"""
    print("Testing Duplicate ID Handling...")
    
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('duplicate_test')
    except:
        pass
    
    # Add first job
    job1 = jq.enqueue({
        'id': 'duplicate_test',
        'command': 'echo First job'
    })
    
    # Try to add duplicate
    try:
        job2 = jq.enqueue({
            'id': 'duplicate_test',
            'command': 'echo Second job'
        })
        print("  FAIL: Should reject duplicate IDs")
        return False
    except:
        print("  PASS: Properly rejects duplicate IDs")
        return True

def main():
    """Run all enqueue tests"""
    print("=== Testing Job Enqueuing ===")
    print()
    
    tests = [
        test_basic_enqueue,
        test_enqueue_with_priority,
        test_enqueue_scheduled,
        test_enqueue_with_timeout,
        test_enqueue_with_retries,
        test_enqueue_cli,
        test_enqueue_validation,
        test_enqueue_duplicate_id
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
    
    print(f"Enqueue Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()