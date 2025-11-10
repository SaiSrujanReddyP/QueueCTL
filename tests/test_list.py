#!/usr/bin/env python3
"""
Test job listing functionality
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.job_queue import JobQueue

def test_list_all_jobs():
    """Test listing all jobs"""
    print("Testing List All Jobs...")
    
    result = subprocess.run(
        "python queuectl.py list",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: List all jobs works")
        return True
    else:
        print("  FAIL: List all jobs failed")
        return False

def test_list_by_state():
    """Test listing jobs by state"""
    print("Testing List by State...")
    
    states = ['pending', 'completed', 'failed', 'dead', 'scheduled']
    
    for state in states:
        result = subprocess.run(
            f"python queuectl.py list --state {state}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  FAIL: List {state} jobs failed")
            return False
    
    print("  PASS: List by state works for all states")
    return True

def test_list_with_limit():
    """Test listing jobs with limit"""
    print("Testing List with Limit...")
    
    result = subprocess.run(
        "python queuectl.py list --limit 5",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: List with limit works")
        return True
    else:
        print("  FAIL: List with limit failed")
        return False

def test_list_table_format():
    """Test list table formatting"""
    print("Testing List Table Format...")
    
    result = subprocess.run(
        "python queuectl.py list --limit 3",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("|" in result.stdout or "ID" in result.stdout):
        print("  PASS: Table format works")
        return True
    else:
        print("  FAIL: Table format not working")
        return False

def test_list_empty_state():
    """Test listing empty state"""
    print("Testing List Empty State...")
    
    # Try to list a state that might be empty
    result = subprocess.run(
        "python queuectl.py list --state failed",
        shell=True,
        capture_output=True,
        text=True
    )
    
    # Should handle empty results gracefully
    if result.returncode == 0:
        print("  PASS: Empty state handled gracefully")
        return True
    else:
        print("  FAIL: Empty state not handled properly")
        return False

def test_list_help():
    """Test list command help"""
    print("Testing List Help...")
    
    result = subprocess.run(
        "python queuectl.py list --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("state" in result.stdout or "limit" in result.stdout):
        print("  PASS: List help available")
        return True
    else:
        print("  FAIL: List help not working")
        return False

def test_list_full_ids():
    """Test that full job IDs are displayed"""
    print("Testing Full Job IDs...")
    
    # Add a test job with known ID
    jq = JobQueue()
    try:
        jq.delete_job('full_id_test_12345')
    except:
        pass
    
    job = jq.enqueue({
        'id': 'full_id_test_12345',
        'command': 'echo Full ID test'
    })
    
    # List jobs and check if full ID is shown
    result = subprocess.run(
        "python queuectl.py list --state pending",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "full_id_test_12345" in result.stdout:
        print("  PASS: Full job IDs displayed")
        return True
    else:
        print("  FAIL: Full job IDs not displayed")
        return False

def test_list_job_details():
    """Test that job details are shown"""
    print("Testing Job Details Display...")
    
    result = subprocess.run(
        "python queuectl.py list --limit 1",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for common table headers
        if any(header in result.stdout for header in ["Command", "State", "ID"]):
            print("  PASS: Job details displayed")
            return True
        else:
            print("  FAIL: Job details not properly displayed")
            return False
    else:
        print("  FAIL: Could not retrieve job details")
        return False

def main():
    """Run all list tests"""
    print("=== Testing Job Listing ===")
    print()
    
    tests = [
        test_list_help,
        test_list_all_jobs,
        test_list_by_state,
        test_list_with_limit,
        test_list_table_format,
        test_list_empty_state,
        test_list_full_ids,
        test_list_job_details
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
    
    print(f"List Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()