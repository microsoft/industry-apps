"""
Dataverse Client Library

Shared library for interacting with Microsoft Dataverse Web API.
Used by both build-automation CLI tools and ui-tools backend API.
"""

from .client import DataverseClient
from .config import (
    load_deployment_config, 
    get_deployment_auth, 
    scan_solutions,
    get_solution_info,
    get_next_option_value,
    assign_option_values
)
from .buildmd_parser import parse_field_line, parse_buildmd
from .buildmd_updater import update_buildmd, update_choice_buildmd
from .schema_helpers import generate_schema_name, validate_schema_name

__all__ = [
    'DataverseClient',
    'load_deployment_config',
    'get_deployment_auth',
    'scan_solutions',
    'get_solution_info',
    'get_next_option_value',
    'assign_option_values',
    'parse_field_line',
    'parse_buildmd',
    'update_buildmd',
    'update_choice_buildmd',
    'generate_schema_name',
    'validate_schema_name',
]
