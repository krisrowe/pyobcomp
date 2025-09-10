"""
Tests for diff formatting functionality.
"""
import pytest
from pyobcomp import create, CompareProfile, FieldSettings
from pyobcomp.models import ComparisonStatus, ComparisonResult


class TestFormat:
    """Test diff formatting functionality."""
    
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
        
        self.comparer = create(self.profile)
    
    def test_level_fails(self):
        """Test that only failed fields are shown in output."""
        result = self.comparer.compare(self.expected_data, self.actual_data)
        output = result.format_table(detail='failures')
        
        # Should contain 'fat' (failed) but not 'protein' or 'carbs'
        assert 'fat' in output
        assert 'protein' not in output
        assert 'carbs' not in output
        
        # Verify the comparison actually failed
        assert result.matches == False
    
    def test_level_diffs(self):
        """Test that all differences (including within tolerance) are shown using filter."""
        result = self.comparer.compare(self.expected_data, self.actual_data)
        
        # Filter to show only fields that are different (not identical)
        from pyobcomp.models import ComparisonStatus
        filtered_result = result.filter(ComparisonStatus.IN_TOLERANCE)
        filtered_result.fields.extend(result.filter(ComparisonStatus.OUTSIDE_TOLERANCE).fields)
        
        output = filtered_result.format_table(detail='differences')
        
        # Should contain 'fat' (failed) and 'carbs' (different but within tolerance)
        # but not 'protein' (exact match)
        assert 'fat' in output
        assert 'carbs' in output
        assert 'protein' not in output
    
    def test_level_all(self):
        """Test that all fields are shown in output using filter."""
        result = self.comparer.compare(self.expected_data, self.actual_data)
        
        # Filter to show all fields (identical, in tolerance, outside tolerance)
        from pyobcomp.models import ComparisonStatus
        all_fields = []
        for status in [ComparisonStatus.IDENTICAL, ComparisonStatus.IN_TOLERANCE, ComparisonStatus.OUTSIDE_TOLERANCE]:
            all_fields.extend(result.filter(status).fields)
        
        filtered_result = ComparisonResult(fields=all_fields)
        output = filtered_result.format_table(detail='all')
        
        # Should contain all three field names
        assert 'protein' in output
        assert 'fat' in output
        assert 'carbs' in output
