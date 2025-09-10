"""
Tests for YAML configuration loading and validation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from pyobcomp import load_profile, create_from_file
from pyobcomp.models import FieldSettings, ComparisonOptions
from .helpers.config import Helper


class TestLoadYAML:
    """Test YAML configuration loading and validation."""

    def setup_method(self):
        """Set up test helper."""
        self.helper = Helper()

    def test_valid(self):
        """Test loading a valid YAML configuration."""
        # Test loading profile (this validates the YAML)
        profile = load_profile("tests/samples/valid/config.yaml")
        assert profile.fields['calories'].percentage == 5.0
        assert profile.fields['protein'].absolute == 2.0
        assert profile.fields['carbs'].required == True
        assert profile.fields['fiber'].ignore == True
        assert profile.options.normalize_types == True
        # Debug option no longer exists - use logging framework instead
        
        # Test creating comparer from file (this also validates the YAML)
        comparer = create_from_file("tests/samples/valid/config.yaml")
        assert comparer is not None

    def test_invalid(self):
        """Test loading an invalid YAML configuration that causes schema errors."""
        # Test 1: Both tolerance and behavior settings (mutually exclusive)
        with pytest.raises(ValueError, match="Field cannot have multiple behavior settings"):
            load_profile("tests/samples/invalid/config.yaml")
        
        # Test 2: Creating comparer from invalid file should also fail
        with pytest.raises(ValueError, match="Field cannot have multiple behavior settings"):
            create_from_file("tests/samples/invalid/config.yaml")
        
        # Test 3: Wrong data type
        yaml_content = """
fields:
  "calories":
    percentage: "10%"  # This should cause an error - should be number
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML configuration"):
                load_profile(temp_file)
                
        finally:
            os.unlink(temp_file)

    def test_missing_file(self):
        """Test handling of missing YAML file."""
        with pytest.raises(FileNotFoundError):
            load_profile('nonexistent.yaml')
        
        with pytest.raises(FileNotFoundError):
            create_from_file('nonexistent.yaml')

    def test_empty_yaml(self):
        """Test loading an empty YAML file."""
        yaml_content = ""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Empty YAML should create a profile with default settings
            profile = load_profile(temp_file)
            assert len(profile.fields) == 0
            assert profile.options.normalize_types == False
            # Debug option no longer exists - use logging framework instead
            
        finally:
            os.unlink(temp_file)

    def test_minimal_valid_yaml(self):
        """Test loading a minimal valid YAML configuration."""
        yaml_content = """
fields:
  "test_field":
    required: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            profile = load_profile(temp_file)
            assert len(profile.fields) == 1
            assert profile.fields['test_field'].required == True
            
        finally:
            os.unlink(temp_file)
