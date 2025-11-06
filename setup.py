#!/usr/bin/env python3
"""
Setup script for QueueCTL
"""

import subprocess
import sys
import os


def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(" Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Failed to install requirements: {e}")
        return False


def make_executable():
    """Make queuectl.py executable"""
    try:
        os.chmod("queuectl.py", 0o755)
        print(" Made queuectl.py executable")
        return True
    except Exception as e:
        print(f" Failed to make executable: {e}")
        return False


def test_installation():
    """Test the installation"""
    print("\nTesting installation...")
    try:
        result = subprocess.run([sys.executable, "queuectl.py", "--help"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(" QueueCTL is working correctly")
            return True
        else:
            print(f" QueueCTL test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f" Installation test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("QueueCTL Setup")
    print("=" * 30)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Make executable
    if not make_executable():
        success = False
    
    # Test installation
    if not test_installation():
        success = False
    
    print("\n" + "=" * 30)
    if success:
        print(" Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python queuectl.py --help")
        print("2. Try the demo: python demo.py")
        print("3. Run tests: python test_queuectl.py")
    else:
        print(" Setup failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())