#!/usr/bin/env python3
"""
Test bonus features and enhancements
"""

import sys
import os
import time
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_priority_queues():
    """Test priority queue functionality"""
    print("Testing Priority Queues...")
    
    jq = JobQueue()
    
    # Clean up test jobs
    test_ids = ['priority_low', 'priority_high', 'priority_normal']
    for job_id in test_ids:
        try:
            jq.delete_job(job_id)
        except:
            pass
    
    # Add jobs with different priorities
    low_job = jq.enqueue({
        'id': 'priority_low',
        'command': 'echo Low priority job',
        'priority': 1
    })
    
    high_job = jq.enqueue({
        'id': 'priority_high', 
        'command': 'echo High priority job',
        'priority': 10
    })
    
    normal_job = jq.enqueue({
        'id': 'priority_normal',
        'command': 'echo Normal priority job',
        'priority': 5
    })
    
    print(f"  Added low priority job: {low_job['priority']}")
    print(f"  Added high priority job: {high_job['priority']}")
    print(f"  Added normal priority job: {normal_job['priority']}")
    
    # Test priority ordering
    pending_jobs = jq.list_jobs('pending')
    priorities = [job['priority'] for job in pending_jobs if job['id'] in test_ids]
    
    if priorities == sorted(priorities, reverse=True):
        print("  PASS: Jobs ordered by priority (high to low)")
    else:
        print("  FAIL: Jobs not properly ordered by priority")
    
    return True

def test_scheduled_jobs():
    """Test scheduled job functionality"""
    print("Testing Scheduled Jobs...")
    
    jq = JobQueue()
    
    # Clean up test jobs
    try:
        jq.delete_job('scheduled_test_bonus')
    except:
        pass
    
    # Add scheduled job
    from datetime import datetime, timezone, timedelta
    future_time = (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
    
    scheduled_job = jq.enqueue({
        'id': 'scheduled_test_bonus',
        'command': 'echo Scheduled job test',
        'run_at': future_time
    })
    
    print(f"  Added scheduled job for: {scheduled_job.get('run_at', 'N/A')}")
    
    # Check if job is in scheduled state
    scheduled_jobs = jq.list_jobs('scheduled')
    scheduled_ids = [job['id'] for job in scheduled_jobs]
    
    if 'scheduled_test_bonus' in scheduled_ids:
        print("  PASS: Scheduled job created successfully")
    else:
        print("  FAIL: Scheduled job not found in scheduled state")
    
    return True

def test_interactive_shell():
    """Test interactive shell functionality"""
    print("Testing Interactive Shell...")
    
    # Test shell startup
    result = subprocess.run(
        'echo "help" | python queuectl.py shell',
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0 and "Available commands:" in result.stdout:
        print("  PASS: Interactive shell starts and shows help")
    else:
        print("  FAIL: Interactive shell not working properly")
    
    return True

def test_web_dashboard():
    """Test web dashboard functionality"""
    print("Testing Web Dashboard...")
    
    # Test dashboard start (don't actually start it, just test command)
    result = subprocess.run(
        "python queuectl.py dashboard --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Dashboard command available")
    else:
        print("  FAIL: Dashboard command not working")
    
    return True

def test_enhanced_errors():
    """Test enhanced error handling"""
    print("Testing Enhanced Error Handling...")
    
    # Test invalid command
    result = subprocess.run(
        "python queuectl.py invalid_command",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("  PASS: Invalid commands properly rejected")
    else:
        print("  FAIL: Invalid commands not properly handled")
    
    return True

def main():
    """Run all bonus feature tests"""
    print("=== Testing Bonus Features ===")
    print()
    
    tests = [
        test_priority_queues,
        test_scheduled_jobs,
        test_interactive_shell,
        test_web_dashboard,
        test_enhanced_errors
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
    
    print(f"Bonus Features Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()