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
    
    def _run_comparison_and_capture_logs(self, profile, expected_data, actual_data):
        """Helper method to run comparison and capture log output."""
        comparer = create(profile)
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger("pyobcomp.comparison")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform comparison
        result = comparer.compare(expected_data, actual_data)
        
        # Get log output
        log_output = log_capture.getvalue()
        
        # Clean up
        logger.removeHandler(handler)
        
        return result, log_output
    
    def _assert_basic_headers(self, log_output):
        """Helper method to assert basic table headers are present."""
        assert "Comparison Result" in log_output, "Missing comparison result header"
        assert "Field Name" in log_output, "Missing table header"
        assert "Status" in log_output, "Missing status column"
        assert "Expected" in log_output, "Missing expected column"
        assert "Actual" in log_output, "Missing actual column"
    
    def _check_output_contains_failed_field(self, log_output):
        """Helper method to check for failed field assertions."""
        assert "value" in log_output, "Missing failed field 'value'"
        assert "10" in log_output, "Missing expected value 10"
        assert "12" in log_output, "Missing actual value 12"
        assert "fail" in log_output, "Missing fail status"
    
    def _check_output_contains_tolerated_field(self, log_output):
        """Helper method to check for tolerated field assertions."""
        assert "count" in log_output, "Missing different field 'count'"
        assert "5.0" in log_output, "Missing expected count 5.0"
        assert "5.5" in log_output, "Missing actual count 5.5"
        assert "tolerated" in log_output, "Missing tolerated status for count field"
    
    def _extract_table_content(self, log_output):
        """Helper method to extract table content (excluding headers)."""
        lines = log_output.split('\n')
        table_rows = [line for line in lines if '|' in line and 'Field Name' not in line]
        return '\n'.join(table_rows)
    
    def _assert_identical_fields_not_in_table(self, log_output, detail_type):
        """Helper method to assert identical fields are not in table content."""
        table_content = self._extract_table_content(log_output)
        assert "name" not in table_content, f"Identical field 'name' should not appear in {detail_type} detail: {table_content}"
        assert "status" not in table_content, f"Identical field 'status' should not appear in {detail_type} detail: {table_content}"
    
    @pytest.fixture
    def test_data(self):
        """Test data with both identical and different fields."""
        return {
            "expected": {
                "name": "test",
                "value": 10,
                "status": "active",
                "count": 5.0
            },
            "actual": {
                "name": "test",  # Identical
                "value": 12,     # Different (outside tolerance)
                "status": "active",  # Identical
                "count": 5.5     # Different (within tolerance)
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
        
        # Run comparison and capture logs
        result, log_output = self._run_comparison_and_capture_logs(
            profile, test_data["expected"], test_data["actual"]
        )
        
        # Check basic headers
        self._assert_basic_headers(log_output)
        
        # Must show failed fields with specific values
        self._check_output_contains_failed_field(log_output)
        
        # Count field should NOT appear in FAILURES detail (it's tolerated, not failed)
        assert "count" not in log_output, "Tolerated field 'count' should not appear in FAILURES detail"
        
        # Must NOT show identical fields in the table rows
        self._assert_identical_fields_not_in_table(log_output, "FAILURES")
    
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
        
        # Run comparison and capture logs
        result, log_output = self._run_comparison_and_capture_logs(
            profile, test_data["expected"], test_data["actual"]
        )
        
        # Check basic headers
        self._assert_basic_headers(log_output)
        
        # Must show different fields with specific values
        self._check_output_contains_failed_field(log_output)
        
        # Must show different count field (tolerated but different)
        self._check_output_contains_tolerated_field(log_output)
        
        # Must NOT show identical fields in the table rows
        self._assert_identical_fields_not_in_table(log_output, "DIFFERENCES")
    
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
        
        # Run comparison and capture logs
        result, log_output = self._run_comparison_and_capture_logs(
            profile, test_data["expected"], test_data["actual"]
        )
        
        # Check basic headers
        self._assert_basic_headers(log_output)
        
        # Must show different fields with specific values
        self._check_output_contains_failed_field(log_output)
        
        # Must show different count field (tolerated but different)
        self._check_output_contains_tolerated_field(log_output)
        
        # Must ALSO show identical fields in the table rows
        table_content = self._extract_table_content(log_output)
        assert "name" in table_content, f"Identical field 'name' should appear in ALL detail: {table_content}"
        assert "status" in table_content, f"Identical field 'status' should appear in ALL detail: {table_content}"
        assert "test" in table_content, "Identical value 'test' should appear in ALL detail"
        assert "active" in table_content, "Identical value 'active' should appear in ALL detail"
        assert "match" in table_content, "Should show 'match' status for identical fields"
