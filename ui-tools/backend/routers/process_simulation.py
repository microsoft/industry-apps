"""
API router for Process Simulation endpoints.

Provides endpoints for managing business process definitions, scenarios,
event streams, and executing simulations against Dataverse.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from uuid import uuid4
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
    ExecutionEventResult,
    ExecuteSingleEventRequest,
    ExecuteSingleEventResponse,
    GetExecutionStateRequest,
    ExecutionStateResponse,
    ResetExecutionStateRequest
)
from services.process_simulation_service import ProcessSimulationService
from services.simulation_hydrator import SimulationHydrator
from config import PROJECT_ROOT

router = APIRouter(prefix="/api/process-sim", tags=["process-simulation"])

# Initialize services
service = ProcessSimulationService(Path(PROJECT_ROOT))
hydrator = SimulationHydrator(Path(PROJECT_ROOT))


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


@router.post("/analyze-prerequisites")
async def analyze_prerequisites(request: ValidateEventStreamRequest):
    """
    Analyze event stream to identify prerequisite records.
    
    Extracts:
    - Lookup references (lookup:...) expecting existing records
    - Template variables ({{...}}) not created by previous events
    
    Helps identify what records need to exist before execution.
    """
    try:
        result = service.analyze_prerequisites(request.event_stream_yaml)
        
        return {
            "lookup_prerequisites": result.get("lookup_prerequisites", []),
            "template_prerequisites": result.get("template_prerequisites", []),
            "total_prerequisites": result.get("total_prerequisites", 0),
            "error": result.get("error")
        }
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
    """
    try:
        success, total_events, executed_events, errors, warnings, event_results = service.execute(
            request.module_path,
            request.event_stream_yaml,
            request.deployment,
            request.environment,
            request.clear_before_run
        )
        
        # Calculate total duration
        total_duration = sum(er.get("duration_seconds", 0.0) for er in event_results)
        
        return ExecuteEventStreamResponse(
            success=success,
            total_events=total_events,
            executed_events=executed_events,
            failed_events=total_events - executed_events,
            errors=errors,
            event_results=[
                ExecutionEventResult(
                    event_id=er["event_id"],
                    operation=er["operation"],
                    entity=er["entity"],
                    success=er["success"],
                    record_id=er.get("record_id"),
                    errors=er.get("errors", []),
                    duration_seconds=er.get("duration_seconds", 0.0)
                )
                for er in event_results
            ],
            total_duration_seconds=total_duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-event")
async def execute_single_event(request: ExecuteSingleEventRequest):
    """
    Execute a single event from an event stream (step-by-step execution).
    
    This maintains execution state across calls, allowing incremental
    debugging and testing of simulations.
    """
    try:
        result = service.execute_single_event(
            request.module_path,
            request.event_stream_yaml,
            request.event_id,
            request.deployment,
            request.environment
        )
        
        # Parse YAML to get simulation name and total event count
        import yaml
        data = yaml.safe_load(request.event_stream_yaml)
        simulation_name = data.get("event_stream_name", "unknown")
        total_events = len(data.get("events", []))
        
        # Get state summary
        state = service.get_execution_state(request.module_path, simulation_name)
        executed_count = len(state["executed_events"]) if state else 0
        
        return ExecuteSingleEventResponse(
            success=result["success"],
            event_id=result["event_id"],
            record_id=result.get("record_id"),
            errors=result.get("errors", []),
            duration_seconds=result.get("duration_seconds", 0.0),
            state_summary={
                "total_events": total_events,
                "executed_count": executed_count,
                "pending_count": total_events - executed_count
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execution-state/get")
async def get_execution_state(request: GetExecutionStateRequest):
    """
    Get the current execution state for a simulation.
    
    Returns state information including executed events and stored records.
    """
    try:
        state = service.get_execution_state(request.module_path, request.simulation_name)
        
        if not state:
            raise HTTPException(status_code=404, detail="No execution state found for this simulation")
        
        # Extract executed event IDs
        executed_event_ids = [e.get("event_id") for e in state.get("executed_events", [])]
        
        return ExecutionStateResponse(
            simulation_key=state["simulation_key"],
            module_path=state["module_path"],
            simulation_name=state["simulation_name"],
            deployment=state["deployment"],
            environment=state["environment"],
            executed_event_ids=executed_event_ids,
            execution_results=state.get("executed_events", []),
            created_at=state.get("created_at", ""),
            last_updated=state.get("last_updated", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execution-state/reset")
async def reset_execution_state(request: ResetExecutionStateRequest):
    """
    Reset/clear the execution state for a simulation.
    
    This allows starting over with step-by-step execution.
    """
    try:
        success = service.reset_execution_state(request.module_path, request.simulation_name)
        
        if success:
            return {"success": True, "message": "Execution state reset successfully"}
        else:
            return {"success": False, "message": "No execution state found to reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# Template Hydration Endpoints
# ========================================================================

@router.post("/templates/list")
async def list_templates(request: FileListRequest):
    """
    List template event stream files in a module.
    
    Templates are stored in design/templates/ directory.
    """
    try:
        # Override file_type to templates
        files = service.list_files(request.module_path, "templates")
        return FileListResponse(files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hydrate/load-pools")
async def load_record_pools(request: dict):
    """
    Load record pools from Dataverse for persona selection.
    
    Args:
        module_path: Path to module
        deployment: Deployment name
        environment: Environment name
    
    Returns:
        Dictionary with counts of records loaded per entity type
    """
    try:
        module_path = request.get("module_path")
        deployment = request.get("deployment")
        environment = request.get("environment")
        
        if not all([module_path, deployment, environment]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get DataverseClient
        client = service._get_dataverse_client(deployment, environment)
        
        # Load record pools
        counts = hydrator.load_record_pools(module_path, client)
        
        return {
            "success": True,
            "record_pools": counts,
            "total_records": sum(counts.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hydrate/preview")
async def preview_hydration(request: dict):
    """
    Preview hydration of a template without saving.
    
    Args:
        module_path: Path to module
        template_name: Name of template file (e.g., 'harassment-investigation-template.yaml')
        deployment: Deployment name
        environment: Environment name
        stage: Optional stage to truncate at
    
    Returns:
        Hydrated event stream (single variation)
    """
    try:
        module_path = request.get("module_path")
        template_name = request.get("template_name")
        deployment = request.get("deployment")
        environment = request.get("environment")
        stage = request.get("stage")
        
        if not all([module_path, template_name, deployment, environment]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get template path
        template_path = Path(PROJECT_ROOT) / module_path / "design" / "templates" / template_name
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
        
        # Load record pools if not already loaded
        if not hydrator.record_pools:
            client = service._get_dataverse_client(deployment, environment)
            hydrator.load_record_pools(module_path, client)
        
        # Hydrate template
        hydrated = hydrator.hydrate_template(template_path, stage=stage)
        
        return {
            "success": True,
            "event_stream": hydrated,
            "event_count": len(hydrated.get("events", [])),
            "truncated_at_stage": hydrated.get("truncated_at_stage")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hydrate/generate-batch")
async def generate_batch(request: dict):
    """
    Generate multiple hydrated variations from a template.
    
    Args:
        module_path: Path to module
        template_name: Name of template file
        deployment: Deployment name
        environment: Environment name
        count: Number of variations to generate
        stage_distribution: Dict mapping stage names to percentages
        save_to_disk: Whether to save generated files to simulations/ folder
    
    Returns:
        List of hydrated event streams or file paths if saved
    """
    try:
        module_path = request.get("module_path")
        template_name = request.get("template_name")
        deployment = request.get("deployment")
        environment = request.get("environment")
        count = request.get("count", 10)
        stage_distribution = request.get("stage_distribution", {})
        save_to_disk = request.get("save_to_disk", False)
        
        if not all([module_path, template_name, deployment, environment]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get template path
        template_path = Path(PROJECT_ROOT) / module_path / "design" / "templates" / template_name
        
        if not template_path.exists():
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
        
        # Load record pools if not already loaded
        if not hydrator.record_pools:
            client = service._get_dataverse_client(deployment, environment)
            hydrator.load_record_pools(module_path, client)
        
        # Generate batch
        import yaml
        streams = hydrator.generate_batch(template_path, count, stage_distribution)
        
        if save_to_disk:
            # Save each stream to simulations/ directory
            simulations_dir = Path(PROJECT_ROOT) / module_path / "design" / "simulations"
            simulations_dir.mkdir(parents=True, exist_ok=True)
            
            saved_paths = []
            for stream in streams:
                stream_name = stream.get("event_stream_name", f"simulation-{uuid4().hex[:8]}")
                file_path = simulations_dir / f"{stream_name}.yaml"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(stream, f, sort_keys=False, allow_unicode=True)
                
                saved_paths.append(str(file_path.relative_to(PROJECT_ROOT)))
            
            return {
                "success": True,
                "count": len(saved_paths),
                "file_paths": saved_paths
            }
        else:
            # Return streams directly
            return {
                "success": True,
                "count": len(streams),
                "streams": streams
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
