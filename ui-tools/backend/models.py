"""
Pydantic models for request/response validation.

This module contains all the data models used by the Industry Apps API endpoints.
Models are organized by feature domain for clarity.
"""

from pydantic import BaseModel
from typing import Optional


# ============================================================================
# Deployment Models
# ============================================================================

class DeployRequest(BaseModel):
    deployment: str
    category: str
    module: str
    targetEnvironment: str = None
    managed: bool = True
    upgrade: bool = False
    operationId: Optional[str] = None


class SyncRequest(BaseModel):
    deployment: str
    category: str
    module: str
    operationId: Optional[str] = None


class SyncFromRequest(BaseModel):
    deployment: str
    category: str
    module: str
    sourceEnvironment: str
    operationId: Optional[str] = None


class ShipRequest(BaseModel):
    tenant: str
    environment: str
    category: str
    module: str
    managed: bool = True
    upgrade: bool = False
    operationId: Optional[str] = None


# ============================================================================
# Module Management Models
# ============================================================================

class CreateModuleRequest(BaseModel):
    category: str
    moduleName: str
    deployment: str
    sourceEnvironment: str
    targetEnvironments: list[str] = []
    deploy: bool = False
    operationId: Optional[str] = None


# ============================================================================
# Release Management Models
# ============================================================================

class ReleaseRequest(BaseModel):
    category: str
    module: str
    operationId: Optional[str] = None


class UpdateVersionRequest(BaseModel):
    deployment: str
    category: str
    module: str
    version: str
    operationId: Optional[str] = None


class ReleaseValidationRequest(BaseModel):
    module_path: str


class ReleaseExecutionRequest(BaseModel):
    module_path: str
    module_name: str
    module_display_name: Optional[str] = None
    release_type: str
    new_version: str
    release_notes: str
    enabled_steps: list[str]
    sync_tenant: Optional[str] = None
    sync_environment: Optional[str] = None


class StepExecutionRequest(BaseModel):
    module_path: str
    module_name: str
    module_display_name: Optional[str] = None
    step: str
    version: str
    release_notes: str
    sync_tenant: Optional[str] = None
    sync_environment: Optional[str] = None
    operationId: str


class BuildPackagesRequest(BaseModel):
    module_path: str


# ============================================================================
# Field Management Models
# ============================================================================

class CreateFieldsRequest(BaseModel):
    deployment: str
    environment: str
    tableName: str
    fields: list[dict]


class FieldTemplateRequest(BaseModel):
    name: str
    description: str = ""
    publisherPrefix: str = ""
    fields: list[dict]


class BatchCreateFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    publisherPrefix: str = "appbase_"
    mode: str = "interactive"  # or "auto"
    operationId: str


class SingleTableFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    tableName: str
    publisherPrefix: str = "appbase_"
    operationId: str


class DetectExistingFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    publisherPrefix: str = "appbase_"


# ============================================================================
# Helpers & Utilities Models
# ============================================================================

class TableScanRequest(BaseModel):
    deployment: str
    environment: str


class OptionSetSearchRequest(BaseModel):
    displayName: Optional[str] = None
    optionLabels: Optional[list[str]] = None


class OptionSetCreateRequest(BaseModel):
    schemaName: str
    displayName: str
    description: str = ""
    options: list[dict]  # [{label: str, value: Optional[str]}]
    targetSolution: str  # solution unique name
    deployment: str
    environment: str


class PendingOptionSetRequest(BaseModel):
    schemaName: str
    displayName: str
    description: str = ""
    category: str
    module: str
    path: str
    options: list[dict]
    deployment: str
    environment: str


class CancelRequest(BaseModel):
    operationId: str


# ============================================================================
# Form Builder Models
# ============================================================================

class ListEntitiesRequest(BaseModel):
    module_path: str


class ExtractFieldsRequest(BaseModel):
    module_path: str
    entity_name: str
    form_guid: Optional[str] = None


class ValidateYamlRequest(BaseModel):
    yaml_config: str
    module_path: str


class BuildFormRequest(BaseModel):
    yaml_config: Optional[str] = None
    module_path: Optional[str] = None
    file_path: Optional[str] = None
    dry_run: bool = False


class ExtractAllEntitiesRequest(BaseModel):
    module_path: str
    overwrite: bool = False


class ExtractSingleEntityRequest(BaseModel):
    module_path: str
    entity_name: str


class BuildAllFormsRequest(BaseModel):
    module_path: str
