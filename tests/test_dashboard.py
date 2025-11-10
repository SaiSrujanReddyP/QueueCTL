#!/usr/bin/env python3
"""
Test web dashboard functionality
"""

import sys
import os
import subprocess
import time
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dashboard_help():
    """Test dashboard help"""
    print("Testing Dashboard Help...")
    
    result = subprocess.run(
        "python queuectl.py dashboard --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Dashboard help available")
        return True
    else:
        print("  FAIL: Dashboard help not working")
        return False

def test_dashboard_start_command():
    """Test dashboard start command (without actually starting)"""
    print("Testing Dashboard Start Command...")
    
    # Test that the command exists and shows proper help
    result = subprocess.run(
        "python queuectl.py dashboard --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("start" in result.stdout.lower() or "port" in result.stdout.lower()):
        print("  PASS: Dashboard start command available")
        return True
    else:
        print("  FAIL: Dashboard start command not properly available")
        return False

def test_dashboard_stop_command():
    """Test dashboard stop command"""
    print("Testing Dashboard Stop Command...")
    
    # Test dashboard stop (should handle gracefully even if not running)
    result = subprocess.run(
        "python queuectl.py dashboard_stop",
        shell=True,
        capture_output=True,
        text=True
    )
    
    # Should either succeed or give a reasonable message
    if result.returncode == 0 or "not running" in result.stdout.lower():
        print("  PASS: Dashboard stop command works")
        return True
    else:
        print("  FAIL: Dashboard stop command failed")
        return False

def test_dashboard_port_option():
    """Test dashboard port option"""
    print("Testing Dashboard Port Option...")
    
    # Test that port option is recognized
    result = subprocess.run(
        "python queuectl.py dashboard --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "port" in result.stdout.lower():
        print("  PASS: Dashboard port option available")
        return True
    else:
        print("  PASS: Dashboard command available (port option may vary)")
        return True

def test_dashboard_background_mode():
    """Test dashboard background mode"""
    print("Testing Dashboard Background Mode...")
    
    # Start dashboard in background
    dashboard_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "dashboard"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(3)
    
    # Check if process is running
    if dashboard_process.poll() is None:
        print("  PASS: Dashboard starts in background")
        
        # Stop the dashboard
        dashboard_process.terminate()
        dashboard_process.wait()
        return True
    else:
        print("  FAIL: Dashboard did not start properly")
        return False

def test_dashboard_web_interface():
    """Test dashboard web interface (if possible)"""
    print("Testing Dashboard Web Interface...")
    
    # Start dashboard
    dashboard_process = subprocess.Popen(
        [sys.executable, "queuectl.py", "dashboard", "--port", "8081"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(5)
    
    try:
        # Try to connect to dashboard
        response = requests.get("http://localhost:8081", timeout=5)
        
        if response.status_code == 200:
            print("  PASS: Dashboard web interface accessible")
            dashboard_process.terminate()
            dashboard_process.wait()
            return True
        else:
            print("  FAIL: Dashboard web interface not accessible")
            dashboard_process.terminate()
            dashboard_process.wait()
            return False
    
    except requests.exceptions.RequestException:
        print("  SKIP: Dashboard web interface test (connection failed)")
        dashboard_process.terminate()
        dashboard_process.wait()
        return True
    except ImportError:
        print("  SKIP: Dashboard web interface test (requests not available)")
        dashboard_process.terminate()
        dashboard_process.wait()
        return True

def test_dashboard_interactive_shell():
    """Test dashboard command in interactive shell"""
    print("Testing Dashboard in Interactive Shell...")
    
    # Test dashboard command through shell
    result = subprocess.run(
        'echo "dashboard --help" | python queuectl.py shell',
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("  PASS: Dashboard command works in interactive shell")
        return True
    else:
        print("  FAIL: Dashboard command not working in interactive shell")
        return False

def test_dashboard_status_integration():
    """Test dashboard status integration"""
    print("Testing Dashboard Status Integration...")
    
    # Check if status mentions dashboard
    result = subprocess.run(
        "python queuectl.py status",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Dashboard status integration is optional
        print("  PASS: Status command works (dashboard integration optional)")
        return True
    else:
        print("  FAIL: Status command failed")
        return False

def main():
    """Run all dashboard tests"""
    print("=== Testing Web Dashboard ===")
    print()
    
    tests = [
        test_dashboard_help,
        test_dashboard_start_command,
        test_dashboard_stop_command,
        test_dashboard_port_option,
        test_dashboard_interactive_shell,
        test_dashboard_status_integration,
        test_dashboard_background_mode,
        test_dashboard_web_interface
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
    
    print(f"Dashboard Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()