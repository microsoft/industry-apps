"""
Constants for Dataverse Model-Driven App FormXml manipulation.

This module contains GUID constants for control types (classid), form presentation types,
and other FormXml-specific constants used in Dataverse solutions.
"""

from enum import Enum
from typing import Dict


class ControlClassId(Enum):
    """Control type class IDs used in FormXml controls."""
    
    # Text-based controls
    TEXT_BOX = "{4273EDBD-AC1D-40d3-9FB2-095C621B552D}"
    MULTILINE_TEXT = "{E0DECE4B-6FC8-4A8F-A065-082708572369}"
    
    # Numeric controls
    WHOLE_NUMBER = "{C6D124CA-7EDA-4A60-AEA9-7FB8D318B68F}"
    DECIMAL_NUMBER = "{0D2C745A-E5A8-4C8F-BA63-C6D3BB604660}"
    CURRENCY = "{533B9E00-756B-4312-95A0-DC888637AC78}"
    
    # Date and time controls
    DATE_TIME = "{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}"
    
    # Choice controls
    OPTION_SET = "{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}"
    TWO_OPTIONS = "{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}"
    STATUS = "{5D68B988-0661-4db2-BC3E-17598AD3BE6C}"
    
    # Lookup controls
    LOOKUP = "{270BD3DB-D9AF-4782-9025-509E298DEC0A}"
    
    # Subgrid control
    SUBGRID = "{E7A81278-8635-4D9E-8D4D-59480B391C5B}"
    
    # Other controls
    NOTES = "{06375649-C143-495E-A496-C962E5B4488E}"
    QUICK_VIEW_FORM = "{5C5600E0-1D6E-4205-A272-BE80DA87FD42}"
    IFRAME = "{FD2A7985-3187-444e-908D-6624B4F19989}"
    WEB_RESOURCE = "{9FDF5F91-88B1-47f4-AD53-C11EFC01A01D}"
    SPACER = "{5546FE48-FFFE-4071-B072-2A1B649B7FF9}"
    BUSINESS_PROCESS_FLOW = "{F9A8A302-114E-466A-B582-6771B2AE0D92}"


class FormPresentation(Enum):
    """Form presentation types."""
    MAIN = 1
    MOBILE = 2
    QUICK_CREATE = 5
    QUICK_VIEW = 6
    CARD = 11
    MAIN_INTERACTIVE_EXPERIENCE = 12


class FormActivationState(Enum):
    """Form activation states."""
    INACTIVE = 0
    ACTIVE = 1


class HeaderDensity(Enum):
    """Header density options for forms."""
    HIGH = "High"
    HIGH_WITH_CONTROLS = "HighWithControls"
    LOW = "Low"


class SectionLayout(Enum):
    """Section layout types."""
    VARWIDTH = "varwidth"
    FIXED = "fixed"


class CellLabelAlignment(Enum):
    """Cell label alignment options."""
    LEFT = "Left"
    CENTER = "Center"
    RIGHT = "Right"


class CellLabelPosition(Enum):
    """Cell label position options."""
    LEFT = "Left"
    TOP = "Top"


# Mapping from friendly field type names to control class IDs
FIELD_TYPE_TO_CLASSID: Dict[str, str] = {
    "text": ControlClassId.TEXT_BOX.value,
    "singleline": ControlClassId.TEXT_BOX.value,
    "multiline": ControlClassId.MULTILINE_TEXT.value,
    "memo": ControlClassId.MULTILINE_TEXT.value,
    "richtext": ControlClassId.MULTILINE_TEXT.value,
    "integer": ControlClassId.WHOLE_NUMBER.value,
    "wholenumber": ControlClassId.WHOLE_NUMBER.value,
    "decimal": ControlClassId.DECIMAL_NUMBER.value,
    "float": ControlClassId.DECIMAL_NUMBER.value,
    "currency": ControlClassId.CURRENCY.value,
    "money": ControlClassId.CURRENCY.value,
    "datetime": ControlClassId.DATE_TIME.value,
    "date": ControlClassId.DATE_TIME.value,
    "optionset": ControlClassId.OPTION_SET.value,
    "picklist": ControlClassId.OPTION_SET.value,
    "choice": ControlClassId.OPTION_SET.value,
    "twooptions": ControlClassId.TWO_OPTIONS.value,
    "boolean": ControlClassId.TWO_OPTIONS.value,
    "yesno": ControlClassId.TWO_OPTIONS.value,
    "status": ControlClassId.STATUS.value,
    "statuscode": ControlClassId.STATUS.value,
    "lookup": ControlClassId.LOOKUP.value,
    "customer": ControlClassId.LOOKUP.value,
    "owner": ControlClassId.LOOKUP.value,
    "subgrid": ControlClassId.SUBGRID.value,
    "notes": ControlClassId.NOTES.value,
    "quickview": ControlClassId.QUICK_VIEW_FORM.value,
    "iframe": ControlClassId.IFRAME.value,
    "webresource": ControlClassId.WEB_RESOURCE.value,
    "spacer": ControlClassId.SPACER.value,
}


# Reverse mapping from class ID to friendly name
CLASSID_TO_FIELD_TYPE: Dict[str, str] = {
    ControlClassId.TEXT_BOX.value: "text",
    ControlClassId.MULTILINE_TEXT.value: "multiline",
    ControlClassId.WHOLE_NUMBER.value: "integer",
    ControlClassId.DECIMAL_NUMBER.value: "decimal",
    ControlClassId.CURRENCY.value: "currency",
    ControlClassId.DATE_TIME.value: "datetime",
    ControlClassId.OPTION_SET.value: "optionset",
    ControlClassId.TWO_OPTIONS.value: "twooptions",
    ControlClassId.STATUS.value: "status",
    ControlClassId.LOOKUP.value: "lookup",
    ControlClassId.SUBGRID.value: "subgrid",
    ControlClassId.NOTES.value: "notes",
    ControlClassId.QUICK_VIEW_FORM.value: "quickview",
    ControlClassId.IFRAME.value: "iframe",
    ControlClassId.WEB_RESOURCE.value: "webresource",
    ControlClassId.SPACER.value: "spacer",
}


def get_classid_for_field_type(field_type: str) -> str:
    """
    Get the control class ID for a given field type name.
    
    Args:
        field_type: Friendly field type name (case-insensitive)
        
    Returns:
        The GUID class ID for the control
        
    Raises:
        ValueError: If the field type is not recognized
    """
    field_type_lower = field_type.lower()
    if field_type_lower not in FIELD_TYPE_TO_CLASSID:
        raise ValueError(
            f"Unknown field type: {field_type}. Valid types: {', '.join(sorted(set(FIELD_TYPE_TO_CLASSID.keys())))}"
        )
    return FIELD_TYPE_TO_CLASSID[field_type_lower]


def get_field_type_for_classid(classid: str) -> str:
    """
    Get the friendly field type name for a given control class ID.
    
    Args:
        classid: The GUID class ID for the control
        
    Returns:
        Friendly field type name
        
    Raises:
        ValueError: If the class ID is not recognized
    """
    classid_upper = classid.upper()
    if classid_upper not in CLASSID_TO_FIELD_TYPE:
        raise ValueError(f"Unknown control class ID: {classid}")
    return CLASSID_TO_FIELD_TYPE[classid_upper]


def is_valid_classid(classid: str) -> bool:
    """
    Check if a given string is a valid control class ID.
    
    Args:
        classid: The GUID string to validate
        
    Returns:
        True if the class ID is recognized, False otherwise
    """
    return classid.upper() in CLASSID_TO_FIELD_TYPE


# Default values for common FormXml elements
DEFAULT_LANGUAGE_CODE = 1033  # English (United States)
DEFAULT_SECTION_COLUMNS = 1
DEFAULT_SECTION_LABELWIDTH = 115
DEFAULT_SUBGRID_RECORDS_PER_PAGE = 4
DEFAULT_SUBGRID_AUTO_EXPAND = "Fixed"
