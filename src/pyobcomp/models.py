"""
Pydantic models for PyObComp configuration and results.

This module contains all the data models used by PyObComp, with no dependencies
on the comparison logic to avoid circular imports.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
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


class ToleranceConfig(BaseModel):
    """Configuration for numerical tolerance settings."""
    percentage: Optional[float] = Field(None, ge=0, description="Percentage tolerance (0-100)")
    absolute: Optional[float] = Field(None, ge=0, description="Absolute tolerance")
    
    @field_validator('percentage', 'absolute')
    @classmethod
    def at_least_one_tolerance(cls, v, info):
        if v is None and not any(info.data.values()):
            raise ValueError("At least one tolerance (percentage or absolute) must be specified")
        return v


class FieldConfig(BaseModel):
    """Configuration for field behavior settings."""
    required: bool = Field(True, description="Field must be present and match exactly")
    ignore: bool = Field(False, description="Skip field entirely during comparison")
    text_validation: bool = Field(False, description="Only check that field is not empty")
    
    @field_validator('ignore', 'text_validation')
    @classmethod
    def mutually_exclusive_with_required(cls, v, info):
        if v and info.data.get('required', True):
            raise ValueError("Field cannot be both ignored/text-validated and required")
        return v
    
    @field_validator('ignore', 'text_validation')
    @classmethod
    def mutually_exclusive_with_each_other(cls, v, info):
        if v and info.data.get('text_validation', False):
            raise ValueError("Field cannot be both ignored and text-validated")
        return v


class ComparisonOptions(BaseModel):
    """Global options for object comparison."""
    normalize_types: bool = Field(False, description="Handle int/float differences (9 vs 9.0)")
    debug: bool = Field(False, description="Enable debug logging")


class FieldResult(BaseModel):
    """Result of a single field comparison."""
    name: str = Field(..., description="Field path (e.g., 'items[0].nutrition.calories')")
    passed: bool = Field(..., description="Simple pass/fail boolean")
    status: ComparisonStatus = Field(..., description="Detailed status enum")
    expected: Any = Field(..., description="Expected value")
    actual: Any = Field(..., description="Actual value")
    reason: str = Field(..., description="Human-readable reason")
    tolerance_applied: Optional[str] = Field(None, description="Tolerance that was applied")
    expected_type: Optional[str] = Field(None, description="Expected value type")
    actual_type: Optional[str] = Field(None, description="Actual value type")


class ComparisonResult(BaseModel):
    """Base result class for filtered comparison results."""
    fields: List[FieldResult] = Field(default_factory=list, description="Individual field results")
    
    def format_table(self, detail: str = 'failures') -> str:
        """Format comparison results as a table.
        
        Args:
            detail: Level of detail ('failures', 'differences', 'all')
        """
        # TODO: Implement table formatting
        return f"Comparison result: {len(self.fields)} fields"


class FullComparisonResult(ComparisonResult):
    """Complete result of an object comparison with overall status."""
    matches: bool = Field(..., description="Overall pass/fail result")
    summary: str = Field(..., description="Human-readable summary")
    
    def filter(self, status_filter: 'ComparisonStatus') -> ComparisonResult:
        """Filter results by comparison status.
        
        Args:
            status_filter: Status to filter by
            
        Returns:
            Filtered ComparisonResult with only fields matching the status
        """
        filtered_fields = [f for f in self.fields if f.status == status_filter]
        return ComparisonResult(fields=filtered_fields)


class FieldSettings(BaseModel):
    """Settings for a specific field pattern."""
    # Tolerance settings (mutually exclusive with behavior settings)
    percentage: Optional[float] = Field(None, ge=0, description="Percentage tolerance")
    absolute: Optional[float] = Field(None, ge=0, description="Absolute tolerance")
    
    # Behavior settings (mutually exclusive with tolerance settings)
    required: Optional[bool] = Field(None, description="Must match exactly")
    ignore: Optional[bool] = Field(None, description="Skip field entirely")
    text_validation: Optional[bool] = Field(None, description="Only check not empty")
    
    @field_validator('percentage', 'absolute')
    @classmethod
    def tolerance_settings(cls, v, info):
        """Ensure tolerance settings are valid."""
        # This validator runs for each field individually, so we can't check other fields here
        # The mutual exclusivity check will be done in the model_validator
        return v
    
    @field_validator('required', 'ignore', 'text_validation')
    @classmethod
    def behavior_settings(cls, v, info):
        """Ensure behavior settings are mutually exclusive with tolerance settings."""
        # This validator runs for each field individually, so we can't check other fields here
        # The mutual exclusivity check will be done in the model_validator
        return v
    
    @model_validator(mode='after')
    def validate_field_settings(self):
        """Validate the complete field settings."""
        percentage = self.percentage
        absolute = self.absolute
        required = self.required
        ignore = self.ignore
        text_validation = self.text_validation
        
        # Check if we have tolerance settings (any tolerance field with non-None value)
        has_tolerance = percentage is not None or absolute is not None
        # Check if we have behavior settings (any behavior field with non-None value)
        has_behavior = required is not None or ignore is not None or text_validation is not None
        
        if has_tolerance and has_behavior:
            raise ValueError("Field cannot have both tolerance settings and behavior settings")
        
        # Check for mutual exclusivity within behavior settings
        behavior_count = sum(1 for x in [required, ignore, text_validation] if x is not None)
        if behavior_count > 1:
            raise ValueError("Field cannot have multiple behavior settings (required, ignore, text_validation)")
        
        # If tolerance fields are specified, at least one must have a non-None value
        # This only applies when tolerance fields are explicitly provided in YAML but both are None
        # We can't easily detect this at the model level, so we'll handle it in the factory
        
        return self


class CompareProfile(BaseModel):
    """Complete comparison profile that mirrors YAML schema."""
    fields: Dict[str, FieldSettings] = Field(default_factory=dict, description="Field-specific settings")
    options: ComparisonOptions = Field(default_factory=ComparisonOptions, description="Global options")
    
    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True  # Validate on assignment
    )
