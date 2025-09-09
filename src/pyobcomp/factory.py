"""
Factory for creating Comparer instances from various sources.

This module provides factory methods to create Comparer instances from
YAML files, CompareProfile objects, or other sources.
"""

import yaml
from typing import Union, Dict, Any
from pathlib import Path

from .models import CompareProfile, FieldSettings, ComparisonOptions, ToleranceConfig, FieldConfig


class ComparerFactory:
    """Factory for creating Comparer instances."""
    
    @staticmethod
    def load_profile(file_path: Union[str, Path]) -> CompareProfile:
        """Load a CompareProfile from a YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            CompareProfile instance
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return ComparerFactory._parse_config_data(config_data)
    
    @staticmethod
    def create_from_file(file_path: Union[str, Path]):
        """Create a Comparer directly from a YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            Comparer instance
        """
        profile = ComparerFactory.load_profile(file_path)
        return ComparerFactory.create(profile)
    
    @staticmethod
    def create(profile: CompareProfile):
        """Create a Comparer from a CompareProfile.
        
        Args:
            profile: CompareProfile instance
            
        Returns:
            Comparer instance
        """
        # Import here to avoid circular dependencies
        from .comparer import Comparer
        
        # Convert CompareProfile to the format expected by Comparer
        tolerances = {}
        for field_path, field_settings in profile.fields.items():
            if field_settings.percentage is not None or field_settings.absolute is not None:
                # Tolerance configuration - only pass non-None values
                tolerance_kwargs = {}
                if field_settings.percentage is not None:
                    tolerance_kwargs['percentage'] = field_settings.percentage
                if field_settings.absolute is not None:
                    tolerance_kwargs['absolute'] = field_settings.absolute
                tolerances[field_path] = ToleranceConfig(**tolerance_kwargs)
            else:
                # Field configuration - use defaults for unspecified values
                # If ignore or text_validation is True, set required to False to avoid validation conflict
                required_default = True
                if field_settings.ignore is True or field_settings.text_validation is True:
                    required_default = False
                
                tolerances[field_path] = FieldConfig(
                    required=field_settings.required if field_settings.required is not None else required_default,
                    ignore=field_settings.ignore if field_settings.ignore is not None else False,
                    text_validation=field_settings.text_validation if field_settings.text_validation is not None else False
                )
        
        return Comparer(tolerances=tolerances, options=profile.options)
    
    @staticmethod
    def _parse_config_data(config_data: Dict[str, Any]) -> CompareProfile:
        """Parse raw YAML data into a CompareProfile.
        
        Args:
            config_data: Raw YAML data
            
        Returns:
            CompareProfile instance
            
        Raises:
            ValidationError: If the YAML structure is invalid
        """
        try:
            # Handle empty YAML files
            if config_data is None:
                config_data = {}
            
            fields = {}
            if 'fields' in config_data and config_data['fields']:
                for field_path, field_config in config_data['fields'].items():
                    # Check if tolerance fields are explicitly provided but both are None
                    if ('percentage' in field_config or 'absolute' in field_config) and \
                       field_config.get('percentage') is None and field_config.get('absolute') is None:
                        raise ValueError("At least one tolerance (percentage or absolute) must be specified")
                    
                    fields[field_path] = FieldSettings(**field_config)
            
            options = ComparisonOptions()
            if 'options' in config_data and config_data['options']:
                options = ComparisonOptions(**config_data['options'])
            
            return CompareProfile(fields=fields, options=options)
        except Exception as e:
            raise ValueError(f"Invalid YAML configuration: {e}") from e
    


# Convenience functions for module-level usage
def load_profile(file_path: Union[str, Path]) -> CompareProfile:
    """Load a CompareProfile from a YAML file."""
    return ComparerFactory.load_profile(file_path)


def create_from_file(file_path: Union[str, Path]):
    """Create a Comparer directly from a YAML file."""
    return ComparerFactory.create_from_file(file_path)


def create(profile: CompareProfile):
    """Create a Comparer from a CompareProfile."""
    return ComparerFactory.create(profile)


