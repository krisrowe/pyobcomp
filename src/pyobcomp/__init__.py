"""
PyObComp - Python Object Comparison Framework

A robust object comparison framework with field-level tolerance settings
and comprehensive reporting capabilities for testing and validation.
"""

from .comparer import Comparer
from .factory import ComparerFactory, load_profile, create_from_file, create
from .models import (
    ToleranceConfig, FieldConfig, FieldSettings, ComparisonOptions, 
    ComparisonResult, FullComparisonResult, FieldResult, ComparisonStatus, CompareProfile,
    LoggingConfig, LoggingLevel, LoggingFormat
)

__version__ = "0.1.0"
__author__ = "Kris Rowe"
__email__ = "krisrowe@example.com"

__all__ = [
    "Comparer",
    "ComparerFactory",
    "load_profile",
    "create_from_file", 
    "create",
    "ToleranceConfig", 
    "FieldConfig",
    "FieldSettings",
    "ComparisonOptions",
    "ComparisonResult",
    "FullComparisonResult",
    "FieldResult",
    "ComparisonStatus",
    "CompareProfile",
    "LoggingConfig",
    "LoggingLevel", 
    "LoggingFormat",
]
