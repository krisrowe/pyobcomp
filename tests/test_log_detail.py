"""
Tests for LoggingDetail behavior - ensuring detail level affects content but not visibility.
"""
import pytest
import logging
import io
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions, LoggingConfig, LoggingDetail, LoggingFormat


class TestLogDetail:
    """Test that LoggingDetail affects content but not visibility."""
    
    def setup_module(self):
        """Set global logging level to INFO at module start."""
        self.original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.INFO)
    
    def teardown_module(self):
        """Restore original logging level at module end."""
        logging.getLogger().setLevel(self.original_level)
    
    @pytest.fixture
    def test_data(self):
        """Test data with both identical and different fields."""
        return {
            "expected": {
                "name": "test",
                "value": 10,
                "status": "active",
                "count": 5
            },
            "actual": {
                "name": "test",  # Identical
                "value": 12,     # Different (outside tolerance)
                "status": "active",  # Identical
                "count": 3       # Different (within tolerance)
            }
        }
    
    def test_detail_failures(self, test_data):
        """Test FAILURES detail - should only show failed fields."""
        profile = CompareProfile(
            fields={
                "name": FieldSettings(percentage=0.1),
                "value": FieldSettings(absolute=1.0),
                "status": FieldSettings(percentage=0.1),
                "count": FieldSettings(absolute=1.0)
            },
            options=ComparisonOptions(
                logging=LoggingConfig(
                    enabled=True,
                    when="always",
                    detail=LoggingDetail.FAILURES,
                    format=LoggingFormat.TABLE
                    # level uses default INFO
                )
            )
        )
        
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(test_data["expected"], test_data["actual"])
        
        # Check log output
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        assert "value" in log_output  # Should show failed field
        assert "count" in log_output  # Should show failed field
        # Should not show identical fields in detail
        assert "name" not in log_output or "test" not in log_output
        assert "status" not in log_output or "active" not in log_output
        
        logger.removeHandler(handler)
    
    def test_detail_differences(self, test_data):
        """Test DIFFERENCES detail - should show all non-identical fields."""
        profile = CompareProfile(
            fields={
                "name": FieldSettings(percentage=0.1),
                "value": FieldSettings(absolute=1.0),
                "status": FieldSettings(percentage=0.1),
                "count": FieldSettings(absolute=1.0)
            },
            options=ComparisonOptions(
                logging=LoggingConfig(
                    enabled=True,
                    when="always",
                    detail=LoggingDetail.DIFFERENCES,
                    format=LoggingFormat.TABLE
                    # level uses default INFO
                )
            )
        )
        
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(test_data["expected"], test_data["actual"])
        
        # Check log output
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        assert "value" in log_output  # Should show different field
        assert "count" in log_output  # Should show different field
        # Should not show identical fields
        assert "name" not in log_output or "test" not in log_output
        assert "status" not in log_output or "active" not in log_output
        
        logger.removeHandler(handler)
    
    def test_detail_all(self, test_data):
        """Test ALL detail - should show all fields including identical ones."""
        profile = CompareProfile(
            fields={
                "name": FieldSettings(percentage=0.1),
                "value": FieldSettings(absolute=1.0),
                "status": FieldSettings(percentage=0.1),
                "count": FieldSettings(absolute=1.0)
            },
            options=ComparisonOptions(
                logging=LoggingConfig(
                    enabled=True,
                    when="always",
                    detail=LoggingDetail.ALL,
                    format=LoggingFormat.TABLE
                    # level uses default INFO
                )
            )
        )
        
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(test_data["expected"], test_data["actual"])
        
        # Check log output
        log_output = log_capture.getvalue()
        assert "Comparison Result" in log_output
        assert "value" in log_output  # Should show different field
        assert "count" in log_output  # Should show different field
        # Should also show identical fields
        assert "name" in log_output  # Should show identical field
        assert "status" in log_output  # Should show identical field
        
        logger.removeHandler(handler)
