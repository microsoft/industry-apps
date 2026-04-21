"""
API router for Process Simulation endpoints.

Provides endpoints for managing business process definitions, scenarios,
event streams, and executing simulations against Dataverse.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models import (
    GenerateDataModelsRequest,
    ListModulesWithProcessesResponse,
    FileListRequest,
    FileListResponse,
    ReadFileRequest,
    ReadFileResponse,
    WriteFileRequest,
    ValidateEventStreamRequest,
    ValidateEventStreamResponse,
    ValidationResult,
    DryRunRequest,
    DryRunResponse,
    DryRunEventResult,
    ExecuteEventStreamRequest,
    ExecuteEventStreamResponse,
    ExecutionEventResult
)
from services.process_simulation_service import ProcessSimulationService
from config import PROJECT_ROOT

router = APIRouter(prefix="/api/process-sim", tags=["process-simulation"])

# Initialize service
service = ProcessSimulationService(Path(PROJECT_ROOT))


@router.get("/modules")
async def list_modules():
    """
    List all modules that have or can have process definitions.
    
    Returns:
        List of module dictionaries
    """
    try:
        modules = service.list_modules_with_processes()
        return {"modules": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files")
async def list_files(request: FileListRequest):
    """
    List files of a specific type in a module.
    
    Valid file_type values:
    - data-models
    - processes
    - scenarios
    - simulations
    """
    try:
        files = service.list_files(request.module_path, request.file_type)
        return FileListResponse(files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/read")
async def read_file(request: ReadFileRequest):
    """
    Read the contents of a YAML file.
    """
    try:
        content = service.read_file(request.file_path)
        return ReadFileResponse(content=content, file_path=request.file_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/write")
async def write_file(request: WriteFileRequest):
    """
    Write or update a YAML file.
    """
    try:
        service.write_file(request.file_path, request.content, request.create_dirs)
        return {"success": True, "file_path": request.file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-data-models")
async def generate_data_models(request: GenerateDataModelsRequest):
    """
    Generate individual data-model YAML files from Entity.xml files in a module.
    
    Scans the module's src/Entities directory and creates individual YAML files
    for each table, documenting fields and relationships.
    """
    try:
        output_paths = service.generate_data_models(request.module_path)
        return {
            "success": True,
            "file_paths": output_paths,
            "count": len(output_paths),
            "message": f"Generated {len(output_paths)} data model files successfully"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-stream")
async def validate_event_stream(request: ValidateEventStreamRequest):
    """
    Validate an event stream against entity schemas.
    
    Checks:
    - YAML syntax is valid
    - Referenced entities exist
    - Referenced fields exist
    - Operations are valid
    - Required fields are present
    """
    try:
        valid, errors, warnings, event_validations = service.validate_event_stream(
            request.module_path,
            request.event_stream_yaml
        )
        
        return ValidateEventStreamResponse(
            valid=valid,
            errors=errors,
            warnings=warnings,
            event_validations=[
                ValidationResult(
                    event_id=ev["event_id"],
                    valid=ev["valid"],
                    errors=ev["errors"],
                    warnings=ev["warnings"]
                )
                for ev in event_validations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dry-run")
async def dry_run(request: DryRunRequest):
    """
    Simulate event stream execution without creating records.
    
    Performs validation and template variable resolution without
    actually executing operations against Dataverse.
    """
    try:
        success, total_events, valid_events, errors, warnings, event_results = service.dry_run(
            request.module_path,
            request.event_stream_yaml
        )
        
        return DryRunResponse(
            success=success,
            total_events=total_events,
            valid_events=valid_events,
            errors=errors,
            warnings=warnings,
            event_results=[
                DryRunEventResult(
                    event_id=er["event_id"],
                    operation=er["operation"],
                    entity=er["entity"],
                    success=er["success"],
                    errors=er["errors"],
                    warnings=er["warnings"],
                    resolved_fields=er["resolved_fields"]
                )
                for er in event_results
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_event_stream(request: ExecuteEventStreamRequest):
    """
    Execute an event stream against Dataverse.
    
    Creates/updates records in Dataverse according to the event stream.
    Requires dry-run validation to pass first.
    
    NOTE: Currently returns dry-run results. Full Dataverse integration
    is TODO.
    """
    try:
        # TODO: Implement actual execution with Dataverse client
        # For now, return dry-run results
        success, total_events, valid_events, errors, warnings, event_results = service.execute(
            request.module_path,
            request.event_stream_yaml,
            request.deployment,
            request.environment,
            request.clear_before_run
        )
        
        return ExecuteEventStreamResponse(
            success=success,
            total_events=total_events,
            executed_events=valid_events,
            failed_events=total_events - valid_events,
            errors=errors,
            event_results=[
                ExecutionEventResult(
                    event_id=er["event_id"],
                    operation=er["operation"],
                    entity=er["entity"],
                    success=er["success"],
                    record_id=None,  # TODO: Return actual record ID from Dataverse
                    errors=er["errors"],
                    duration_seconds=0.0  # TODO: Track actual execution time
                )
                for er in event_results
            ],
            total_duration_seconds=0.0  # TODO: Track total execution time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
