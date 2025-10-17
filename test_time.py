"""
Time Validation Script for GDP Analytics
=========================================

This script tests and validates the time functions to ensure proper time handling.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timezone
import time

# Import our time utilities
from app import get_current_time, get_current_utc_time, format_timestamp

def test_time_functions():
    """Test all time-related functions."""
    print("=" * 60)
    print("GDP Analytics - Time Function Validation")
    print("=" * 60)
    
    # Test current time functions
    local_time = get_current_time()
    utc_time = get_current_utc_time()
    
    print(f"Local Time: {local_time}")
    print(f"UTC Time: {utc_time}")
    print(f"Local Time Formatted: {format_timestamp(local_time)}")
    print(f"UTC Time Formatted: {format_timestamp(utc_time)}")
    
    # Test time difference
    time_diff = abs((local_time - utc_time).total_seconds() / 3600)
    print(f"Time Difference (hours): {time_diff:.2f}")
    
    # Test response time calculation
    start = time.time()
    time.sleep(0.1)  # Simulate 100ms processing
    end = time.time()
    response_time = (end - start) * 1000
    print(f"Response Time Test: {response_time:.2f}ms (should be ~100ms)")
    
    # Test logging timestamp format
    import logging
    
    # Create a test log entry
    test_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create a log record
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=1,
        msg='Test log message',
        args=(),
        exc_info=None
    )
    
    formatted_log = test_formatter.format(record)
    print(f"Log Format Test: {formatted_log}")
    
    print("=" * 60)
    print("Time validation completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_time_functions()