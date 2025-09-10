"""
Tests for object comparison functionality using YAML configurations.

These tests load profiles and data from YAML/JSON files and test the same scenarios
as the programmatic tests, ensuring identical behavior.
"""

import pytest
from .helpers.config import Helper
from .helpers.compare import BaseCompareTests


class TestCompareWithConf(BaseCompareTests):
    """Test object comparison functionality using YAML configurations."""

    def setup_method(self):
        """Set up test helpers."""
        self.helper = Helper()

    def get_test_data(self, test_name):
        """Load profile and data from YAML files."""
        expected_data, actual_data, profile = self.helper.load_sample_files_with_profile(test_name)
        return profile, expected_data, actual_data
