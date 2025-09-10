#!/usr/bin/env python3
"""
Example demonstrating pyobcomp logging functionality.

This example shows how to configure and use automatic comparison logging
in your application.
"""

import logging
from pyobcomp import (
    create, CompareProfile, FieldSettings, ComparisonOptions, 
    LoggingConfig, LoggingLevel, LoggingFormat
)

def setup_logging():
    """Set up logging configuration for the example."""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure pyobcomp logger specifically
    pyobcomp_logger = logging.getLogger("pyobcomp.comparison")
    pyobcomp_logger.setLevel(logging.INFO)

def example_basic_logging():
    """Example of basic logging configuration."""
    print("=== Basic Logging Example ===")
    
    # Create a comparison profile
    profile = CompareProfile(
        fields={
            'calories': FieldSettings(percentage=10.0),
            'protein': FieldSettings(absolute=2.0),
            'fat': FieldSettings(percentage=15.0),
        }
    )
    
    # Configure logging to log only failures
    logging_config = LoggingConfig(
        enabled=True,
        when="on_fail",  # Only log when comparison fails
        level=LoggingLevel.FAILURES,
        format=LoggingFormat.TABLE
    )
    
    options = ComparisonOptions(logging=logging_config)
    comparer = create(profile, options=options)
    
    # Test data
    expected = {"calories": 200, "protein": 25.0, "fat": 10.0}
    actual = {"calories": 220, "protein": 26.5, "fat": 12.0}  # fat will fail
    
    print("Performing comparison with logging enabled...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()

def example_always_log_json():
    """Example of always logging with JSON format."""
    print("=== Always Log JSON Example ===")
    
    # Create a comparison profile
    profile = CompareProfile(
        fields={
            'calories': FieldSettings(percentage=10.0),
            'protein': FieldSettings(absolute=2.0),
        }
    )
    
    # Configure logging to always log in JSON format
    logging_config = LoggingConfig(
        enabled=True,
        when="always",
        level=LoggingLevel.DIFFERENCES,
        format=LoggingFormat.JSON
    )
    
    options = ComparisonOptions(logging=logging_config)
    comparer = create(profile, options=options)
    
    # Test data
    expected = {"calories": 200, "protein": 25.0}
    actual = {"calories": 195, "protein": 26.0}  # Both within tolerance
    
    print("Performing comparison with JSON logging...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()

def example_manual_logging():
    """Example of manual logging control."""
    print("=== Manual Logging Example ===")
    
    # Create a comparison profile without auto-logging
    profile = CompareProfile(
        fields={
            'calories': FieldSettings(percentage=5.0),
            'protein': FieldSettings(absolute=1.0),
        }
    )
    
    comparer = create(profile)  # No logging config
    
    # Test data
    expected = {"calories": 200, "protein": 25.0}
    actual = {"calories": 210, "protein": 26.5}  # Both will fail
    
    print("Performing comparison without auto-logging...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    
    # Manually log with custom settings
    logger = logging.getLogger("pyobcomp.comparison")
    print("Manually logging all fields in table format:")
    result.log_result(logger, LoggingLevel.ALL, LoggingFormat.TABLE)
    print()

def example_different_loggers():
    """Example using different logger names."""
    print("=== Different Logger Names Example ===")
    
    # Create a custom logger
    custom_logger = logging.getLogger("myapp.comparisons")
    custom_logger.setLevel(logging.INFO)
    
    # Create a comparison profile with custom logger
    profile = CompareProfile(
        fields={
            'calories': FieldSettings(percentage=10.0),
        }
    )
    
    logging_config = LoggingConfig(
        enabled=True,
        when="always",
        level=LoggingLevel.ALL,
        format=LoggingFormat.TABLE,
        logger_name="myapp.comparisons"  # Custom logger name
    )
    
    options = ComparisonOptions(logging=logging_config)
    comparer = create(profile, options=options)
    
    # Test data
    expected = {"calories": 200}
    actual = {"calories": 200}  # Exact match
    
    print("Performing comparison with custom logger...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()

if __name__ == "__main__":
    setup_logging()
    
    example_basic_logging()
    example_always_log_json()
    example_manual_logging()
    example_different_loggers()
    
    print("All examples completed!")

