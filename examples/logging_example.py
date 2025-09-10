#!/usr/bin/env python3
"""
Example demonstrating pyobcomp logging functionality.

This example shows how to configure and use automatic comparison logging
in your application.
"""

import logging
from pyobcomp import (
    create, CompareProfile, FieldSettings, ComparisonOptions, 
    LoggingConfig, LoggingLevel, LoggingFormat, enable_logging
)

def setup_logging():
    """Set up logging configuration for the example.
    
    NOTE: This setup is REQUIRED for logging to work, even when using auto_log.
    The Python logging system must be configured before any logging can occur.
    """
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure pyobcomp logger specifically
    pyobcomp_logger = logging.getLogger("pyobcomp.comparison")
    pyobcomp_logger.setLevel(logging.INFO)

def example_silent_by_default():
    """Example showing that logging is silent by default."""
    print("=== Silent By Default Example ===")
    
    # Temporarily disable the logger to show true default behavior
    original_level = logging.getLogger("pyobcomp.comparison").level
    logging.getLogger("pyobcomp.comparison").setLevel(logging.CRITICAL + 1)  # Disable
    
    try:
        # Create a comparison profile (no logging configuration)
        profile = CompareProfile(
            fields={
                'calories': FieldSettings(percentage=10.0),
                'protein': FieldSettings(absolute=2.0),
            }
        )
        
        comparer = create(profile)
        
        # Test data that will fail
        expected = {"calories": 200, "protein": 25.0}
        actual = {"calories": 220, "protein": 28.0}  # Both will fail
        
        print("Performing comparison WITHOUT any logging configuration...")
        print("(This should produce NO log output)")
        result = comparer.compare(expected, actual)
        print(f"Comparison result: {result.matches}")
        print("Notice: No log output appeared above!")
        print()
        
    finally:
        # Restore original logger level
        logging.getLogger("pyobcomp.comparison").setLevel(original_level)

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
    
    # Set logging config on the profile
    profile.options.logging = logging_config
    comparer = create(profile)
    
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
    
    # Set logging config on the profile
    profile.options.logging = logging_config
    comparer = create(profile)
    
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
    logger.info(f"Comparison Result:\n{result.format_table('all')}")
    print()

def example_logger_based_logging():
    """Example of logger-based logging (new approach)."""
    print("=== Logger-Based Logging Example ===")
    
    # Method 1: Use convenience function
    print("Method 1: Using enable_logging() convenience function")
    enable_logging(level=logging.INFO, when="on_fail", format="table")
    
    # Create a comparison profile (no explicit logging config needed)
    profile = CompareProfile(
        fields={
            'calories': FieldSettings(percentage=10.0),
            'protein': FieldSettings(absolute=2.0),
        }
    )
    
    comparer = create(profile)
    
    # Test data that will fail
    expected = {"calories": 200, "protein": 25.0}
    actual = {"calories": 220, "protein": 28.0}  # Both will fail
    
    print("Performing comparison with auto-logging...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()
    
    # Method 2: Direct logger configuration
    print("Method 2: Direct logger configuration")
    logging.getLogger("pyobcomp.comparison").setLevel(logging.INFO)
    
    # Test data that will pass
    expected2 = {"calories": 200, "protein": 25.0}
    actual2 = {"calories": 205, "protein": 26.0}  # Within tolerance
    
    print("Performing comparison with auto-logging (should not log since it passes)...")
    result2 = comparer.compare(expected2, actual2)
    print(f"Comparison result: {result2.matches}")
    print()

def example_table_output():
    """Example demonstrating table output functionality."""
    print("=== Table Output Example ===")
    
    # Create a comparison profile
    profile = CompareProfile(
        fields={
            'protein': FieldSettings(percentage=5.0),   # 5% tolerance
            'fat': FieldSettings(percentage=20.0),      # 20% tolerance  
            'carbs': FieldSettings(percentage=15.0),    # 15% tolerance
        }
    )
    
    comparer = create(profile)
    
    # Test data: protein matches exactly, fat fails (out of tolerance), carbs within tolerance
    expected = {"protein": 25.0, "fat": 10.0, "carbs": 50.0}
    actual = {"protein": 25.0, "fat": 15.0, "carbs": 55.0}  # fat will fail, carbs within tolerance
    
    print("Performing comparison...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()
    
    # Show different table output levels
    print("1. FAILURES ONLY (only failed fields):")
    print(result.format_table('failures'))
    print()
    
    print("2. DIFFERENCES (all non-identical fields):")
    from pyobcomp.models import ComparisonStatus
    filtered_result = result.filter(ComparisonStatus.IN_TOLERANCE)
    filtered_result.fields.extend(result.filter(ComparisonStatus.OUTSIDE_TOLERANCE).fields)
    print(filtered_result.format_table('differences'))
    print()
    
    print("3. ALL FIELDS (everything):")
    all_fields = []
    for status in [ComparisonStatus.IDENTICAL, ComparisonStatus.IN_TOLERANCE, ComparisonStatus.OUTSIDE_TOLERANCE]:
        all_fields.extend(result.filter(status).fields)
    from pyobcomp.models import ComparisonResult
    all_result = ComparisonResult(fields=all_fields)
    print(all_result.format_table('all'))
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
    
    # Set logging config on the profile
    profile.options.logging = logging_config
    comparer = create(profile)
    
    # Test data
    expected = {"calories": 200}
    actual = {"calories": 200}  # Exact match
    
    print("Performing comparison with custom logger...")
    result = comparer.compare(expected, actual)
    print(f"Comparison result: {result.matches}")
    print()

if __name__ == "__main__":
    setup_logging()
    
    example_silent_by_default()
    example_basic_logging()
    example_always_log_json()
    example_manual_logging()
    example_logger_based_logging()
    example_table_output()
    example_different_loggers()
    
    print("All examples completed!")

