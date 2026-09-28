"""
Database Validation Suite Wrapper
--------------------------------
Provides compatibility for `scripts/validate_database.py` by delegating directly
to the comprehensive automated synthetic data validation suite in `scripts/validate_data.py`.
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.validate_data import main

if __name__ == "__main__":
    main()
