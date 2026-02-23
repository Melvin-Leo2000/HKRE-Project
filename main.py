#!/usr/bin/env python3
"""
HKRE App - Main Entry Point (Convenience Wrapper)
This file redirects to src/main.py for backward compatibility.
You can run: python src/main.py directly
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simply execute src/main.py
if __name__ == "__main__":
    import runpy
    runpy.run_path('src/main.py', run_name='__main__')

