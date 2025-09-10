"""
Common comparison test logic shared between test modules.

This module contains reusable test methods that can be used by both
YAML-based tests and manual tests that create profiles programmatically.
"""

import pytest
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions
from pyobcomp.models import ComparisonStatus


class BaseCompareTests:
    """Base class containing all comparison test methods."""
    
    def get_test_data(self, test_name):
        """Override this method in subclasses to provide profile and data."""
        raise NotImplementedError("Subclasses must implement get_test_data")
    
    @pytest.fixture(autouse=True)
    def test_data(self, request):
        """Automatically inject test data for each test method."""
        test_name = request.function.__name__.replace('test_', '')
        
        # Handle name mapping for tests that don't match data keys
        name_mapping = {
            'percent_tolerance': 'percentage_tolerance',
            'deep_nested_mismatch': 'deep_nested',
        }
        
        mapped_name = name_mapping.get(test_name, test_name)
        return self.get_test_data(mapped_name)
    
    def test_absolute_tolerance(self, test_data):
        """Test absolute tolerance comparison."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IN_TOLERANCE.value
    
    def test_percent_tolerance(self, test_data):
        """Test percentage tolerance comparison."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IN_TOLERANCE.value
    
    def test_field_not_required(self, test_data):
        """Test optional field handling."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 3
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IDENTICAL.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.OPTIONAL_MISSING.value
        
        fiber_field = next(f for f in result.fields if f.name == 'fiber')
        assert fiber_field.passed == True
        assert fiber_field.status == ComparisonStatus.OPTIONAL_MISSING.value
    
    def test_field_required(self, test_data):
        """Test required field handling."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == False
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IDENTICAL.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == False
        assert protein_field.status == ComparisonStatus.MISSING_REQUIRED.value
    
    def test_list_item_missing(self, test_data):
        """Test missing list item handling."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == False
        assert len(result.fields) == 4
        
        # Check the array length mismatch
        length_field = next(f for f in result.fields if f.name == 'items.length')
        assert length_field.passed == False
        assert length_field.status == ComparisonStatus.ARRAY_LENGTH_MISMATCH.value
    
    def test_list_item_field_mismatch(self, test_data):
        """Test field mismatch within list items."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == False
        assert len(result.fields) == 4
        
        # Check the field mismatch
        calories_field = next(f for f in result.fields if f.name == 'items[1].calories')
        assert calories_field.passed == False
        assert calories_field.status == ComparisonStatus.OUTSIDE_TOLERANCE.value
    
    def test_deep_nested_mismatch(self, test_data):
        """Test mismatch on a field within an object within an object."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == False
        assert len(result.fields) == 3
        
        # Check the deep nested field
        vitamin_c_field = next(f for f in result.fields if f.name == 'nutrition.vitamins.vitamin_c')
        assert vitamin_c_field.passed == False
        assert vitamin_c_field.status == ComparisonStatus.VALUE_MISMATCH.value
    
    def test_mixed_tolerances(self, test_data):
        """Test mixed tolerances where one field passes by absolute but fails by percentage, and vice versa."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IN_TOLERANCE.value
    
    def test_ignore_fields(self, test_data):
        """Test ignoring fields completely."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 4
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE.value
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IGNORED.value
        
        sodium_field = next(f for f in result.fields if f.name == 'sodium')
        assert sodium_field.passed == True
        assert sodium_field.status == ComparisonStatus.IGNORED.value
        
        carbs_field = next(f for f in result.fields if f.name == 'carbs')
        assert carbs_field.passed == True
        assert carbs_field.status == ComparisonStatus.IDENTICAL.value
    
    def test_text_validation(self, test_data):
        """Test text validation (only check not empty)."""
        profile, expected_data, actual_data = test_data
        comparer = create(profile)
        result = comparer.compare(expected_data, actual_data)
        
        assert result.matches == True
        assert len(result.fields) == 3
        
        # Check individual field results
        name_field = next(f for f in result.fields if f.name == 'name')
        assert name_field.passed == True
        assert name_field.status in [ComparisonStatus.IDENTICAL.value, ComparisonStatus.IN_TOLERANCE.value]
        
        description_field = next(f for f in result.fields if f.name == 'description')
        assert description_field.passed == True
        assert description_field.status in [ComparisonStatus.IDENTICAL.value, ComparisonStatus.IN_TOLERANCE.value]