"""
Pydantic models for request/response validation.

This module contains all the data models used by the Industry Apps API endpoints.
Models are organized by feature domain for clarity.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


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


class ImportDataRequest(BaseModel):
    deployment: str
    environment_key: str
    module_path: str
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
    module_name: str
    version: str
    operationId: str


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


# ============================================================================
# Quick Create Form Builder Models
# ============================================================================

class AddQuickCreateSectionsRequest(BaseModel):
    """Add quick_create sections to all entity YAML files in a module."""
    module_path: str
    overwrite: bool = False  # If True, regenerate quick_create sections even if they exist


class UpdateQuickCreateSectionRequest(BaseModel):
    """Update or add quick_create section for a single entity."""
    module_path: str
    entity_name: str
    fields: Optional[List[str]] = None  # If None, generate smart defaults


class BuildQuickCreateRequest(BaseModel):
    """Build a Quick Create form for a single entity."""
    module_path: str
    entity_name: str
    file_path: Optional[str] = None  # Optional: read from specific YAML file
    use_single_column: bool = True  # Use single column (True) or 3-column template (False)
    force: bool = False  # If True, rebuild even if Quick Create form already exists


class BuildAllQuickCreateFormsRequest(BaseModel):
    """Build Quick Create forms for all entities in a module."""
    module_path: str
    use_single_column: bool = True
    force: bool = False  # If True, rebuild existing forms


# ============================================================================
# Process Simulation Models
# ============================================================================

class GenerateDataModelsRequest(BaseModel):
    """Generate data-models YAML from Entity.xml files in a module."""
    module_path: str


class ListModulesWithProcessesResponse(BaseModel):
    """Response containing modules that have process definitions."""
    modules: List[Dict[str, Any]]


class FileListRequest(BaseModel):
    """Request to list files of a specific type in a module."""
    module_path: str
    file_type: str  # 'data-models', 'processes', 'scenarios', 'simulations'


class FileListResponse(BaseModel):
    """Response containing list of definition files."""
    files: List[Dict[str, str]]  # [{name: str, path: str, modified: str}]


class ReadFileRequest(BaseModel):
    """Request to read a specific YAML file."""
    file_path: str


class ReadFileResponse(BaseModel):
    """Response containing file contents."""
    content: str
    file_path: str


class WriteFileRequest(BaseModel):
    """Request to write/update a YAML file."""
    file_path: str
    content: str
    create_dirs: bool = True


class ValidateEventStreamRequest(BaseModel):
    """Request to validate an event stream against entity schemas."""
    module_path: str
    event_stream_yaml: str


class ValidationResult(BaseModel):
    """Result of validation for a single event."""
    event_id: int
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class ValidateEventStreamResponse(BaseModel):
    """Response containing validation results."""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    event_validations: List[ValidationResult] = []


class DryRunRequest(BaseModel):
    """Request to dry-run an event stream (validate without executing)."""
    module_path: str
    event_stream_yaml: str
    deployment: Optional[str] = None
    environment: Optional[str] = None


class DryRunEventResult(BaseModel):
    """Result of dry-run for a single event."""
    event_id: int
    operation: str
    entity: str
    success: bool
    errors: List[str] = []
    warnings: List[str] = []
    resolved_fields: Dict[str, Any] = {}  # Shows template variable substitution


class DryRunResponse(BaseModel):
    """Response containing dry-run results."""
    success: bool
    total_events: int
    valid_events: int
    errors: List[str] = []
    warnings: List[str] = []
    event_results: List[DryRunEventResult] = []


class ExecuteEventStreamRequest(BaseModel):
    """Request to execute an event stream against Dataverse."""
    module_path: str
    event_stream_yaml: str
    deployment: str
    environment: str
    clear_before_run: bool = True
    operationId: Optional[str] = None


class ExecutionEventResult(BaseModel):
    """Result of executing a single event."""
    event_id: int
    operation: str
    entity: str
    success: bool
    record_id: Optional[str] = None
    errors: List[str] = []
    duration_seconds: float


class ExecuteEventStreamResponse(BaseModel):
    """Response containing execution results."""
    success: bool
    total_events: int
    executed_events: int
    failed_events: int
    errors: List[str] = []
    event_results: List[ExecutionEventResult] = []
    total_duration_seconds: float


# ============================================================================
# Process Simulation - YAML Schema Models (for validation)
# ============================================================================

class EntityField(BaseModel):
    """Entity field definition in data models."""
    logical_name: str
    display_name: str
    type: str  # string, choice, lookup, datetime, etc.
    required: str  # none, recommended, business_required, system_required
    max_length: Optional[int] = None
    options: Optional[List[Dict[str, Any]]] = None  # For choice fields
    target_entity: Optional[str] = None  # For lookup fields


class EntityRelationship(BaseModel):
    """Entity relationship definition."""
    name: str
    type: str  # one_to_many, many_to_one, many_to_many
    target_entity: str
    referencing_field: Optional[str] = None


class EntityDefinition(BaseModel):
    """Entity definition in data models."""
    logical_name: str
    display_name: str
    primary_field: str
    description: Optional[str] = None
    fields: List[EntityField]
    relationships: Optional[List[EntityRelationship]] = []


class DataModelsSchema(BaseModel):
    """Schema for individual data-model table files."""
    module: str
    generated: Optional[str] = None
    entities: List[EntityDefinition]


class ProcessPersona(BaseModel):
    """Persona definition in process."""
    role: str
    name: str
    responsibilities: List[str]


class ProcessStep(BaseModel):
    """Step definition in process."""
    step: int
    action: str
    description: str
    performed_by: str
    entities: List[str]
    required_fields: List[str]
    optional_fields: Optional[List[str]] = []
    business_rules: Optional[List[str]] = []


class ProcessOutcome(BaseModel):
    """Outcome definition in process."""
    outcome: str
    description: str
    required_records: Dict[str, Any]


class ProcessVariation(BaseModel):
    """Variation definition in process."""
    variation: str
    description: str
    affects_steps: List[int]
    notes: Optional[str] = None


class ProcessDefinitionSchema(BaseModel):
    """Schema for process definition YAML."""
    process_name: str
    display_name: str
    module: str
    description: str
    version: str
    personas: List[ProcessPersona]
    steps: List[ProcessStep]
    outcomes: Optional[List[ProcessOutcome]] = []
    variations: Optional[List[ProcessVariation]] = []


class ScenarioPersona(BaseModel):
    """Persona instance in scenario."""
    name: str
    employee_id: Optional[str] = None
    personality: Optional[str] = None
    experience_level: Optional[str] = None
    working_conditions: Optional[str] = None


class ScenarioDefinitionSchema(BaseModel):
    """Schema for scenario definition YAML."""
    scenario_name: str
    display_name: str
    module: str
    process: str  # References process_name
    version: str
    context: Dict[str, Any]
    personas: Dict[str, ScenarioPersona]
    parties: Optional[Dict[str, Any]] = {}
    case_details: Optional[Dict[str, Any]] = {}
    assignment_criteria: Optional[Dict[str, Any]] = {}
    complexity: Optional[str] = None
    estimated_steps: Optional[int] = None
    variations_applied: Optional[List[str]] = []
    generation_hints: Optional[List[str]] = []


class EventDefinition(BaseModel):
    """Single event in event stream."""
    event_id: int
    timestamp: str
    operation: str  # create, update, delete
    entity: str
    performed_by: Optional[str] = None
    reasoning: Optional[str] = None
    fields: Dict[str, Any]
    store_as: Optional[str] = None
    record_reference: Optional[str] = None  # For update operations


class EventStreamExecution(BaseModel):
    """Execution metadata in event stream."""
    dry_run_only: bool = False
    clear_before_run: bool = True
    stop_on_error: bool = True


class EventStreamSummary(BaseModel):
    """Summary of event stream."""
    total_events: int
    records_created: Dict[str, int]
    records_updated: Optional[Dict[str, int]] = {}
    estimated_duration: Optional[str] = None
    process_completed: bool
    variations_used: Optional[List[str]] = []


class EventStreamSchema(BaseModel):
    """Schema for event stream YAML."""
    event_stream_name: str
    display_name: str
    module: str
    based_on_process: str
    based_on_scenario: str
    generated: Optional[str] = None
    generated_by: Optional[str] = None
    execution: EventStreamExecution
    events: List[EventDefinition]
    summary: Optional[EventStreamSummary] = None

