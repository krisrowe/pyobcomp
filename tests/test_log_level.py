"""
Tests for logging level behavior - ensuring comparisons respect global logging levels.
"""
import pytest
import logging
import io
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions, LoggingConfig, LoggingDetail, LoggingFormat

# Module-level flag to track if default logging test passed
_default_logging_works = None

# Constants for log output checking
COMPARISON_RESULT_MARKER = "Comparison Result"
FAILED_FIELD_MARKER = "protein_grams"  # Field name that should fail in our test
EXPECTED_VALUE_MARKER = "10"            # Expected value in our test
ACTUAL_VALUE_MARKER = "12"              # Actual value in our test


class TestLogLevel:
    """Test that comparisons respect global logging levels."""
    
    def setup_module(self):
        """Set global logging level to WARNING at module start."""
        self.original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.WARNING)
    
    def teardown_module(self):
        """Restore original logging level at module end."""
        logging.getLogger().setLevel(self.original_level)
    
    @pytest.fixture
    def profile(self):
        """Create a basic comparison profile with default logging."""
        return CompareProfile(
            fields={
                "name": FieldSettings(percentage=0.1),
                "protein_grams": FieldSettings(absolute=1.0)
            }
        )
    
    def _test_logging_level(self, global_level, should_show_logs, profile):
        """Helper method to test logging behavior at a specific level."""
        # Temporarily set global logging level
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(global_level)
        logger = None
        handler = None
        
        try:
            # Use provided profile
            comparer = create(profile)
            
            # Capture log output
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setLevel(global_level)
            logger = logging.getLogger("pyobcomp.comparison")
            logger.addHandler(handler)
            logger.setLevel(global_level)
            
            # Perform comparison that should fail
            result = comparer.compare(
                {"name": "test", "protein_grams": 10},
                {"name": "test", "protein_grams": 12}  # Different value
            )
            
            # Check log output based on expectation
            log_output = log_capture.getvalue()
            if should_show_logs:
                assert COMPARISON_RESULT_MARKER in log_output
                assert FAILED_FIELD_MARKER in log_output  # Should show the failed field
                assert EXPECTED_VALUE_MARKER in log_output  # Should show expected value
                assert ACTUAL_VALUE_MARKER in log_output    # Should show actual value
            else:
                assert COMPARISON_RESULT_MARKER not in log_output
            
        finally:
            # Restore original level
            logging.getLogger().setLevel(original_level)
            if logger and handler:
                logger.removeHandler(handler)
    
    def test_lib_uses_correct_default_log_level(self, profile):
        """Test that pyobcomp uses INFO level by default with no configuration."""
        global _default_logging_works
        
        # Temporarily set to INFO to show INFO-level logs
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.INFO)
        logger = None
        handler = None
        
        try:
            # Use default profile with no logging configuration
            comparer = create(profile)
            
            # Capture log output
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setLevel(logging.INFO)
            logger = logging.getLogger("pyobcomp.comparison")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            # Perform comparison that should fail
            result = comparer.compare(
                {"name": "test", "protein_grams": 10},
                {"name": "test", "protein_grams": 12}  # Different value
            )
            
            # Check that comparison was logged at INFO level (default)
            log_output = log_capture.getvalue()
            _default_logging_works = (
                COMPARISON_RESULT_MARKER in log_output and 
                FAILED_FIELD_MARKER in log_output and
                EXPECTED_VALUE_MARKER in log_output and
                ACTUAL_VALUE_MARKER in log_output
            )
            
            if not _default_logging_works:
                pytest.fail("Default logging level test failed - pyobcomp not using INFO level by default")
            
        finally:
            # Restore original level
            logging.getLogger().setLevel(original_level)
            if logger and handler:
                logger.removeHandler(handler)
    
    def test_level_info_shows(self, profile):
        """Test that INFO level shows INFO-level comparison logs."""
        if _default_logging_works is False:
            pytest.skip("Default logging test failed - skipping remaining tests")
        
        self._test_logging_level(logging.INFO, should_show_logs=True, profile=profile)
    
    def test_level_debug_shows(self, profile):
        """Test that DEBUG level shows INFO-level comparison logs."""
        if _default_logging_works is False:
            pytest.skip("Default logging test failed - skipping remaining tests")
        
        self._test_logging_level(logging.DEBUG, should_show_logs=True, profile=profile)
    
    def test_level_warning_no_show(self, profile):
        """Test with WARNING level - should NOT show comparisons."""
        if _default_logging_works is False:
            pytest.skip("Default logging test failed - skipping remaining tests")
        
        self._test_logging_level(logging.WARNING, should_show_logs=False, profile=profile)
    
    def test_no_output_by_default(self, profile):
        """Test that no output goes to logs by default without adjusting global logging level."""
        # Don't adjust global logging level - use whatever it is by default
        # Create comparer with default profile
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        # Don't set logger level - use default
        
        # Perform comparison that should fail
        result = comparer.compare(
            {"name": "test", "protein_grams": 10},
            {"name": "test", "protein_grams": 12}  # Different value
        )
        
        # Should NOT have logged anything by default
        log_output = log_capture.getvalue()
        assert COMPARISON_RESULT_MARKER not in log_output
        
        # Clean up
        logger.removeHandler(handler)
