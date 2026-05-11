#!/usr/bin/env python3
"""
ApiForge - Command Line Interface
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_forge import main

if __name__ == '__main__':
    main()
