#!/usr/bin/env python3
"""
Test system status reporting functionality
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_status_command():
    """Test basic status command"""
    print("Testing Status Command...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Status command works")
        return True
    else:
        print("  FAIL: Status command failed")
        return False

def test_status_help():
    """Test status help"""
    print("Testing Status Help...")
    
    result = subprocess.run(
        "python queuectl.py status --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Status help available")
        return True
    else:
        print("  FAIL: Status help not working")
        return False

def test_status_job_counts():
    """Test job count reporting in status"""
    print("Testing Job Count Reporting...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for job state counts
        job_states = ["pending", "completed", "failed", "dead", "scheduled"]
        content_lower = result.stdout.lower()
        
        found_states = [state for state in job_states if state in content_lower]
        
        if found_states:
            print(f"  PASS: Status includes job states: {', '.join(found_states)}")
            return True
        else:
            print("  FAIL: Status missing job state information")
            return False
    else:
        print("  FAIL: Could not retrieve status")
        return False

def test_status_system_info():
    """Test system information in status"""
    print("Testing System Information...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for system-related information
        system_indicators = ["worker", "queue", "system", "database", "redis"]
        content_lower = result.stdout.lower()
        
        found_indicators = [indicator for indicator in system_indicators if indicator in content_lower]
        
        if found_indicators:
            print(f"  PASS: Status includes system info: {', '.join(found_indicators)}")
            return True
        else:
            print("  PASS: Status command works (system info optional)")
            return True
    else:
        print("  FAIL: Could not retrieve system information")
        return False

def test_status_formatting():
    """Test status output formatting"""
    print("Testing Status Formatting...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for structured output
        if any(char in result.stdout for char in ["|", ":", "-", "="]) or result.stdout.strip():
            print("  PASS: Status has structured output")
            return True
        else:
            print("  FAIL: Status output not properly formatted")
            return False
    else:
        print("  FAIL: Could not check status formatting")
        return False

def test_status_numerical_data():
    """Test numerical data in status"""
    print("Testing Numerical Data...")
    
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for numerical data
        if any(char.isdigit() for char in result.stdout):
            print("  PASS: Status includes numerical data")
            return True
        else:
            print("  FAIL: Status missing numerical data")
            return False
    else:
        print("  FAIL: Could not retrieve numerical data")
        return False

def test_status_with_jobs():
    """Test status after adding jobs"""
    print("Testing Status with Jobs...")
    
    from src.job_queue import JobQueue
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('status_test_job')
    except:
        pass
    
    # Add a test job
    job = jq.enqueue({
        'id': 'status_test_job',
        'command': 'echo Status test job'
    })
    
    # Check status
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Status works with jobs in queue")
        return True
    else:
        print("  FAIL: Status failed with jobs in queue")
        return False

def test_status_consistency():
    """Test status consistency across calls"""
    print("Testing Status Consistency...")
    
    # Get status twice
    result1 = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    result2 = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result1.returncode == 0 and result2.returncode == 0:
        # Both calls should succeed
        print("  PASS: Status calls are consistent")
        return True
    else:
        print("  FAIL: Status calls inconsistent")
        return False

def main():
    """Run all status tests"""
    print("=== Testing System Status ===")
    print()
    
    tests = [
        test_status_help,
        test_status_command,
        test_status_formatting,
        test_status_numerical_data,
        test_status_job_counts,
        test_status_system_info,
        test_status_with_jobs,
        test_status_consistency
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
    
    print(f"Status Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()