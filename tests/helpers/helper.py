"""
Test helper class for common test logic using sample files.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Tuple

from pyobcomp import ComparerFactory, ComparisonResult


class Helper:
    """Helper class for loading sample files and performing comparisons."""
    
    def __init__(self, samples_dir: str = "tests/samples"):
        self.samples_dir = Path(samples_dir)
    
    def load_sample_files(self, test_case: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
        """Load YAML config and JSON files for a test case.
        
        Args:
            test_case: Name of the test case subdirectory
            
        Returns:
            Tuple of (expected_data, actual_data, config_path)
        """
        case_dir = self.samples_dir / test_case
        
        # Load expected and actual JSON files
        with open(case_dir / "expected.json", 'r') as f:
            expected_data = json.load(f)
        
        with open(case_dir / "actual.json", 'r') as f:
            actual_data = json.load(f)
        
        # Get config file path
        config_path = case_dir / "config.yaml"
        
        return expected_data, actual_data, str(config_path)
    
    def compare_with_config(self, test_case: str) -> ComparisonResult:
        """Load sample files and perform comparison using YAML config.
        
        Args:
            test_case: Name of the test case subdirectory
            
        Returns:
            ComparisonResult from the comparison
        """
        expected_data, actual_data, config_path = self.load_sample_files(test_case)
        
        # Create comparer from YAML config
        comparer = ComparerFactory.create_from_file(config_path)
        
        # Perform comparison
        return comparer.compare(expected_data, actual_data)
    
    def compare_with_profile(self, test_case: str, profile_modifier=None) -> ComparisonResult:
        """Load sample files and perform comparison using a profile object.
        
        Args:
            test_case: Name of the test case subdirectory
            profile_modifier: Optional function to modify the profile before creating comparer
            
        Returns:
            ComparisonResult from the comparison
        """
        expected_data, actual_data, config_path = self.load_sample_files(test_case)
        
        # Load profile from YAML
        profile = ComparerFactory.load_profile(config_path)
        
        # Apply modifications if provided
        if profile_modifier:
            profile = profile_modifier(profile)
        
        # Create comparer from profile
        comparer = ComparerFactory.create(profile)
        
        # Perform comparison
        return comparer.compare(expected_data, actual_data)
