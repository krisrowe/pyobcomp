"""
Tests for object comparison functionality.
"""

import pytest
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions
from pyobcomp.models import ComparisonStatus
from .helpers.helper import Helper


class TestCompare:
    """Test object comparison functionality."""

    def setup_method(self):
        """Set up test helper."""
        self.helper = Helper()

    def test_absolute_tolerance(self):
        """Test absolute tolerance comparison."""
        result = self.helper.compare_with_config("absolute_tolerance")
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IN_TOLERANCE

    def test_percent_tolerance(self):
        """Test percentage tolerance comparison."""
        result = self.helper.compare_with_config("percentage_tolerance")
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IN_TOLERANCE

    def test_field_not_required(self):
        """Test optional field handling."""
        profile = CompareProfile(
            fields={
                'calories': FieldSettings(required=True),
                'protein': FieldSettings(required=False),  # Optional field
                'fiber': FieldSettings(required=False),    # Optional field
            }
        )
        comparer = create(profile)
        
        expected = {'calories': 100, 'protein': 15.0, 'fiber': 5.0}
        actual = {'calories': 100}  # Missing optional fields
        
        result = comparer.compare(expected, actual)
        assert result.matches == True
        assert len(result.fields) == 3
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IDENTICAL
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.OPTIONAL_MISSING
        
        fiber_field = next(f for f in result.fields if f.name == 'fiber')
        assert fiber_field.passed == True
        assert fiber_field.status == ComparisonStatus.OPTIONAL_MISSING

    def test_field_required(self):
        """Test required field handling."""
        profile = CompareProfile(
            fields={
                'calories': FieldSettings(required=True),
                'protein': FieldSettings(required=True),
            }
        )
        comparer = create(profile)
        
        expected = {'calories': 100, 'protein': 15.0}
        actual = {'calories': 100}  # Missing required field
        
        result = comparer.compare(expected, actual)
        assert result.matches == False
        assert len(result.fields) == 2
        
        # Check individual field results
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IDENTICAL
        
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == False
        assert protein_field.status == ComparisonStatus.MISSING_REQUIRED

    def test_list_item_missing(self):
        """Test missing list item handling."""
        result = self.helper.compare_with_config("list_items")
        assert result.matches == True  # Should pass with the sample data
        
        # Test with missing item by creating a custom comparison
        profile = CompareProfile(
            fields={
                'items.*.calories': FieldSettings(percentage=10.0),
                'items.*.protein': FieldSettings(percentage=10.0),
            }
        )
        comparer = create(profile)
        
        expected = {
            'items': [
                {'calories': 100, 'protein': 15.0},
                {'calories': 200, 'protein': 25.0}
            ]
        }
        actual = {
            'items': [
                {'calories': 100, 'protein': 15.0}
                # Missing second item
            ]
        }
        
        result = comparer.compare(expected, actual)
        assert result.matches == False
        
        # Should have failures for missing list item
        failed_fields = [f for f in result.fields if not f.passed]
        assert len(failed_fields) > 0
        
        # Check that we have failures related to missing list items
        missing_item_fields = [f for f in failed_fields if 'items[1]' in f.name]
        assert len(missing_item_fields) > 0

    def test_list_item_field_mismatch(self):
        """Test field mismatch within list items."""
        result = self.helper.compare_with_config("list_items")
        assert result.matches == True  # Should pass with the sample data
        
        # Test with field mismatch by creating a custom comparison
        profile = CompareProfile(
            fields={
                'items.*.calories': FieldSettings(percentage=10.0),
                'items.*.protein': FieldSettings(percentage=10.0),
            }
        )
        comparer = create(profile)
        
        expected = {
            'items': [
                {'calories': 100, 'protein': 15.0},
                {'calories': 200, 'protein': 25.0}
            ]
        }
        actual = {
            'items': [
                {'calories': 100, 'protein': 15.0},
                {'calories': 250, 'protein': 25.0}  # calories outside tolerance
            ]
        }
        
        result = comparer.compare(expected, actual)
        assert result.matches == False
        
        # Should have exactly one failure for the calories field in the second item
        failed_fields = [f for f in result.fields if not f.passed]
        assert len(failed_fields) == 1
        
        failed_field = failed_fields[0]
        assert failed_field.name == 'items[1].calories'
        assert failed_field.status == ComparisonStatus.OUTSIDE_TOLERANCE

    def test_deep_nested_mismatch(self):
        """Test mismatch on a field within an object within an object."""
        result = self.helper.compare_with_config("deep_nested")
        assert result.matches == False  # Should fail with the sample data
        
        # Should have exactly one failure for the vitamin_c field
        failed_fields = [f for f in result.fields if not f.passed]
        assert len(failed_fields) == 1
        
        failed_field = failed_fields[0]
        assert failed_field.name == 'nutrition.vitamins.vitamin_c'
        assert failed_field.status == ComparisonStatus.VALUE_MISMATCH

    def test_mixed_tolerances(self):
        """Test mixed tolerances where one field passes by absolute but fails by percentage, and vice versa."""
        result = self.helper.compare_with_config("mixed_tolerances")
        assert result.matches == True
        assert len(result.fields) == 2
        
        # Both fields should pass because we use the more permissive tolerance
        field1_result = next(f for f in result.fields if f.name == 'calories')
        assert field1_result.passed == True
        assert field1_result.status == ComparisonStatus.IN_TOLERANCE
        
        field2_result = next(f for f in result.fields if f.name == 'protein')
        assert field2_result.passed == True
        assert field2_result.status == ComparisonStatus.IN_TOLERANCE

    def test_ignore_fields(self):
        """Test ignoring fields completely."""
        result = self.helper.compare_with_config("ignore_fields")
        assert result.matches == True
        
        # Should have results for all fields
        assert len(result.fields) == 4
        
        # Check calories field
        calories_field = next(f for f in result.fields if f.name == 'calories')
        assert calories_field.passed == True
        assert calories_field.status == ComparisonStatus.IN_TOLERANCE
        
        # Check ignored fields
        protein_field = next(f for f in result.fields if f.name == 'protein')
        assert protein_field.passed == True
        assert protein_field.status == ComparisonStatus.IGNORED
        
        sodium_field = next(f for f in result.fields if f.name == 'sodium')
        assert sodium_field.passed == True
        assert sodium_field.status == ComparisonStatus.IGNORED

    def test_text_validation(self):
        """Test text validation (only check not empty)."""
        result = self.helper.compare_with_config("text_validation")
        assert result.matches == True
        
        # Both fields should pass because they're both non-empty
        name_field = next(f for f in result.fields if f.name == 'name')
        assert name_field.passed == True
        assert name_field.status == ComparisonStatus.IDENTICAL
        
        description_field = next(f for f in result.fields if f.name == 'description')
        assert description_field.passed == True
        assert description_field.status == ComparisonStatus.IDENTICAL