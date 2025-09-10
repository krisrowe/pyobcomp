"""
Pydantic models for PyObComp configuration and results.

This module contains all the data models used by PyObComp, with no dependencies
on the comparison logic to avoid circular imports.
"""

from typing import Dict, Any, Optional, List, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum
import logging


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


class LoggingLevel(str, Enum):
    """Logging levels for comparison output."""
    FAILURES = "failures"      # Only failed fields
    DIFFERENCES = "differences"  # All differences (including within tolerance)
    ALL = "all"                # All fields including identical matches


class LoggingFormat(str, Enum):
    """Output format for comparison logging."""
    TABLE = "table"            # Human-readable table format
    JSON = "json"              # JSON format for machine parsing


class LoggingConfig(BaseModel):
    """Configuration for comparison logging."""
    enabled: Optional[bool] = Field(None, description="Enable logging (None=auto-detect from logger, True/False=explicit)")
    when: Literal["never", "always", "on_fail"] = Field("on_fail", description="When to log comparisons")
    level: LoggingLevel = Field(LoggingLevel.FAILURES, description="Level of detail to log")
    format: LoggingFormat = Field(LoggingFormat.TABLE, description="Output format for logs")
    logger_name: str = Field("pyobcomp.comparison", description="Logger name to use")


class ComparisonOptions(BaseModel):
    """Global options for object comparison."""
    normalize_types: bool = Field(False, description="Handle int/float differences (9 vs 9.0)")
    debug: bool = Field(False, description="Enable debug logging")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")


class FieldResult(BaseModel):
    """Result of a single field comparison."""
    model_config = ConfigDict(use_enum_values=True)
    
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
    model_config = ConfigDict(use_enum_values=True)
    
    fields: List[FieldResult] = Field(default_factory=list, description="Individual field results")
    
    def format_table(self, detail: str = 'failures') -> str:
        """Format comparison results as a table.
        
        Args:
            detail: Level of detail ('failures', 'differences', 'all')
        """
        if not self.fields:
            return "No fields to display"
        
        # Filter fields based on detail level
        if detail == 'failures':
            # Only show fields that failed (not identical and not in tolerance)
            filtered_fields = [f for f in self.fields if f.status not in ['identical', 'in_tolerance']]
        elif detail == 'differences':
            # Show fields that are different (not identical)
            filtered_fields = [f for f in self.fields if f.status != 'identical']
        elif detail == 'all':
            # Show all fields
            filtered_fields = self.fields
        else:
            raise ValueError(f"Invalid detail level: {detail}. Must be 'failures', 'differences', or 'all'")
        
        if not filtered_fields:
            return "No fields match the specified detail level"
        
        # Create table header
        header = "Field Name          | Status     | Expected | Actual   | Reason"
        separator = "-" * len(header)
        
        # Create table rows
        rows = []
        for field in filtered_fields:
            # Truncate long values for display
            expected_str = str(field.expected)[:8] + "..." if len(str(field.expected)) > 8 else str(field.expected)
            actual_str = str(field.actual)[:8] + "..." if len(str(field.actual)) > 8 else str(field.actual)
            
            # Convert status to simpler format
            status_map = {
                'identical': 'match',
                'in_tolerance': 'tolerated',
                'outside_tolerance': 'fail',
                'type_mismatch': 'fail',
                'missing_required': 'fail',
                'optional_missing': 'tolerated',
                'list_item_missing': 'fail',
                'list_item_field_mismatch': 'fail'
            }
            simple_status = status_map.get(field.status, field.status)
            
            # Create shorter reason text
            reason_str = self._create_short_reason(field)
            
            row = f"{field.name:<18} | {simple_status:<10} | {expected_str:<8} | {actual_str:<8} | {reason_str}"
            rows.append(row)
        
        # Combine header, separator, and rows
        table_lines = [header, separator] + rows
        return "\n".join(table_lines)
    
    def _create_short_reason(self, field: 'FieldResult') -> str:
        """Create a short reason string for table display."""
        if field.status == 'identical':
            return 'exact'
        elif field.status == 'in_tolerance':
            if field.tolerance_applied:
                return f"< {field.tolerance_applied}"
            else:
                return 'tolerated'
        elif field.status == 'outside_tolerance':
            if field.tolerance_applied:
                return f"> {field.tolerance_applied}"
            else:
                return 'failed'
        elif field.status == 'type_mismatch':
            return 'type'
        elif field.status == 'missing_required':
            return 'missing'
        elif field.status == 'optional_missing':
            return 'optional'
        else:
            return field.reason[:20] + "..." if len(field.reason) > 20 else field.reason
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        import json
        return json.dumps(self.model_dump(), indent=2)
    
    def _get_filtered_fields(self, level: LoggingLevel) -> List[FieldResult]:
        """Get fields filtered by logging level."""
        if level == LoggingLevel.FAILURES:
            return [f for f in self.fields if not f.passed]
        elif level == LoggingLevel.DIFFERENCES:
            return [f for f in self.fields if f.status != ComparisonStatus.IDENTICAL]
        else:  # ALL
            return self.fields
    
    def log_result(self, logger: logging.Logger, level: LoggingLevel, format: LoggingFormat) -> None:
        """Log comparison result with specified level and format."""
        if not logger.isEnabledFor(logging.INFO):
            return
            
        filtered_fields = self._get_filtered_fields(level)
        
        if format == LoggingFormat.TABLE:
            # Use format_table for table output
            detail_map = {
                LoggingLevel.FAILURES: 'failures',
                LoggingLevel.DIFFERENCES: 'differences', 
                LoggingLevel.ALL: 'all'
            }
            output = self.format_table(detail=detail_map[level])
            logger.info(f"Comparison Result:\n{output}")
        else:  # JSON
            # Create a filtered result for JSON output
            filtered_result = ComparisonResult(fields=filtered_fields)
            logger.info(f"Comparison Result (JSON):\n{filtered_result.to_json()}")


class FullComparisonResult(ComparisonResult):
    """Complete result of an object comparison with overall status."""
    model_config = ConfigDict(use_enum_values=True)
    
    matches: bool = Field(..., description="Overall pass/fail result")
    summary: str = Field(..., description="Human-readable summary")
    
    def filter(self, status_filter: 'ComparisonStatus') -> ComparisonResult:
        """Filter results by comparison status.
        
        Args:
            status_filter: Status to filter by
            
        Returns:
            Filtered ComparisonResult with only fields matching the status
        """
        filtered_fields = [f for f in self.fields if f.status == status_filter.value]
        return ComparisonResult(fields=filtered_fields)
    
    def auto_log(self, logging_config: 'LoggingConfig') -> None:
        """Automatically log comparison result based on configuration.
        
        Args:
            logging_config: Logging configuration to use
        """
        # Check if explicitly disabled
        if logging_config.enabled is False:
            return
        
        # Get logger
        logger = logging.getLogger(logging_config.logger_name)
        
        # If enabled is None, auto-detect from logger level
        if logging_config.enabled is None:
            # Only log if logger is enabled for INFO level or higher
            if not logger.isEnabledFor(logging.INFO):
                return
        
        # Check if we should log based on 'when' setting
        should_log = False
        if logging_config.when == "always":
            should_log = True
        elif logging_config.when == "on_fail" and not self.matches:
            should_log = True
            
        if not should_log:
            return
            
        # Log the result
        self.log_result(logger, logging_config.level, logging_config.format)


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
