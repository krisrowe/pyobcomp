"""
PyObComp - Python Object Comparison Framework

A robust object comparison framework with field-level tolerance settings
and comprehensive reporting capabilities for testing and validation.
"""

from .comparator import ObjectComparator
from .config import ToleranceConfig, FieldConfig, ComparisonOptions
from .result import ComparisonResult, Field, ComparisonStatus

__version__ = "0.1.0"
__author__ = "Kris Rowe"
__email__ = "krisrowe@example.com"

__all__ = [
    "ObjectComparator",
    "ToleranceConfig", 
    "FieldConfig",
    "ComparisonOptions",
    "ComparisonResult",
    "Field",
    "ComparisonStatus",
]
