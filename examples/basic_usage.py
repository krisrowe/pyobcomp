#!/usr/bin/env python3
"""
Basic usage example for PyObComp.
"""

from pyobcomp import ObjectComparator, ToleranceConfig, FieldConfig


def main():
    """Demonstrate basic PyObComp usage."""
    print("PyObComp - Basic Usage Example")
    print("=" * 40)
    
    # Create a comparator with custom tolerances
    comparator = ObjectComparator(
        tolerances={
            'calories': ToleranceConfig(percentage=10.0),  # 10% tolerance
            'protein': ToleranceConfig(percentage=10.0, absolute=2.0),  # 10% or 2.0, whichever is greater
            'verified_calculation': FieldConfig(required=True),  # Must match exactly
            'source_notes': FieldConfig(ignore=True),  # Ignore text fields
        },
        normalize_types=True  # Handle 9 vs 9.0, 2.0 vs 2
    )
    
    # Example data
    expected_data = {
        'calories': 200,
        'protein': 15.0,
        'verified_calculation': True,
        'source_notes': 'Some notes'
    }
    
    actual_data = {
        'calories': 190,  # Within 10% tolerance
        'protein': 14.0,  # Within tolerance (10% = 1.5, absolute = 2.0, so 2.0 is used)
        'verified_calculation': True,  # Exact match required
        'source_notes': 'Different notes'  # Ignored
    }
    
    # Compare objects
    print("Comparing objects...")
    result = comparator.compare(expected_data, actual_data)
    
    # Display results
    print(f"\nOverall result: {'PASS' if result.matches else 'FAIL'}")
    print(f"Summary: {result.summary}")
    
    if not result.matches:
        print("\nDetailed differences:")
        print(result.format_table(detail='failures'))
    else:
        print("✅ Objects match within tolerances!")


if __name__ == '__main__':
    main()
