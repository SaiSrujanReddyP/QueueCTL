#!/usr/bin/env python3
"""
Test configuration management functionality
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_set():
    """Test setting configuration values"""
    print("Testing Config Set...")
    
    # Test setting a config value
    result = subprocess.run(
        'python queuectl.py config set test_key "test_value"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Config set command works")
        return True
    else:
        print("  FAIL: Config set command failed")
        print(f"  Error: {result.stderr}")
        return False

def test_config_get():
    """Test getting configuration values"""
    print("Testing Config Get...")
    
    # First set a value
    subprocess.run(
        'python queuectl.py config set test_get_key "test_get_value"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    # Then get it
    result = subprocess.run(
        'python queuectl.py config get test_get_key',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "test_get_value" in result.stdout:
        print("  PASS: Config get command works")
        return True
    else:
        print("  FAIL: Config get command failed")
        return False

def test_config_list():
    """Test listing all configuration values"""
    print("Testing Config List...")
    
    # Test listing all config
    result = subprocess.run(
        "python queuectl.py config list",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  PASS: Config list command works")
        return True
    else:
        print("  FAIL: Config list command failed")
        return False

def test_config_help():
    """Test configuration help"""
    print("Testing Config Help...")
    
    result = subprocess.run(
        "python queuectl.py config --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and ("set" in result.stdout or "get" in result.stdout):
        print("  PASS: Config help available")
        return True
    else:
        print("  FAIL: Config help not working")
        return False

def test_config_persistence():
    """Test configuration persistence"""
    print("Testing Config Persistence...")
    
    # Set a unique value
    test_key = "persistence_test"
    test_value = "persistent_value_123"
    
    # Set the value
    result1 = subprocess.run(
        f'python queuectl.py config set {test_key} "{test_value}"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result1.returncode != 0:
        print("  FAIL: Could not set config value")
        return False
    
    # Get the value in a separate process
    result2 = subprocess.run(
        f'python queuectl.py config get {test_key}',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result2.returncode == 0 and test_value in result2.stdout:
        print("  PASS: Config values persist across processes")
        return True
    else:
        print("  FAIL: Config values not persisting")
        return False

def test_config_invalid_operations():
    """Test invalid configuration operations"""
    print("Testing Invalid Config Operations...")
    
    # Test getting non-existent key
    result = subprocess.run(
        "python queuectl.py config get non_existent_key_12345",
        shell=True,
        capture_output=True,
        text=True
    )
    
    # Should handle gracefully (either return empty or show not found message)
    if result.returncode == 0 or "not found" in result.stdout.lower():
        print("  PASS: Non-existent keys handled gracefully")
        return True
    else:
        print("  FAIL: Non-existent keys not handled properly")
        return False

def main():
    """Run all configuration tests"""
    print("=== Testing Configuration Management ===")
    print()
    
    tests = [
        test_config_help,
        test_config_set,
        test_config_get,
        test_config_list,
        test_config_persistence,
        test_config_invalid_operations
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
    
    print(f"Configuration Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    main()