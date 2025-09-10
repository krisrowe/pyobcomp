"""
Tests for result filtering functionality.
"""
import pytest
from pyobcomp import create, CompareProfile, FieldSettings
from pyobcomp.models import ComparisonStatus, ComparisonResult


class TestFilterResults:
    """Test result filtering functionality."""
    
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
    
    def test_level_diffs(self):
        """Test filtering to show only differences (including within tolerance)."""
        result = self.comparer.compare(self.expected_data, self.actual_data)
        
        # Filter to show only fields that are different (not identical)
        filtered_result = result.filter(ComparisonStatus.IN_TOLERANCE)
        filtered_result.fields.extend(result.filter(ComparisonStatus.OUTSIDE_TOLERANCE).fields)
        
        # Should have 2 fields: fat (outside tolerance) and carbs (in tolerance)
        assert len(filtered_result.fields) == 2
        
        # Check field names
        field_names = [f.name for f in filtered_result.fields]
        assert 'fat' in field_names
        assert 'carbs' in field_names
        assert 'protein' not in field_names
        
        # Check statuses
        fat_field = next(f for f in filtered_result.fields if f.name == 'fat')
        carbs_field = next(f for f in filtered_result.fields if f.name == 'carbs')
        
        assert fat_field.status == ComparisonStatus.OUTSIDE_TOLERANCE
        assert carbs_field.status == ComparisonStatus.IN_TOLERANCE
    
    def test_level_all(self):
        """Test filtering to show all fields."""
        result = self.comparer.compare(self.expected_data, self.actual_data)
        
        # Filter to show all fields (identical, in tolerance, outside tolerance)
        all_fields = []
        for status in [ComparisonStatus.IDENTICAL, ComparisonStatus.IN_TOLERANCE, ComparisonStatus.OUTSIDE_TOLERANCE]:
            all_fields.extend(result.filter(status).fields)
        
        filtered_result = ComparisonResult(fields=all_fields)
        
        # Should have all 3 fields
        assert len(filtered_result.fields) == 3
        
        # Check field names
        field_names = [f.name for f in filtered_result.fields]
        assert 'protein' in field_names
        assert 'fat' in field_names
        assert 'carbs' in field_names
        
        # Check statuses
        protein_field = next(f for f in filtered_result.fields if f.name == 'protein')
        fat_field = next(f for f in filtered_result.fields if f.name == 'fat')
        carbs_field = next(f for f in filtered_result.fields if f.name == 'carbs')
        
        assert protein_field.status == ComparisonStatus.IDENTICAL
        assert fat_field.status == ComparisonStatus.OUTSIDE_TOLERANCE
        assert carbs_field.status == ComparisonStatus.IN_TOLERANCE
