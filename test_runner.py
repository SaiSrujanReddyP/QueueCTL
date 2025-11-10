#!/usr/bin/env python3
"""
QueueCTL Test Runner - Main test command with options
"""

import sys
import os
import subprocess

def show_menu():
    """Show test menu options"""
    print("=== QueueCTL Test Suite ===")
    print()
    print("Available Tests:")
    print("1.  test_bonus_features    - Test bonus features and enhancements")
    print("2.  test_deliverables      - Test core deliverable requirements")
    print("3.  test_config            - Test configuration management")
    print("4.  test_dlq               - Test Dead Letter Queue functionality")
    print("5.  test_enqueue           - Test job enqueuing and scheduling")
    print("6.  test_list              - Test job listing and filtering")
    print("7.  test_metrics           - Test performance metrics")
    print("8.  test_status            - Test system status reporting")
    print("9.  test_dashboard         - Test web dashboard functionality")
    print("10. test_worker            - Test worker management")
    print("11. test_all               - Run all tests")
    print("12. exit                   - Exit test runner")
    print()

def run_test(test_name):
    """Run a specific test file"""
    test_file = f"tests/{test_name}.py"
    if os.path.exists(test_file):
        print(f"Running {test_name}...")
        print("=" * 50)
        result = subprocess.run([sys.executable, test_file], capture_output=False)
        print("=" * 50)
        return result.returncode == 0
    else:
        print(f"Test file {test_file} not found!")
        return False

def run_all_tests():
    """Run all available tests"""
    tests = [
        "test_bonus_features",
        "test_deliverables", 
        "test_config",
        "test_dlq",
        "test_enqueue",
        "test_list",
        "test_metrics",
        "test_status",
        "test_dashboard",
        "test_worker"
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if run_test(test):
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"Test Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        # Command line argument provided
        test_name = sys.argv[1]
        if test_name == "test_all":
            run_all_tests()
        else:
            run_test(test_name)
        return
    
    # Interactive mode
    while True:
        show_menu()
        choice = input("Select test (1-12): ").strip()
        
        if choice == "1":
            run_test("test_bonus_features")
        elif choice == "2":
            run_test("test_deliverables")
        elif choice == "3":
            run_test("test_config")
        elif choice == "4":
            run_test("test_dlq")
        elif choice == "5":
            run_test("test_enqueue")
        elif choice == "6":
            run_test("test_list")
        elif choice == "7":
            run_test("test_metrics")
        elif choice == "8":
            run_test("test_status")
        elif choice == "9":
            run_test("test_dashboard")
        elif choice == "10":
            run_test("test_worker")
        elif choice == "11":
            run_all_tests()
        elif choice == "12" or choice.lower() == "exit":
            print("Exiting test runner...")
            break
        else:
            print("Invalid choice. Please select 1-12.")
        
        print()

if __name__ == "__main__":
    main()