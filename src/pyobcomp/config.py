"""
Configuration models for PyObComp.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
from enum import Enum


class ComparisonStatus(Enum):
    """Status levels for field comparisons."""
    # Pass states
    IDENTICAL = "identical"           # Exact match
    IN_TOLERANCE = "in_tolerance"     # Within configured tolerance
    IGNORED = "ignored"               # Field configured to ignore
    OPTIONAL_MISSING = "optional_missing"  # Optional field missing
    
    # Fail states  
    OUTSIDE_TOLERANCE = "outside_tolerance"  # Outside configured tolerance
    MISSING_REQUIRED = "missing_required"    # Required field missing
    TYPE_MISMATCH = "type_mismatch"          # Type difference (int vs str, etc.)
    VALUE_MISMATCH = "value_mismatch"        # Value difference (exact match required)
    OBJECT_MISSING = "object_missing"        # Entire object missing
    ARRAY_LENGTH_MISMATCH = "array_length_mismatch"  # Array length differs


@dataclass
class ToleranceConfig:
    """Configuration for numerical tolerance settings."""
    percentage: Optional[float] = None
    absolute: Optional[float] = None
    
    def __post_init__(self):
        if self.percentage is None and self.absolute is None:
            raise ValueError("At least one tolerance (percentage or absolute) must be specified")
        if self.percentage is not None and self.percentage < 0:
            raise ValueError("Percentage tolerance must be non-negative")
        if self.absolute is not None and self.absolute < 0:
            raise ValueError("Absolute tolerance must be non-negative")


@dataclass
class FieldConfig:
    """Configuration for field behavior settings."""
    required: bool = True
    ignore: bool = False
    text_validation: bool = False
    
    def __post_init__(self):
        if self.ignore and self.text_validation:
            raise ValueError("Field cannot be both ignored and text-validated")
        if self.ignore and self.required:
            raise ValueError("Field cannot be both ignored and required")


@dataclass
class ComparisonOptions:
    """Global options for object comparison."""
    normalize_types: bool = False
    debug: bool = False


@dataclass
class Field:
    """Result of a single field comparison."""
    name: str
    passed: bool
    status: ComparisonStatus
    expected: Any
    actual: Any
    reason: str
    tolerance_applied: Optional[str] = None
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None


@dataclass
class ComparisonResult:
    """Result of an object comparison."""
    matches: bool
    summary: str
    fields: list[Field]
    
    def format_table(self, detail: str = 'failures') -> str:
        """Format comparison results as a table.
        
        Args:
            detail: Level of detail ('failures', 'differences', 'all')
        """
        # TODO: Implement table formatting
        return f"Comparison result: {self.summary}"
