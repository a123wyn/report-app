#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    print("Starting Report Generator...")
    
    # Change to app directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Activate virtual environment and run app
    if os.path.exists('venv'):
        if sys.platform == 'win32':
            python_path = 'venv/Scripts/python'
        else:
            python_path = 'venv/bin/python'
    else:
        python_path = 'python3'
    
    try:
        subprocess.run([python_path, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
