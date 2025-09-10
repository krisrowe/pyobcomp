"""
Test helper class for common test logic using sample files.
"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple

from pyobcomp import load_profile


class Helper:
    """Helper class for loading sample files and performing comparisons."""
    
    def __init__(self, samples_dir: str = "tests/samples"):
        self.samples_dir = Path(samples_dir)
    
    def _load_sample_files(self, test_case: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
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
    
    def load_sample_files_with_profile(self, test_case: str) -> Tuple[Dict[str, Any], Dict[str, Any], Any]:
        """Load YAML config, JSON files, and profile for a test case.
        
        Args:
            test_case: Name of the test case subdirectory
            
        Returns:
            Tuple of (expected_data, actual_data, profile)
        """
        expected_data, actual_data, config_path = self._load_sample_files(test_case)
        profile = load_profile(config_path)
        return expected_data, actual_data, profile
    
