"""
Tests for extending profile templates programmatically.
"""

import pytest
import tempfile
import os
from pyobcomp import load_profile, create, FieldSettings
from .helpers.config import Helper


class TestExtendTemplate:
    """Test extending profile templates programmatically."""

    def setup_method(self):
        """Set up test helper."""
        self.helper = Helper()

    def test_extend_template(self):
        """Test loading a YAML template, extending it, and creating a new comparer."""
        # Load the base profile from sample file
        base_profile = load_profile("tests/samples/extend_template/base_config.yaml")
        
        # Test data that will initially fail
        expected = {
            'calories': 200,
            'protein': 25.5,
            'carbs': 30,
            'fiber': 5.0  # This field is not in the profile yet
        }
        actual = {
            'calories': 210,
            'protein': 27.0,
            'carbs': 30,  # Match the expected value
            'fiber': 6.0  # This will cause a mismatch
        }
        
        # Create comparer from base profile
        base_comparer = create(base_profile)
        
        # First comparison should fail because fiber field is not configured
        result1 = base_comparer.compare(expected, actual)
        assert result1.matches == False
        
        # Check that the failure is due to the unconfigured fiber field
        failed_fields = [f for f in result1.fields if not f.passed]
        assert len(failed_fields) > 0
        
        # Now extend the profile to handle the fiber field
        extended_profile = base_profile.model_copy()
        extended_profile.fields['fiber'] = FieldSettings(percentage=20.0)  # 20% tolerance for fiber
        
        # Create new comparer from extended profile
        extended_comparer = create(extended_profile)
        
        # Second comparison should now pass
        result2 = extended_comparer.compare(expected, actual)
        assert result2.matches == True
        
        # Verify that all fields are now handled correctly
        assert len(result2.fields) == 4  # calories, protein, carbs, fiber
        
        # Check individual field results
        calories_field = next(f for f in result2.fields if f.name == 'calories')
        assert calories_field.passed == True
        
        protein_field = next(f for f in result2.fields if f.name == 'protein')
        assert protein_field.passed == True
        
        carbs_field = next(f for f in result2.fields if f.name == 'carbs')
        assert carbs_field.passed == True
        
        fiber_field = next(f for f in result2.fields if f.name == 'fiber')
        assert fiber_field.passed == True

    def test_extend_template_with_stricter_tolerances(self):
        """Test extending a template with stricter tolerances."""
        # Create a base YAML template with lenient tolerances
        yaml_content = """
fields:
  "calories":
    percentage: 20.0
  "protein":
    percentage: 25.0

options:
  normalize_types: true
  debug: false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Load the base profile
            base_profile = load_profile(temp_file)
            
            # Test data
            expected = {'calories': 100, 'protein': 15.0}
            actual = {'calories': 110, 'protein': 18.0}  # Both within lenient tolerances
            
            # Base comparison should pass
            base_comparer = create(base_profile)
            result1 = base_comparer.compare(expected, actual)
            assert result1.matches == True
            
            # Now create a stricter version
            strict_profile = base_profile.model_copy()
            strict_profile.fields['calories'] = FieldSettings(percentage=5.0)  # Much stricter
            strict_profile.fields['protein'] = FieldSettings(percentage=10.0)  # Much stricter
            
            # Stricter comparison should fail
            strict_comparer = create(strict_profile)
            result2 = strict_comparer.compare(expected, actual)
            assert result2.matches == False
            
            # Check that both fields now fail
            failed_fields = [f for f in result2.fields if not f.passed]
            assert len(failed_fields) == 2
            
        finally:
            os.unlink(temp_file)

    def test_extend_template_with_new_behavior_rules(self):
        """Test extending a template with new behavior rules."""
        # Create a base YAML template
        yaml_content = """
fields:
  "calories":
    percentage: 10.0
  "protein":
    percentage: 10.0

options:
  normalize_types: true
  debug: false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Load the base profile
            base_profile = load_profile(temp_file)
            
            # Test data with additional fields
            expected = {
                'calories': 100,
                'protein': 15.0,
                'notes': 'Important note',
                'metadata': {'version': '1.0'}
            }
            actual = {
                'calories': 100,
                'protein': 15.0,
                'notes': 'Different note',  # This will cause issues
                'metadata': {'version': '2.0'}  # This will cause issues
            }
            
            # Base comparison should fail due to unconfigured fields
            base_comparer = create(base_profile)
            result1 = base_comparer.compare(expected, actual)
            assert result1.matches == False
            
            # Now extend the profile to handle the additional fields
            extended_profile = base_profile.model_copy()
            extended_profile.fields['notes'] = FieldSettings(ignore=True)  # Ignore notes
            extended_profile.fields['metadata'] = FieldSettings(ignore=True)  # Ignore metadata
            
            # Extended comparison should now pass
            extended_comparer = create(extended_profile)
            result2 = extended_comparer.compare(expected, actual)
            assert result2.matches == True
            
        finally:
            os.unlink(temp_file)

    def test_extend_template_modify_options(self):
        """Test extending a template by modifying global options."""
        # Create a base YAML template
        yaml_content = """
fields:
  "calories":
    percentage: 10.0

options:
  normalize_types: false
  debug: false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Load the base profile
            base_profile = load_profile(temp_file)
            
            # Test data with type differences
            expected = {'calories': 100}  # int
            actual = {'calories': 100.0}  # float
            
            # Base comparison should fail due to type mismatch
            base_comparer = create(base_profile)
            result1 = base_comparer.compare(expected, actual)
            assert result1.matches == False
            
            # Now extend the profile to enable type normalization
            extended_profile = base_profile.model_copy()
            extended_profile.options.normalize_types = True
            extended_profile.options.debug = True
            
            # Extended comparison should now pass
            extended_comparer = create(extended_profile)
            result2 = extended_comparer.compare(expected, actual)
            assert result2.matches == True
            
        finally:
            os.unlink(temp_file)