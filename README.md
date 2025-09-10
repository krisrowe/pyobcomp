# PyObComp

**Python Object Comparison Framework**

A robust object comparison framework with field-level tolerance settings and comprehensive reporting capabilities for testing and validation.

## Overview

The PyObComp framework provides sophisticated comparison capabilities for complex nested objects, particularly useful for validating generated responses against expected data. It supports:

- **Field-level tolerance settings** for numerical comparisons
- **Flexible tolerance types** (percentage, absolute, or both)
- **Status-based reporting** for different types of differences
- **Configurable field handling** (ignore, require, optional)
- **Rich difference reporting** with detailed explanations
- **Standalone usage** - no dependencies on other frameworks

## Installation

```bash
pip install pyobcomp
```

## Hello World (YAML Configuration)

The easiest way to get started is with a YAML configuration file:

**1. Create a configuration file (`config.yaml`):**
```yaml
fields:
  calories:
    percentage: 10.0
  protein:
    percentage: 10.0
    absolute: 2.0
  verified_calculation:
    required: true
  source_notes:
    ignore: true

options:
  normalize_types: true
```

**2. Use it in your Python code:**
```python
from pyobcomp import create_from_file

# Create comparer directly from YAML file
comparer = create_from_file('config.yaml')

# Compare your objects
expected = {"calories": 200, "protein": 15.0, "verified_calculation": True}
actual = {"calories": 190, "protein": 14.0, "verified_calculation": True}

result = comparer.compare(expected, actual)

if result.matches:
    print("✅ Objects match within tolerances!")
else:
    print(f"❌ Differences found: {result.summary}")
    for field in result.fields:
        if not field.passed:
            print(f"  - {field.name}: {field.reason}")
```

## Usage Examples

### YAML Configuration (Recommended)

Create a comparison rule set using YAML configuration:

**1. Create a configuration file (`nutrition_config.yaml`):**
```yaml
fields:
  calories:
    percentage: 10.0
  protein:
    percentage: 10.0
    absolute: 2.0
  verified_calculation:
    required: true
  source_notes:
    ignore: true

options:
  normalize_types: true
```

**2. Use it in your Python code:**
```python
from pyobcomp import create_from_file

# Create comparer from YAML configuration
comparer = create_from_file('nutrition_config.yaml')

# Compare objects
expected = {"calories": 200, "protein": 15.0, "verified_calculation": True}
actual = {"calories": 190, "protein": 14.0, "verified_calculation": True}

result = comparer.compare(expected, actual)

if result.matches:
    print("✅ Objects match within tolerances!")
else:
    print(f"❌ Differences found: {result.summary}")
    print(result.format_table(detail='failures'))  # Show only failures
```

### Python Code Configuration

For programmatic configuration, build the comparison rule set directly in code:

```python
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions

# Create a comparison rule set
profile = CompareProfile(
    fields={
        'calories': FieldSettings(percentage=10.0),  # 10% tolerance
        'protein': FieldSettings(percentage=10.0, absolute=2.0),  # 10% or 2.0, whichever is greater
        'verified_calculation': FieldSettings(required=True),  # Must match exactly
        'source_notes': FieldSettings(ignore=True),  # Ignore text fields
    },
    options=ComparisonOptions(normalize_types=True)  # Handle 9 vs 9.0, 2.0 vs 2
)

# Create comparer from rule set
comparer = create(profile)

# Compare objects (same as above)
result = comparer.compare(expected, actual)
```

## Core Concepts

### Tolerance Types

#### Percentage Tolerance
Allows a percentage-based variance from the expected value.

**YAML Configuration:**
```yaml
fields:
  calories:
    percentage: 10.0  # 10% tolerance
```

**Python Code:**
```python
FieldSettings(percentage=10.0)  # 10% tolerance
# Expected: 100, Actual: 95 → PASS (within 10%)
# Expected: 100, Actual: 85 → FAIL (outside 10%)
```

#### Absolute Tolerance
Allows a fixed absolute difference from the expected value.

**YAML Configuration:**
```yaml
fields:
  protein:
    absolute: 2.0  # 2.0 absolute tolerance
```

**Python Code:**
```python
FieldSettings(absolute=2.0)  # 2.0 absolute tolerance
# Expected: 100, Actual: 102 → PASS (within 2.0)
# Expected: 100, Actual: 103 → FAIL (outside 2.0)
```

#### Combined Tolerance
Uses whichever tolerance is greater (more permissive).

**YAML Configuration:**
```yaml
fields:
  protein:
    percentage: 10.0
    absolute: 2.0  # Uses whichever is greater
```

**Python Code:**
```python
FieldSettings(percentage=10.0, absolute=2.0)
# For 100: 10% = 10, absolute = 2.0 → uses 10 (more permissive)
# For 5: 10% = 0.5, absolute = 2.0 → uses 2.0 (more permissive)
```

### Field Configuration

Fields can be configured with different behaviors in your comparison rule set:

**YAML Configuration:**
```yaml
fields:
  # Tolerance settings (for numerical comparisons)
  calories:
    percentage: 10.0  # 10% tolerance
  protein:
    absolute: 2.0     # 2.0 absolute tolerance
  carbs:
    percentage: 10.0
    absolute: 2.0     # Combined tolerance
  
  # Behavior settings (for field presence/validation)
  verified_calculation:
    required: true    # Must match exactly
  source_notes:
    required: false   # Optional field
  internal_id:
    ignore: true      # Skip field entirely
  description:
    text_validation: true  # Only check not empty
```

**Python Code:**
```python
from pyobcomp import FieldSettings

# Tolerance settings (for numerical comparisons)
FieldSettings(percentage=10.0)  # 10% tolerance
FieldSettings(absolute=2.0)     # 2.0 absolute tolerance
FieldSettings(percentage=10.0, absolute=2.0)  # Combined tolerance

# Behavior settings (for field presence/validation)
FieldSettings(required=True)        # Must match exactly
FieldSettings(required=False)       # Optional field
FieldSettings(ignore=True)          # Skip field entirely
FieldSettings(text_validation=True) # Only check not empty
```

#### Ignore Fields
Fields that are completely ignored during comparison.

**YAML:**
```yaml
fields:
  internal_id:
    ignore: true
```

**Python:**
```python
FieldSettings(ignore=True)
```

#### Required Fields
Fields that must be present and match exactly (default behavior).

**YAML:**
```yaml
fields:
  verified_calculation:
    required: true
```

**Python:**
```python
FieldSettings(required=True)
```

#### Optional Fields
Fields that are compared if present but don't cause failure if missing.

**YAML:**
```yaml
fields:
  source_notes:
    required: false
```

**Python:**
```python
FieldSettings(required=False)
```

#### Text Field Handling
Special handling for text fields that only require non-empty values.

**YAML:**
```yaml
fields:
  description:
    text_validation: true
```

**Python:**
```python
FieldSettings(text_validation=True)  # Only checks not None/empty
```

### Type Normalization
Handle common type differences where values are logically equal.

**YAML Configuration:**
```yaml
fields:
  calories:
    percentage: 10.0
  protein:
    absolute: 2.0

options:
  normalize_types: true  # 9 == 9.0, 2.0 == 2
```

**Python Code:**
```python
# Enable type normalization for int/float differences
profile = CompareProfile(
    fields={...},
    options=ComparisonOptions(normalize_types=True)  # 9 == 9.0, 2.0 == 2
)
comparer = create(profile)
```

### Status Levels

Differences are categorized by status in your comparison results:

- **fail**: Critical differences that cause comparison failure
- **tolerated**: Differences that are within acceptable tolerances  
- **match**: Fields that match exactly (only shown in 'all' detail level)


## Logging and Output

PyObComp provides comprehensive logging and output capabilities for debugging and monitoring comparisons.

### Automatic Logging

Configure automatic logging that happens during comparison in your comparison rule set:

**YAML Configuration:**
```yaml
fields:
  calories:
    percentage: 10.0
  protein:
    absolute: 2.0

options:
  logging:
    enabled: true
    when: "on_fail"        # Only log when comparison fails
    level: "failures"      # Only show failed fields
    format: "table"        # Human-readable table format
```

**Python Code:**
```python
from pyobcomp import create, CompareProfile, FieldSettings, LoggingConfig, LoggingLevel, LoggingFormat

# Create comparison rule set with logging enabled
profile = CompareProfile(
    fields={
        'calories': FieldSettings(percentage=10.0),
        'protein': FieldSettings(absolute=2.0),
    },
    options=ComparisonOptions(
        logging=LoggingConfig(
            enabled=True,
            when="on_fail",  # Only log when comparison fails
            level=LoggingLevel.FAILURES,  # Only show failed fields
            format=LoggingFormat.TABLE  # Human-readable table format
        )
    )
)

comparer = create(profile)
result = comparer.compare(expected, actual)  # Will auto-log if fails
```

### Logger-Based Logging

Use the standard Python logging system for more control:

```python
import logging
from pyobcomp import enable_logging

# Method 1: Use convenience function
enable_logging(level=logging.INFO, when="on_fail", format="table")

# Method 2: Configure logger directly
logger = logging.getLogger("pyobcomp.comparison")
logger.setLevel(logging.INFO)

# Create comparison rule set (no explicit logging config needed)
profile = CompareProfile(fields={'calories': FieldSettings(percentage=10.0)})
comparer = create(profile)

# Comparisons will auto-log based on logger configuration
result = comparer.compare(expected, actual)
```

**enable_logging() Function:**
```python
from pyobcomp import enable_logging

# Configure logging for all comparisons
enable_logging(
    level=logging.INFO,    # Python logging level
    when="on_fail",        # When to log ("always" or "on_fail")
    format="table"         # Output format ("table" or "json")
)
```

### Manual Logging

Control logging manually for custom scenarios:

```python
# Create comparison rule set without auto-logging
profile = CompareProfile(fields={'calories': FieldSettings(percentage=10.0)})
comparer = create(profile)

result = comparer.compare(expected, actual)

# Manually log with custom settings
logger = logging.getLogger("myapp.comparisons")
logger.info(f"Comparison Result (JSON):\n{result.to_json()}")
```

### Table Output

Format results as clean, readable tables:

```python
# Different detail levels
print("Failures only:")
print(result.format_table('failures'))

print("All differences:")
print(result.format_table('differences'))

print("Everything:")
print(result.format_table('all'))
```

**Table Output Example:**
```
Field Name          | Status     | Expected | Actual   | Reason
---------------------------------------------------------------
calories            | fail       | 200      | 230      | > 10.0%
protein             | tolerated  | 25.0     | 26.5     | < 2.0 absolute
verified_calculation | fail       | True     | False    | exact
```

### Logging Configuration Options

**LoggingConfig:**
- `enabled: Optional[bool]` - Enable logging (None=auto-detect from logger)
- `when: "never" | "always" | "on_fail"` - When to log
- `level: LoggingLevel` - Detail level (FAILURES, DIFFERENCES, ALL)
- `format: LoggingFormat` - Output format (TABLE, JSON)
- `logger_name: str` - Logger name to use

**LoggingLevel:**
- `FAILURES` - Only failed fields
- `DIFFERENCES` - All differences (including within tolerance)
- `ALL` - All fields including identical matches

## Declarative Configuration

Instead of defining tolerances in code, you can use YAML configuration files:

### Configuration File

```yaml
# comparison_config.yaml
fields:
  # Nutritional values with specific tolerances
  "items.*.nutrition.calories": 
    percentage: 10.0
  "items.*.nutrition.protein": 
    percentage: 10.0
    absolute: 2.0
  "items.*.nutrition.carbs": 
    percentage: 10.0
    absolute: 2.0
  "items.*.nutrition.fat": 
    percentage: 10.0
    absolute: 2.0
  
  # Consumed nutrition with same tolerances
  "items.*.consumed.nutrition.calories": 
    percentage: 10.0
  "items.*.consumed.nutrition.protein": 
    percentage: 10.0
    absolute: 2.0
  
  # Totals with same tolerances
  "totals.calories": 
    percentage: 10.0
  "totals.protein": 
    percentage: 10.0
    absolute: 2.0
  
  # Critical fields - must match exactly
  "items.*.verified_calculation": 
    required: true
  "verified_calculation": 
    required: true
  
  # Text fields - only check they're not empty
  "items.*.food_name": 
    text_validation: true
  "items.*.user_description": 
    text_validation: true
  
  # Optional fields - missing is OK
  "items.*.confidence": 
    required: false
  "items.*.fiber": 
    required: false
  
  # Ignore fields that vary but don't matter
  "items.*.source_notes": 
    ignore: true
  "meta.time": 
    ignore: true
  "meta.provider": 
    ignore: true
  "meta": 
    required: false

options:
  normalize_types: true
  logging:
    enabled: true
    when: "on_fail"
    level: "failures"
    format: "table"
    logger_name: "pyobcomp.comparison"
```

### Using Declarative Configuration

```python
from pyobcomp import create_from_file

# Create comparer directly from YAML
comparer = create_from_file('comparison_config.yaml')

# Use normally
result = comparer.compare(expected, actual)
```

### Advanced Configuration with CompareProfile

```python
from pyobcomp import load_profile, create, CompareProfile, FieldSettings

# Load comparison rule set and modify programmatically
profile = load_profile('comparison_config.yaml')

# Enable debug logging via Python logging framework
import logging
logging.getLogger("pyobcomp.comparison").setLevel(logging.DEBUG)

# Create comparer from modified rule set
comparer = create(profile)
```

### Comparison Rule Set Template Extension

A powerful pattern is to load a base comparison rule set template and extend it programmatically for specific test scenarios:

```python
from pyobcomp import load_profile, create, FieldSettings

# Load base nutritional analysis rule set
base_profile = load_profile('nutrition_base.yaml')

# Create a strict version for critical tests
strict_profile = base_profile.model_copy()
strict_profile.fields.update({
    'items.*.nutrition.calories': FieldSettings(percentage=5.0),  # Stricter tolerance
    'items.*.nutrition.protein': FieldSettings(percentage=5.0, absolute=1.0),
    'items.*.verified_calculation': FieldSettings(required=True),  # Must be verified
})
# Enable debug logging for strict tests
import logging
logging.getLogger("pyobcomp.comparison").setLevel(logging.DEBUG)

# Create a lenient version for exploratory tests
lenient_profile = base_profile.model_copy()
lenient_profile.fields.update({
    'items.*.nutrition.calories': FieldSettings(percentage=20.0),  # More lenient
    'items.*.nutrition.protein': FieldSettings(percentage=25.0, absolute=5.0),
    'items.*.confidence': FieldSettings(ignore=True),  # Ignore confidence scores
    'meta.*': FieldSettings(ignore=True),  # Ignore all metadata
})
lenient_profile.options.normalize_types = True

# Create comparers for different test scenarios
strict_comparer = create(strict_profile)
lenient_comparer = create(lenient_profile)

# Use in different test contexts
def test_critical_nutrition_data():
    result = strict_comparer.compare(expected, actual)
    assert result.matches, f"Critical test failed: {result.summary}"

def test_exploratory_analysis():
    result = lenient_comparer.compare(expected, actual)
    # More permissive - just log differences
    if not result.matches:
        print(f"Differences found: {result.summary}")
```

**Base Comparison Rule Set Template (`nutrition_base.yaml`):**
```yaml
fields:
  # Standard nutritional tolerances
  "items.*.nutrition.calories": 
    percentage: 10.0
  "items.*.nutrition.protein": 
    percentage: 10.0
    absolute: 2.0
  "items.*.nutrition.carbs": 
    percentage: 10.0
    absolute: 2.0
  "items.*.nutrition.fat": 
    percentage: 10.0
    absolute: 2.0
  
  # Text fields
  "items.*.food_name": 
    text_validation: true
  "items.*.user_description": 
    text_validation: true
  
  # Optional fields
  "items.*.confidence": 
    required: false
  "items.*.fiber": 
    required: false

options:
  normalize_types: true
```

### Configuration Schema

The configuration follows this schema:

```yaml
fields:
  "field_path_pattern": 
    # Tolerance settings (mutually exclusive with behavior settings)
    percentage: float    # Optional: percentage tolerance
    absolute: float      # Optional: absolute tolerance
    
    # Behavior settings (mutually exclusive with tolerance settings)
    required: bool       # Must match exactly (default: true)
    ignore: bool         # Skip field entirely (default: false)
    text_validation: bool # Only check not empty (default: false)

options:
  normalize_types: bool  # Handle 9 vs 9.0 (default: false)
  logging:              # Logging configuration
    enabled: bool       # Enable logging (default: false)
    when: string        # When to log: "never", "always", "on_fail" (default: "on_fail")
    level: string       # Detail level: "failures", "differences", "all" (default: "failures")
    format: string      # Output format: "table", "json" (default: "table")
    logger_name: string # Logger name (default: "pyobcomp.comparison")
```

**Field Configuration Rules:**
- **Tolerance fields**: `percentage`, `absolute` (for numerical comparisons)
- **Behavior fields**: `required`, `ignore`, `text_validation` (for field handling)
- **Mutually exclusive**: A field can have either tolerance settings OR behavior settings, not both
- **Default behavior**: Fields without configuration are `required: true` (exact match)
- **Required field**: `required: true` = Must match exactly
- **Optional field**: `required: false` = Missing is OK

### Benefits of Declarative Configuration

- **Version Control**: Configuration changes are tracked in git
- **Non-Technical Users**: Business users can modify tolerances
- **Reusability**: Same config across multiple test suites
- **Documentation**: Configuration serves as living documentation

## Advanced Usage

### Nested Object Comparison

The framework automatically handles nested objects and arrays:

```python
# Compare complex nested structures
expected = {
    "items": [
        {
            "nutrition": {
                "calories": 200,
                "protein": 15.5
            }
        }
    ]
}

# Tolerances apply to nested fields
profile = CompareProfile(
    fields={
        'items.*.nutrition.calories': FieldSettings(percentage=5.0),
        'items.*.nutrition.protein': FieldSettings(absolute=1.0),
    }
)
comparer = create(profile)
```

### Custom Field Paths

Use dot notation for nested field paths:

```python
fields = {
    'items.*.nutrition.calories': FieldSettings(percentage=10.0),
    'items.*.standard_serving.nutrition.protein': FieldSettings(absolute=2.0),
    'meta.model': FieldSettings(ignore=True),  # Ignore model name
    'meta.time': FieldSettings(ignore=True),   # Ignore timing
}
```

### Array Comparison

Arrays are compared element-wise with the same tolerances:

```python
# Each item in the array uses the same tolerance rules
expected_items = [{"calories": 100}, {"calories": 200}]
actual_items = [{"calories": 95}, {"calories": 210}]

# Both items will be compared with the same tolerance settings
```

## Real-World Example: Food Log Testing

Here's how you might use this framework to test nutritional analysis responses. Based on actual test failures, here are the typical differences you'll encounter:

**Typical Response Differences:**
- Nutritional values vary slightly (calories: 400→380, protein: 16→14)
- Type differences (confidence_score: 9→9.0, standard_servings: 2.0→2)
- Boolean flags differ (verified_calculation: true→false)
- Text descriptions completely different (source_notes)

**Example Output:**
```
nutrition
- calories          | 400        | 380        | PASS  (10%)
- protein           | 16         | 14         | PASS  (10%+2.0)
- calcium           | 40         | 52         | FAIL  (outside)
- fiber             | 2          | <missing>  | FAIL  (required)

consumed
- standard_servings | 2.0        | 2          | PASS  (norm)
- verified_calc     | true       | false      | FAIL  (exact)
- confidence        | 9.0        | <missing>  | PASS  (optional)
- - calories        | 400        | 380        | PASS  (10%)
- - protein         | 16         | 14         | PASS  (10%+2.0)

items[0]
- food_name         | "Peter Pan" | "Peanut Butter" | FAIL  (exact)
- confidence_score  | 9.0        | 8.5        | PASS  (10%+1.0)
- - calories        | 200        | 190        | PASS  (10%)
- - protein         | 8          | 7          | PASS  (10%+2.0)

items[1]            | <missing>  | {...}      | FAIL  (object missing)
totals              | <missing>  | {...}      | FAIL  (object missing)

meta                | {...}      | <missing>  | PASS  (optional)

source_notes        | "Assumed..." | "Nutrition..." | PASS  (ignore)
```

## Advanced Example: Complex Data Structures

For complex nested data with multiple field types, use wildcard patterns and comprehensive field configuration:

```python
from pyobcomp import create, CompareProfile, FieldSettings, ComparisonOptions

def test_meal_analysis_response():
    # Complex comparison rule set with wildcard patterns for nested structures
    profile = CompareProfile(
        fields={
            # Wildcard patterns for nested nutritional data
            'items.*.nutrition.calories': FieldSettings(percentage=10.0),
            'items.*.nutrition.protein': FieldSettings(percentage=10.0, absolute=2.0),
            'items.*.consumed.nutrition.calories': FieldSettings(percentage=10.0),
            'totals.calories': FieldSettings(percentage=10.0),
            
            # Critical fields - must match exactly
            'items.*.verified_calculation': FieldSettings(required=True),
            'verified_calculation': FieldSettings(required=True),
            
            # Text validation - only check not empty
            'items.*.food_name': FieldSettings(text_validation=True),
            
            # Optional fields - missing is OK
            'items.*.confidence': FieldSettings(required=False),
            'meta': FieldSettings(required=False),
            
            # Ignore variable fields
            'items.*.source_notes': FieldSettings(ignore=True),
            'meta.time': FieldSettings(ignore=True),
        },
        options=ComparisonOptions(normalize_types=True)
    )
    
    comparer = create(profile)
    result = comparer.compare(expected, actual)
    
    # Complete test integration
    if not result.matches:
        print("Response doesn't match expected data:")
        print(result.format_table(detail='failures'))
        assert False, f"Comparison failed: {result.summary}"
    
    print("✅ Response matches expected data within tolerances!")
```

**Key Features Demonstrated:**
- **Wildcard patterns**: `items.*.nutrition.calories` matches all items in arrays
- **Nested field paths**: Handle complex object structures
- **Complete test workflow**: Setup, compare, assert, report
- **Mixed field types**: Required, optional, ignored, and text validation fields

## Configuration Examples

### Strict Comparison
For critical data where exact matches are required:

```python
profile = CompareProfile(
    fields={
        'id': FieldSettings(required=True),  # Must match exactly
        'status': FieldSettings(required=True),
    }
)
comparer = create(profile)
```

### Lenient Comparison
For data where approximate matches are acceptable:

```python
profile = CompareProfile(
    fields={
        '*.calories': FieldSettings(percentage=20.0),
        '*.protein': FieldSettings(percentage=25.0, absolute=5.0),
        '*.description': FieldSettings(ignore=True),
        '*.notes': FieldSettings(ignore=True),
    }
)
comparer = create(profile)
```

### Mixed Strictness
Different tolerances for different types of data:

```python
profile = CompareProfile(
    fields={
        # Critical fields - strict
        'status': FieldSettings(required=True),
        'verified_calculation': FieldSettings(required=True),
        
        # Nutritional data - moderate tolerance
        '*.nutrition.calories': FieldSettings(percentage=10.0),
        '*.nutrition.protein': FieldSettings(percentage=15.0, absolute=2.0),
        
        # Text fields - lenient
        '*.food_name': FieldSettings(text_validation=True),
        '*.source_notes': FieldSettings(ignore=True),
        
        # Metadata - ignore
        'meta.*': FieldSettings(ignore=True),
    }
)
comparer = create(profile)
```

## Difference Reporting

The framework provides both programmatic and textual reporting capabilities:

### Programmatic API

```python
result = comparer.compare(expected, actual)

# Overall result
print(f"Overall match: {result.matches}")
print(f"Summary: {result.summary}")

# Individual field results
for field in result.fields:
    print(f"{field.name}: {field.status} - {field.passed}")
    if field.passed:
        print(f"  Reason: {field.reason}")
    else:
        print(f"  Expected: {field.expected}, Actual: {field.actual}")
```

### Textual Formatting

```python
# Compact tabular output
print(result.format_table(detail='failures'))
```

### Tabular Output Format

The `format_table()` method provides a clean, compact view of all differences:

```
nutrition
- calories          | 190        | 200        | PASS  (10%)
- protein           | 14         | 16         | PASS  (10%+2.0)
- carbs             | 7          | 7          | PASS  (exact)

consumed
- standard_servings | 2          | 2.0        | PASS  (norm)
- verified_calc     | true       | false      | FAIL  (exact)
- - calories        | 190        | 200        | PASS  (10%)
- - protein         | 14         | 16         | PASS  (10%+2.0)

meta
- time              | 100.0      | 95.2       | PASS  (ignore)
- provider          | test       | real       | PASS  (ignore)
```

**Column Format:**
- **Field**: Truncated field name (max 15 chars)
- **Expected**: Expected value (max 12 chars)
- **Actual**: Actual value (max 12 chars) 
- **Status**: PASS/FAIL with reason in parentheses
- **Details**: Tolerance or reason (truncated to fit)

**Grouping**: Fields are grouped by their parent object for better readability.

**Output Detail Levels:**
```python
# Level 1: Show only failures (default)
result.format_table(detail='failures')

# Level 2: Show both passes and failures  
result.format_table(detail='differences')

# Level 3: Show all fields including identical matches
result.format_table(detail='all')
```

**Detail Level Examples:**

**failures** (default - only failures):
```
nutrition
- calcium           | 40         | 52         | FAIL  (outside)
- fiber             | 2          | <missing>  | FAIL  (required)

consumed
- verified_calc     | true       | false      | FAIL  (exact)

items[0]
- food_name         | "Peter Pan" | "Peanut Butter" | FAIL  (exact)
```

**differences** (passes + failures):
```
nutrition
- calories          | 400        | 380        | PASS  (10%)
- protein           | 16         | 14         | PASS  (10%+2.0)
- calcium           | 40         | 52         | FAIL  (outside)
- fiber             | 2          | <missing>  | FAIL  (required)
```

**all** (everything including identical):
```
nutrition
- calories          | 400        | 380        | PASS  (10%)
- protein           | 16         | 14         | PASS  (10%+2.0)
- carbs             | 7          | 7          | IDENTICAL
- calcium           | 40         | 52         | FAIL  (outside)
```

**Nested Property Handling:**
- **Dot notation**: Use `parent.child` for nested properties (e.g., `nutrition.calories`)
- **Array notation**: Use `parent.*.child` for array items (e.g., `items.*.nutrition.calories`)
- **Deep nesting**: Supports unlimited nesting levels (e.g., `items.*.consumed.nutrition.calories`)
- **Hierarchical display**: Use `-` for first level, `- -` for second level, etc.
- **Array items**: Show as `items[0]`, `items[1]` with nested properties underneath
- **Grouped display**: Nested properties are grouped under their parent object

**Missing Value Handling:**
- **Required fields**: Missing values cause FAIL (e.g., `fiber` missing)
- **Optional fields**: Missing values cause PASS (e.g., `confidence` missing)  
- **Missing array items**: Missing array elements cause FAIL (e.g., `items[1]` missing)
- **Missing objects**: Missing non-array objects cause FAIL (e.g., `totals` missing)
- **Missing optional objects**: Missing optional objects cause PASS (e.g., `meta` missing)
- **Missing arrays**: Array length mismatches cause FAIL

## Error Handling

The framework gracefully handles various error conditions:

- **Missing fields**: Configurable as errors, warnings, or ignored
- **Type mismatches**: Clear error messages with expected vs actual types
- **Invalid tolerances**: Validation errors with helpful suggestions
- **Circular references**: Detected and handled safely
- **Large objects**: Efficient comparison with progress reporting

## Performance Considerations

- **Lazy evaluation**: Only compares fields that have tolerance rules
- **Early termination**: Stops on first critical error if configured
- **Memory efficient**: Streams large arrays without loading everything into memory
- **Caching**: Reuses compiled tolerance rules for repeated comparisons

## Integration with Testing Frameworks

### Pytest Integration

```python
import pytest
from pyobcomp import create, CompareProfile, FieldSettings

@pytest.fixture
def nutrition_comparer():
    # Create comparison rule set for nutritional data
    profile = CompareProfile(
        fields={
            '*.nutrition.calories': FieldSettings(percentage=10.0),
            '*.nutrition.protein': FieldSettings(percentage=15.0, absolute=2.0),
        }
    )
    return create(profile)

def test_nutrition_analysis(nutrition_comparer):
    expected = load_expected_data()
    actual = service.analyze("test meal")
    
    result = nutrition_comparer.compare(expected, actual)
    assert result.matches, f"Comparison failed: {result.summary}"
```

### Custom Assertions

```python
def assert_nutrition_matches(expected, actual, tolerances=None):
    """Custom assertion for nutritional data comparison."""
    if tolerances is None:
        tolerances = {
            '*.nutrition.calories': FieldSettings(percentage=10.0),
            '*.nutrition.protein': FieldSettings(percentage=15.0, absolute=2.0),
        }
    
    # Create comparison rule set with tolerances
    profile = CompareProfile(fields=tolerances)
    comparer = create(profile)
    result = comparer.compare(expected, actual)
    
    if not result.matches:
        # Custom error formatting
        error_msg = "Nutritional data doesn't match:\n"
        for field in result.fields:
            if not field.passed:
                error_msg += f"  {field.name}: expected {field.expected}, got {field.actual}\n"
        raise AssertionError(error_msg)
```

## Best Practices

1. **Start with reasonable tolerances** and tighten them as needed
2. **Use percentage tolerances for proportional data** (calories, macros)
3. **Use absolute tolerances for small values** (vitamins, minerals)
4. **Combine tolerances** for maximum flexibility (10% OR 2.0, whichever greater)
5. **Ignore metadata fields** that don't affect functionality
6. **Use text validation** for descriptions and notes
7. **Test with real data** to validate tolerance settings
8. **Document tolerance rationale** in test comments

## Common Patterns

### Food Log Testing
```python
# Typical configuration for nutritional analysis testing
profile = CompareProfile(
    fields={
        # Macros with combined tolerances
        '*.nutrition.calories': FieldSettings(percentage=10.0),
        '*.nutrition.protein': FieldSettings(percentage=10.0, absolute=2.0),
        '*.nutrition.carbs': FieldSettings(percentage=10.0, absolute=2.0),
        '*.nutrition.fat': FieldSettings(percentage=10.0, absolute=2.0),
        
        # Critical flags - must match exactly
        '*.verified_calculation': FieldSettings(required=True),
        
        # Text fields - only check not empty
        '*.food_name': FieldSettings(text_validation=True),
        '*.user_description': FieldSettings(text_validation=True),
        
        # Ignore variable fields
        '*.source_notes': FieldSettings(ignore=True),
        'meta.*': FieldSettings(ignore=True),
    },
    options=ComparisonOptions(normalize_types=True)  # Handle 9 vs 9.0, 2.0 vs 2
)
comparer = create(profile)
```

## Limitations

The framework is designed to be focused and practical. It will **NOT** handle:

- **Unit conversions** (e.g., "g" vs "serving", "ml" vs "cup") - these will fail
- **Complex data transformations** - only direct value comparisons
- **Semantic equivalence** - "peanut butter" vs "PB" will fail
- **Date/time formatting** - only exact matches
- **Array reordering** - arrays must be in same order

For these cases, you should:
1. **Normalize your test data** to use consistent units
2. **Pre-process data** before comparison
3. **Use exact field matching** for critical data

## Troubleshooting

### Common Issues

**Q: Why is my comparison failing when values look close?**
A: Check your tolerance configuration. The framework is strict by default - you need to configure tolerances for numerical fields. Use `result.format_table()` to see a clear summary.

**Q: How do I handle optional fields that might be missing?**
A: Use `FieldSettings(required=False)` for fields that may or may not be present.

**Q: Can I compare arrays of different lengths?**
A: Yes, but it will report the length difference as an error. Configure array length tolerance if needed.

**Q: How do I ignore certain fields completely?**
A: Use `FieldSettings(ignore=True)` for fields you want to skip entirely.

**Q: How do I get a cleaner output format?**
A: Use `result.format_table()` instead of iterating through `result.fields`. It provides a compact tabular view with grouping.


This will log every comparison step, making it easier to understand why comparisons fail.

## API Reference

See the full API documentation in the `pyobcomp` module for detailed information about all classes and methods.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.