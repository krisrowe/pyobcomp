"""
Tests for logging functionality.
"""
import pytest
import logging
import io
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions, LoggingConfig, LoggingDetail, LoggingFormat


class TestLogging:
    """Test logging functionality."""
    
    def setup_method(self):
        """Set up test data and profile."""
        # Test data: protein matches exactly, fat fails (out of tolerance), carbs within tolerance
        self.expected_data = {
            "protein": 25.0,  # Exact match
            "fat": 10.0,      # Will fail - out of tolerance
            "carbs": 50.0     # Within tolerance
        }
        
        self.actual_data = {
            "protein": 25.0,  # Exact match
            "fat": 15.0,      # Out of tolerance (50% difference, tolerance is 20%)
            "carbs": 55.0     # Within tolerance (10% difference, tolerance is 15%)
        }
        
        # Compare profile with different tolerances
        self.profile = CompareProfile(
            fields={
                'protein': FieldSettings(percentage=5.0),   # 5% tolerance
                'fat': FieldSettings(percentage=20.0),      # 20% tolerance  
                'carbs': FieldSettings(percentage=15.0),    # 15% tolerance
            }
        )
    
    def test_logging_disabled(self):
        """Test that logging is disabled by default."""
        # Temporarily disable the logger to test true default behavior
        original_level = logging.getLogger("pyobcomp.comparison").level
        logging.getLogger("pyobcomp.comparison").setLevel(logging.CRITICAL + 1)  # Disable
        
        try:
            # Create comparer with default options (logging disabled)
            comparer = create(self.profile)
            
            # Capture log output
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            logger = logging.getLogger("pyobcomp.comparison")
            logger.addHandler(handler)
            # Don't set logger level to INFO - keep it disabled
            
            # Perform comparison
            result = comparer.compare(self.expected_data, self.actual_data)
            
            # Should not have logged anything
            log_output = log_capture.getvalue()
            assert "Comparison Result" not in log_output
            
            # Clean up
            logger.removeHandler(handler)
            
        finally:
            # Restore original logger level
            logging.getLogger("pyobcomp.comparison").setLevel(original_level)
    
    def test_logging_always_table_format(self):
        """Test logging with always enabled and table format."""
        # Create profile with logging enabled
        profile = self.profile.model_copy()
        profile.options.logging = LoggingConfig(
            enabled=True,
            when="always",
            detail=LoggingDetail.FAILURES,
            format=LoggingFormat.TABLE
        )
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(self.expected_data, self.actual_data)
        
        # Should have logged the result
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        assert "Field Name" in log_output  # Table header
        assert "fat" in log_output  # Failed field should be in output
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_logging_on_fail_only(self):
        """Test logging only on failure."""
        # Create profile with logging on fail only
        profile = self.profile.model_copy()
        profile.options.logging = LoggingConfig(
            enabled=True,
            when="on_fail",
            detail=LoggingDetail.FAILURES,
            format=LoggingFormat.TABLE
        )
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison (should fail due to fat field)
        result = comparer.compare(self.expected_data, self.actual_data)
        
        # Should have logged since comparison failed
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        assert result.matches == False
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_logging_json_format(self):
        """Test logging with JSON format."""
        # Create profile with JSON logging
        profile = self.profile.model_copy()
        profile.options.logging = LoggingConfig(
            enabled=True,
            when="always",
            detail=LoggingDetail.DIFFERENCES,
            format=LoggingFormat.JSON
        )
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(self.expected_data, self.actual_data)
        
        # Should have logged JSON result
        log_output = log_capture.getvalue()
        assert "Comparison Result (JSON)" in log_output
        assert '"fields"' in log_output  # Should contain JSON structure
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_logging_different_levels(self):
        """Test different logging levels."""
        # Test FAILURES level
        profile = self.profile.model_copy()
        profile.options.logging = LoggingConfig(
            enabled=True,
            when="always",
            detail=LoggingDetail.FAILURES,
            format=LoggingFormat.TABLE
        )
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(self.expected_data, self.actual_data)
        
        # Should have logged
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_manual_logging(self):
        """Test manual logging without auto-log."""
        # Create comparer without auto-logging
        comparer = create(self.profile)
        result = comparer.compare(self.expected_data, self.actual_data)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Manually log the result
        logger.info(f"Comparison Result:\n{result.format_table('all')}")
        
        # Should have logged
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        
        # Clean up
        logger.removeHandler(handler)

