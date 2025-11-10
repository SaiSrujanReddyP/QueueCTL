#!/usr/bin/env python3
"""
Test performance metrics functionality
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_metrics_command():
    """Test basic metrics command"""
    print("Testing Metrics Command...")
    
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Metrics command works")
        return True
    else:
        print("  FAIL: Metrics command failed")
        return False

def test_metrics_help():
    """Test metrics help"""
    print("Testing Metrics Help...")
    
    result = subprocess.run(
        "python queuectl.py metrics --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Metrics help available")
        return True
    else:
        print("  FAIL: Metrics help not working")
        return False

def test_metrics_content():
    """Test metrics content"""
    print("Testing Metrics Content...")
    
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for common metric indicators
        metrics_indicators = [
            "jobs", "completed", "failed", "pending",
            "total", "rate", "time", "performance"
        ]
        
        content_lower = result.stdout.lower()
        found_indicators = [indicator for indicator in metrics_indicators if indicator in content_lower]
        
        if found_indicators:
            print(f"  PASS: Metrics content includes: {', '.join(found_indicators)}")
            return True
        else:
            print("  FAIL: Metrics content missing expected indicators")
            return False
    else:
        print("  FAIL: Could not retrieve metrics content")
        return False

def test_metrics_with_jobs():
    """Test metrics after processing jobs"""
    print("Testing Metrics with Job Processing...")
    
    from src.job_queue import JobQueue
    jq = JobQueue()
    
    # Clean up test job
    try:
        jq.delete_job('metrics_test_job')
    except:
        pass
    
    # Add a test job
    job = jq.enqueue({
        'id': 'metrics_test_job',
        'command': 'echo Metrics test job'
    })
    
    # Process the job quickly
    worker_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "worker", "start", "--count", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    worker_process.terminate()
    worker_process.wait()
    
    # Check metrics
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Metrics available after job processing")
        return True
    else:
        print("  FAIL: Metrics not available after job processing")
        return False

def test_metrics_formatting():
    """Test metrics output formatting"""
    print("Testing Metrics Formatting...")
    
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Check for structured output (tables, sections, etc.)
        if any(char in result.stdout for char in ["|", ":", "-", "="]):
            print("  PASS: Metrics have structured formatting")
            return True
        else:
            print("  FAIL: Metrics formatting not structured")
            return False
    else:
        print("  FAIL: Could not check metrics formatting")
        return False

def test_metrics_performance_data():
    """Test performance-related metrics"""
    print("Testing Performance Metrics...")
    
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Look for performance-related terms
        performance_terms = ["time", "duration", "rate", "throughput", "average", "total"]
        content_lower = result.stdout.lower()
        
        found_terms = [term for term in performance_terms if term in content_lower]
        
        if found_terms:
            print(f"  PASS: Performance metrics include: {', '.join(found_terms)}")
            return True
        else:
            print("  FAIL: Performance metrics not found")
            return False
    else:
        print("  FAIL: Could not retrieve performance metrics")
        return False

def test_metrics_statistics():
    """Test statistical metrics"""
    print("Testing Statistical Metrics...")
    
    result = subprocess.run(
        "python queuectl.py metrics",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Look for statistical data
        if any(char.isdigit() for char in result.stdout):
            print("  PASS: Metrics include numerical statistics")
            return True
        else:
            print("  FAIL: No numerical statistics in metrics")
            return False
    else:
        print("  FAIL: Could not retrieve statistical metrics")
        return False

def main():
    """Run all metrics tests"""
    print("=== Testing Performance Metrics ===")
    print()
    
    tests = [
        test_metrics_help,
        test_metrics_command,
        test_metrics_content,
        test_metrics_formatting,
        test_metrics_statistics,
        test_metrics_performance_data,
        test_metrics_with_jobs
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
    
    print(f"Metrics Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()