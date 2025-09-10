"""
Tests for object comparison functionality using programmatic profile creation.

These tests create profiles programmatically to match the same scenarios as
YAML-based tests, ensuring identical behavior with different data sources.
"""

import pytest
from pyobcomp import CompareProfile, FieldSettings, ComparisonOptions
from .helpers.compare import BaseCompareTests


class TestCompareWithCode(BaseCompareTests):
    """Tests for object comparison functionality using programmatic profile creation."""
    
    def setup_method(self):
        """Set up test helper."""
        self.test_data = {
            "absolute_tolerance": (
                CompareProfile(fields={
                    'calories': FieldSettings(absolute=10.0),
                    'protein': FieldSettings(absolute=2.5),
                }),
                {"calories": 200, "protein": 25.5},
                {"calories": 205, "protein": 27.0}
            ),
            "percentage_tolerance": (
                CompareProfile(fields={
                    'calories': FieldSettings(percentage=5.0),
                    'protein': FieldSettings(percentage=10.0),
                }),
                {"calories": 200, "protein": 25.5},
                {"calories": 195, "protein": 23.0}
            ),
            "field_not_required": (
                CompareProfile(fields={
                    'calories': FieldSettings(required=True),
                    'protein': FieldSettings(required=False),
                    'fiber': FieldSettings(required=False),
                }),
                {"calories": 100, "protein": 15.0, "fiber": 5.0},
                {"calories": 100}
            ),
            "field_required": (
                CompareProfile(fields={
                    'calories': FieldSettings(required=True),
                    'protein': FieldSettings(required=True),
                }),
                {"calories": 100, "protein": 15.0},
                {"calories": 100}
            ),
            "list_item_missing": (
                CompareProfile(fields={
                    'items.*.calories': FieldSettings(percentage=10.0),
                    'items.*.protein': FieldSettings(percentage=10.0),
                }),
                {
                    'items': [
                        {'calories': 100, 'protein': 15.0},
                        {'calories': 200, 'protein': 25.0}
                    ]
                },
                {
                    'items': [
                        {'calories': 100, 'protein': 15.0}
                    ]
                }
            ),
            "list_item_field_mismatch": (
                CompareProfile(fields={
                    'items.*.calories': FieldSettings(percentage=10.0),
                    'items.*.protein': FieldSettings(percentage=10.0),
                }),
                {
                    'items': [
                        {'calories': 100, 'protein': 15.0},
                        {'calories': 200, 'protein': 25.0}
                    ]
                },
                {
                    'items': [
                        {'calories': 100, 'protein': 15.0},
                        {'calories': 250, 'protein': 25.0}
                    ]
                }
            ),
            "deep_nested": (
                CompareProfile(fields={
                    'nutrition.macros.calories': FieldSettings(percentage=5.0),
                    'nutrition.macros.protein': FieldSettings(absolute=2.0),
                    'nutrition.vitamins.vitamin_c': FieldSettings(required=True),
                }),
                {
                    'nutrition': {
                        'macros': {
                            'calories': 200,
                            'protein': 25.5
                        },
                        'vitamins': {
                            'vitamin_c': 50
                        }
                    }
                },
                {
                    'nutrition': {
                        'macros': {
                            'calories': 210,
                            'protein': 27.0
                        },
                        'vitamins': {
                            'vitamin_c': 45
                        }
                    }
                }
            ),
            "mixed_tolerances": (
                CompareProfile(fields={
                    'calories': FieldSettings(percentage=10.0, absolute=5.0),
                    'protein': FieldSettings(percentage=5.0, absolute=10.0),
                }),
                {"calories": 100, "protein": 20.0},
                {"calories": 98, "protein": 18.0}
            ),
            "ignore_fields": (
                CompareProfile(fields={
                    'calories': FieldSettings(percentage=10.0),
                    'protein': FieldSettings(ignore=True),
                    'sodium': FieldSettings(ignore=True),
                    'carbs': FieldSettings(percentage=10.0),
                }),
                {"calories": 100, "protein": 15.0, "sodium": 500, "carbs": 5.0},
                {"calories": 95, "protein": 20.0, "sodium": 600, "carbs": 5.0}
            ),
            "text_validation": (
                CompareProfile(fields={
                    'name': FieldSettings(text_validation=True),
                    'description': FieldSettings(text_validation=True),
                    'calories': FieldSettings(percentage=5.0),
                }),
                {"name": "Apple", "description": "A red fruit", "calories": 200},
                {"name": "Apple", "description": "A red fruit", "calories": 210}
            ),
        }
    
    def get_test_data(self, test_name):
        """Get profile and data from dictionary."""
        return self.test_data[test_name]
