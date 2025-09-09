"""
Tests for ObjectComparator.
"""

import pytest
from pyobcomp import ObjectComparator, ToleranceConfig, FieldConfig


class TestObjectComparator:
    """Test cases for ObjectComparator."""
    
    def test_initialization(self):
        """Test basic initialization."""
        comparator = ObjectComparator()
        assert comparator.tolerances == {}
        assert comparator.options.normalize_types is False
        assert comparator.options.debug is False
    
    def test_initialization_with_tolerances(self):
        """Test initialization with tolerances."""
        tolerances = {
            'calories': ToleranceConfig(percentage=10.0),
            'protein': ToleranceConfig(percentage=10.0, absolute=2.0),
        }
        comparator = ObjectComparator(tolerances=tolerances)
        assert comparator.tolerances == tolerances
    
    def test_compare_not_implemented(self):
        """Test that compare method returns placeholder result."""
        comparator = ObjectComparator()
        result = comparator.compare({'a': 1}, {'a': 1})
        
        assert result.matches is True
        assert "not yet implemented" in result.summary
        assert result.fields == []
    
    def test_from_yaml_not_implemented(self):
        """Test that from_yaml method returns placeholder comparator."""
        # This will fail until we implement YAML loading
        with pytest.raises(FileNotFoundError):
            ObjectComparator.from_yaml('nonexistent.yaml')
