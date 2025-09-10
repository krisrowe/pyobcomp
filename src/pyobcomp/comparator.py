"""
Main ObjectComparator class for PyObComp.
"""

from typing import Dict, Any, Optional, Union, List
import yaml
import re
from .config import ToleranceConfig, FieldConfig, ComparisonOptions, ComparisonResult, Field, ComparisonStatus


class ObjectComparator:
    """Main class for object comparison with tolerance settings."""
    
    def __init__(
        self,
        tolerances: Optional[Dict[str, Union[ToleranceConfig, FieldConfig]]] = None,
        options: Optional[ComparisonOptions] = None
    ):
        """Initialize the comparator.
        
        Args:
            tolerances: Dictionary mapping field paths to tolerance/field configs
            options: Global comparison options
        """
        self.tolerances = tolerances or {}
        self.options = options or ComparisonOptions()
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ObjectComparator':
        """Create comparator from YAML configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Configured ObjectComparator instance
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Parse fields configuration
        tolerances = {}
        if 'fields' in config:
            for field_path, field_config in config['fields'].items():
                if isinstance(field_config, dict):
                    if 'percentage' in field_config or 'absolute' in field_config:
                        # Tolerance configuration
                        tolerances[field_path] = ToleranceConfig(
                            percentage=field_config.get('percentage'),
                            absolute=field_config.get('absolute')
                        )
                    else:
                        # Field configuration
                        tolerances[field_path] = FieldConfig(
                            required=field_config.get('required', True),
                            ignore=field_config.get('ignore', False),
                            text_validation=field_config.get('text_validation', False)
                        )
        
        # Parse options
        options = ComparisonOptions()
        if 'options' in config:
            options.normalize_types = config['options'].get('normalize_types', False)
        
        return cls(tolerances=tolerances, options=options)
    
    def compare(self, expected: Any, actual: Any) -> ComparisonResult:
        """Compare two objects.
        
        Args:
            expected: Expected object
            actual: Actual object
            
        Returns:
            ComparisonResult with detailed comparison information
        """
        fields = []
        all_passed = True
        
        # Start comparison at root level
        result = self._compare_values("", expected, actual, fields)
        all_passed = result.matches
        
        return ComparisonResult(
            matches=all_passed,
            summary=f"Comparison {'passed' if all_passed else 'failed'} with {len([f for f in fields if not f.passed])} differences",
            fields=fields
        )
    
    def _compare_values(self, path: str, expected: Any, actual: Any, fields: List[Field]) -> ComparisonResult:
        """Compare two values at a specific path."""
        # Check if this field should be ignored
        field_config = self._get_field_config(path)
        if field_config and field_config.ignore:
            fields.append(Field(
                name=path or "root",
                passed=True,
                status=ComparisonStatus.IGNORED,
                expected=expected,
                actual=actual,
                reason="Field configured to ignore"
            ))
            return ComparisonResult(matches=True, summary="Field ignored", fields=[])
        
        # Handle missing values
        if expected is None and actual is None:
            fields.append(Field(
                name=path or "root",
                passed=True,
                status=ComparisonStatus.IDENTICAL,
                expected=expected,
                actual=actual,
                reason="Both values are None"
            ))
            return ComparisonResult(matches=True, summary="Both None", fields=[])
        
        if expected is None:
            if field_config and not field_config.required:
                fields.append(Field(
                    name=path or "root",
                    passed=True,
                    status=ComparisonStatus.OPTIONAL_MISSING,
                    expected=expected,
                    actual=actual,
                    reason="Optional field missing in expected"
                ))
                return ComparisonResult(matches=True, summary="Optional field missing", fields=[])
            else:
                fields.append(Field(
                    name=path or "root",
                    passed=False,
                    status=ComparisonStatus.MISSING_REQUIRED,
                    expected=expected,
                    actual=actual,
                    reason="Required field missing in expected"
                ))
                return ComparisonResult(matches=False, summary="Required field missing", fields=[])
        
        if actual is None:
            if field_config and not field_config.required:
                fields.append(Field(
                    name=path or "root",
                    passed=True,
                    status=ComparisonStatus.OPTIONAL_MISSING,
                    expected=expected,
                    actual=actual,
                    reason="Optional field missing in actual"
                ))
                return ComparisonResult(matches=True, summary="Optional field missing", fields=[])
            else:
                fields.append(Field(
                    name=path or "root",
                    passed=False,
                    status=ComparisonStatus.MISSING_REQUIRED,
                    expected=expected,
                    actual=actual,
                    reason="Required field missing in actual"
                ))
                return ComparisonResult(matches=False, summary="Required field missing", fields=[])
        
        # Type checking
        if not self._types_compatible(expected, actual):
            fields.append(Field(
                name=path or "root",
                passed=False,
                status=ComparisonStatus.TYPE_MISMATCH,
                expected=expected,
                actual=actual,
                reason=f"Type mismatch: expected {type(expected).__name__}, got {type(actual).__name__}",
                expected_type=type(expected).__name__,
                actual_type=type(actual).__name__
            ))
            return ComparisonResult(matches=False, summary="Type mismatch", fields=[])
        
        # Handle different data types
        if isinstance(expected, dict) and isinstance(actual, dict):
            return self._compare_dicts(path, expected, actual, fields)
        elif isinstance(expected, list) and isinstance(actual, list):
            return self._compare_lists(path, expected, actual, fields)
        else:
            return self._compare_primitives(path, expected, actual, fields)
    
    def _compare_dicts(self, path: str, expected: Dict, actual: Dict, fields: List[Field]) -> ComparisonResult:
        """Compare two dictionaries."""
        all_passed = True
        all_keys = set(expected.keys()) | set(actual.keys())
        
        for key in all_keys:
            key_path = f"{path}.{key}" if path else key
            exp_value = expected.get(key)
            act_value = actual.get(key)
            
            result = self._compare_values(key_path, exp_value, act_value, fields)
            if not result.matches:
                all_passed = False
        
        return ComparisonResult(matches=all_passed, summary="Dict comparison", fields=[])
    
    def _compare_lists(self, path: str, expected: List, actual: List, fields: List[Field]) -> ComparisonResult:
        """Compare two lists."""
        all_passed = True
        
        if len(expected) != len(actual):
            fields.append(Field(
                name=f"{path}.length" if path else "length",
                passed=False,
                status=ComparisonStatus.ARRAY_LENGTH_MISMATCH,
                expected=len(expected),
                actual=len(actual),
                reason=f"Array length mismatch: expected {len(expected)}, got {len(actual)}"
            ))
            all_passed = False
        else:
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                result = self._compare_values(item_path, exp_item, act_item, fields)
                if not result.matches:
                    all_passed = False
        
        return ComparisonResult(matches=all_passed, summary="List comparison", fields=[])
    
    def _compare_primitives(self, path: str, expected: Any, actual: Any, fields: List[Field]) -> ComparisonResult:
        """Compare primitive values (numbers, strings, booleans)."""
        # Check for exact match first
        if expected == actual:
            fields.append(Field(
                name=path or "root",
                passed=True,
                status=ComparisonStatus.IDENTICAL,
                expected=expected,
                actual=actual,
                reason="Values match exactly"
            ))
            return ComparisonResult(matches=True, summary="Exact match", fields=[])
        
        # Check if this is a numerical comparison with tolerance
        if self._is_numerical(expected) and self._is_numerical(actual):
            return self._compare_numerical_with_tolerance(path, expected, actual, fields)
        
        # Check for text validation
        field_config = self._get_field_config(path)
        if field_config and field_config.text_validation:
            # For text validation, only check that actual is not empty
            if actual and str(actual).strip():
                fields.append(Field(
                    name=path or "root",
                    passed=True,
                    status=ComparisonStatus.IN_TOLERANCE,
                    expected=expected,
                    actual=actual,
                    reason="Text validation passed (non-empty)"
                ))
                return ComparisonResult(matches=True, summary="Text validation passed", fields=[])
            else:
                fields.append(Field(
                    name=path or "root",
                    passed=False,
                    status=ComparisonStatus.OUTSIDE_TOLERANCE,
                    expected=expected,
                    actual=actual,
                    reason="Text validation failed (empty or None)"
                ))
                return ComparisonResult(matches=False, summary="Text validation failed", fields=[])
        
        # Default: exact match required
        fields.append(Field(
            name=path or "root",
            passed=False,
            status=ComparisonStatus.VALUE_MISMATCH,
            expected=expected,
            actual=actual,
            reason=f"Value mismatch: expected {expected}, got {actual}"
        ))
        return ComparisonResult(matches=False, summary="Value mismatch", fields=[])
    
    def _compare_numerical_with_tolerance(self, path: str, expected: float, actual: float, fields: List[Field]) -> ComparisonResult:
        """Compare numerical values with tolerance settings."""
        field_config = self._get_field_config(path)
        
        if not field_config or not isinstance(field_config, ToleranceConfig):
            # No tolerance configured, require exact match
            fields.append(Field(
                name=path or "root",
                passed=False,
                status=ComparisonStatus.VALUE_MISMATCH,
                expected=expected,
                actual=actual,
                reason=f"Value mismatch: expected {expected}, got {actual} (no tolerance configured)"
            ))
            return ComparisonResult(matches=False, summary="Value mismatch", fields=[])
        
        # Calculate tolerances
        percentage_tolerance = None
        absolute_tolerance = None
        
        if field_config.percentage is not None:
            percentage_tolerance = abs(expected * field_config.percentage / 100.0)
        
        if field_config.absolute is not None:
            absolute_tolerance = field_config.absolute
        
        # Determine which tolerance to use (whichever is greater)
        tolerance = None
        tolerance_type = None
        
        if percentage_tolerance is not None and absolute_tolerance is not None:
            if percentage_tolerance >= absolute_tolerance:
                tolerance = percentage_tolerance
                tolerance_type = f"{field_config.percentage}%"
            else:
                tolerance = absolute_tolerance
                tolerance_type = f"{field_config.absolute} absolute"
        elif percentage_tolerance is not None:
            tolerance = percentage_tolerance
            tolerance_type = f"{field_config.percentage}%"
        elif absolute_tolerance is not None:
            tolerance = absolute_tolerance
            tolerance_type = f"{field_config.absolute} absolute"
        
        if tolerance is None:
            # No tolerance configured
            fields.append(Field(
                name=path or "root",
                passed=False,
                status=ComparisonStatus.VALUE_MISMATCH,
                expected=expected,
                actual=actual,
                reason=f"Value mismatch: expected {expected}, got {actual} (no tolerance configured)"
            ))
            return ComparisonResult(matches=False, summary="Value mismatch", fields=[])
        
        # Check if within tolerance
        difference = abs(expected - actual)
        if difference <= tolerance:
            fields.append(Field(
                name=path or "root",
                passed=True,
                status=ComparisonStatus.IN_TOLERANCE,
                expected=expected,
                actual=actual,
                reason=f"Within tolerance ({tolerance_type})",
                tolerance_applied=tolerance_type
            ))
            return ComparisonResult(matches=True, summary="Within tolerance", fields=[])
        else:
            fields.append(Field(
                name=path or "root",
                passed=False,
                status=ComparisonStatus.OUTSIDE_TOLERANCE,
                expected=expected,
                actual=actual,
                reason=f"Outside tolerance ({tolerance_type}): difference {difference:.2f} > tolerance {tolerance:.2f}",
                tolerance_applied=tolerance_type
            ))
            return ComparisonResult(matches=False, summary="Outside tolerance", fields=[])
    
    def _get_field_config(self, path: str) -> Optional[Union[ToleranceConfig, FieldConfig]]:
        """Get field configuration for a given path."""
        # Direct match first
        if path in self.tolerances:
            return self.tolerances[path]
        
        # Try wildcard matching
        for pattern, config in self.tolerances.items():
            if self._path_matches_pattern(path, pattern):
                return config
        
        return None
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a field path matches a pattern with wildcards."""
        # Convert pattern to regex
        # Replace * with .* for wildcard matching
        regex_pattern = pattern.replace('*', '.*')
        regex_pattern = regex_pattern.replace('.', r'\.')  # Escape dots
        regex_pattern = regex_pattern.replace(r'\.*', '.*')  # Fix wildcard after escaped dot
        
        try:
            return bool(re.match(f"^{regex_pattern}$", path))
        except re.error:
            return False
    
    def _types_compatible(self, expected: Any, actual: Any) -> bool:
        """Check if two values have compatible types."""
        if type(expected) == type(actual):
            return True
        
        # Handle type normalization
        if self.options.normalize_types:
            # Check for int/float compatibility
            if self._is_numerical(expected) and self._is_numerical(actual):
                return True
            
            # Check for string compatibility
            if isinstance(expected, str) and isinstance(actual, str):
                return True
        
        return False
    
    def _is_numerical(self, value: Any) -> bool:
        """Check if a value is numerical."""
        return isinstance(value, (int, float)) and not isinstance(value, bool)




