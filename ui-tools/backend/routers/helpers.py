"""
Helpers Router - API endpoints for field creation and repository utilities.

This module contains endpoints for:
- Field creation (create-fields, batch operations)
- BUILD.md parsing and management
- Field templates
- Module scanning
- Solutions listing
- Table scanning
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pathlib import Path
from typing import List
import sys
import json
import xml.etree.ElementTree as ET

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    CreateFieldsRequest,
    FieldTemplateRequest,
    BatchCreateFieldsRequest,
    SingleTableFieldsRequest,
    TableScanRequest
)

# Import Dataverse client
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'dataverse-client'))
from client import DataverseClient


router = APIRouter(prefix="/api/helpers", tags=["Helpers"])


# Import scan_option_sets from option_sets router
async def scan_option_sets():
    """Import scan_option_sets from option_sets router"""
    from routers.option_sets import scan_option_sets as _scan_option_sets
    return await _scan_option_sets()


@router.post("/create-fields")
async def create_fields(request: CreateFieldsRequest):
    """Mass create fields on a Dataverse table using Python Dataverse client"""
    
    async def stream_field_creation():
        try:
            # Load deployment configuration
            config_path = PROJECT_ROOT / ".config" / "deployments.json"
            if not config_path.exists():
                yield f"data: {{\"type\": \"error\", \"message\": \"Configuration not found at {config_path}\"}}\n\n"
                return
            
            with open(config_path) as f:
                config = json.load(f)
            
            # Get the deployment configuration
            if request.deployment not in config.get("Deployments", {}):
                yield f"data: {{\"type\": \"error\", \"message\": \"Deployment '{request.deployment}' not found in configuration\"}}\n\n"
                return
            
            deployment_config = config["Deployments"][request.deployment]
            
            # Get authentication configuration from deployment
            if "Auth" not in deployment_config:
                yield f"data: {{\"type\": \"error\", \"message\": \"Auth configuration missing for deployment '{request.deployment}'. Please add Auth section with TenantId, ClientId, ClientSecret, and EnvironmentUrls.\"}}\n\n"
                return
            
            auth_config = deployment_config["Auth"]
            tenant_id = auth_config.get("TenantId")
            client_id = auth_config.get("ClientId")
            client_secret = auth_config.get("ClientSecret")
            
            if not all([tenant_id, client_id, client_secret]):
                yield f"data: {{\"type\": \"error\", \"message\": \"Incomplete auth configuration for deployment '{request.deployment}'. TenantId, ClientId, and ClientSecret are required.\"}}\n\n"
                return
            
            # Get environment URL from auth configuration
            environment_url = auth_config.get("EnvironmentUrls", {}).get(request.environment)
            if not environment_url:
                yield f"data: {{\"type\": \"error\", \"message\": \"Environment URL not configured for '{request.environment}' in deployment '{request.deployment}'\"}}\n\n"
                return
            
            # Initialize message
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Create Fields on Table: {request.tableName} ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Table: {request.tableName}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Fields to create: {len(request.fields)}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create Dataverse client
            yield f"data: {{\"type\": \"output\", \"line\": \"Connecting to Dataverse...\"}}\n\n"
            client = DataverseClient(
                environment_url=environment_url,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Authenticate
            client.authenticate()
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Connected successfully\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate choice fields have existing option sets
            choice_fields = [f for f in request.fields if f.get("type") in ["Choice", "Picklist"]]
            if choice_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating choice fields...\"}}\n\n"
                
                # Get option sets from Dataverse (primary source)
                yield f"data: {{\"type\": \"output\", \"line\": \"  Querying Dataverse for global option sets...\"}}\n\n"
                dataverse_option_sets = client.get_global_optionset_definitions()
                
                # Also scan local workspace option sets
                option_sets_response = await scan_option_sets()
                local_option_sets = option_sets_response.get("optionSets", [])
                
                # Merge: Dataverse option sets + local option sets (deduplicate by schema name)
                all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                for os in local_option_sets:
                    if os["schemaName"] not in all_option_sets:
                        all_option_sets[os["schemaName"]] = os
                
                all_option_sets_list = list(all_option_sets.values())
                yield f"data: {{\"type\": \"output\", \"line\": \"  Found {len(dataverse_option_sets)} option sets in Dataverse, {len(local_option_sets)} local\"}}\n\n"
                
                # Build lookup maps: schema name -> schema name, display name -> schema name
                option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                
                # Check each choice field and normalize option set references
                missing_option_sets = []
                for field in choice_fields:
                    option_set_name = field.get("optionSetSchemaName")
                    if not option_set_name:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                    else:
                        # Try to find by schema name first, then by display name
                        if option_set_name in option_set_by_schema:
                            # Already using schema name, no change needed
                            pass
                        elif option_set_name in option_set_by_display:
                            # Convert display name to schema name
                            schema_name = option_set_by_display[option_set_name]
                            field["optionSetSchemaName"] = schema_name
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ℹ Resolved '{option_set_name}' to '{schema_name}'\"}}\n\n"
                        else:
                            # Not found by either name
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                
                if missing_option_sets:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_option_sets:
                        error_escaped = error.replace('"', '\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced option sets exist (use Choice Creator to create them)\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All choice field option sets found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate lookup fields have existing target tables
            lookup_fields = [f for f in request.fields if f.get("type") in ["Lookup", "Reference"]]
            if lookup_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating lookup fields...\"}}\n\n"
                
                # Get all tables from Dataverse
                all_tables = client.get_entity_definitions()
                
                # Build lookup maps: logical name -> logical name, display name -> logical name
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                
                # Check each lookup field and normalize table references
                missing_tables = []
                for field in lookup_fields:
                    target_table = field.get("targetTableLogicalName")
                    if not target_table:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                    else:
                        # Try to find by logical name first, then by display name
                        if target_table in table_by_logical:
                            # Already using logical name, no change needed
                            pass
                        elif target_table in table_by_display:
                            # Convert display name to logical name
                            logical_name = table_by_display[target_table]
                            field["targetTableLogicalName"] = logical_name
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ℹ Resolved '{target_table}' to '{logical_name}'\"}}\n\n"
                        else:
                            # Not found by either name
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                
                if missing_tables:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_tables:
                        error_escaped = error.replace('"', '\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced tables exist\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All lookup field target tables found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Resolve table name to logical name
            all_tables = client.get_entity_definitions()
            table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
            table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
            
            table_logical_name = request.tableName
            if request.tableName in table_by_display:
                # Convert display name to logical name
                table_logical_name = table_by_display[request.tableName]
            elif request.tableName not in table_by_logical:
                # Table not found
                yield f"data: {{\"type\": \"error\", \"message\": \"Table '{request.tableName}' not found in Dataverse\"}}\n\n"
                return
            
            # Separate Name field renames from regular field creations
            name_field = None
            fields_to_create = []
            
            for field in request.fields:
                if field.get('operation') == 'rename_name_field':
                    if name_field:
                        yield f"data: {{\"type\": \"error\", \"message\": \"Multiple Name fields specified - only one allowed per table\"}}\n\n"
                        return
                    name_field = field
                else:
                    fields_to_create.append(field)
            
            # Calculate total operations
            total_operations = len(fields_to_create) + (1 if name_field else 0)
            
            # Process Name field rename first (if specified)
            name_rename_success = False
            if name_field:
                yield f"data: {{\"type\": \"output\", \"line\": \"Renaming table Name field...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  New display name: {name_field['displayName']}\"}}\n\n"
                
                result = client.update_name_field_display_name(
                    table_logical_name=table_logical_name,
                    new_display_name=name_field['displayName']
                )
                
                if result.get('success'):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Name field renamed successfully\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    name_rename_success = True
                else:
                    error_msg = result.get('error', 'Unknown error').replace('\"', '\\\\\"')
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Now create regular fields
            if fields_to_create:
                yield f"data: {{\"type\": \"output\", \"line\": \"Creating fields...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create fields
            success_count = 0
            fail_count = 0
            
            if name_rename_success:
                success_count += 1
            elif name_field and not name_rename_success:
                fail_count += 1
            
            for i, field in enumerate(fields_to_create, 1):
                schema_name = field.get("schemaName")
                display_name = field.get("displayName")
                field_type = field.get("type")
                
                yield f"data: {{\"type\": \"output\", \"line\": \"[{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  Type: {field_type}\"}}\n\n"
                
                # Create the field using the resolved logical table name
                result = client.create_field(table_logical_name, field)
                
                if result.get("success"):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Field created successfully\"}}\n\n"
                    success_count += 1
                else:
                    error_msg = result.get("error", "Unknown error")
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    fail_count += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Summary
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Summary ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Total operations: {total_operations}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Successful: {success_count}\"}}\n\n"
            if fail_count > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {fail_count}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Complete
            exit_code = 0 if fail_count == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_field_creation(),
        media_type="text/event-stream"
    )

@router.post("/create-single-table-fields")
async def create_single_table_fields(request: SingleTableFieldsRequest):
    """
    Create fields for a single table from BUILD.md Planned section.
    Simplified version of batch endpoint for single table operations.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables, move_fields_to_completed_last_round
    
    async def stream_single_table_creation():
        try:
            # Parse BUILD.md to get the specific table
            module_path = PROJECT_ROOT / request.modulePath
            
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Creating Fields for {request.tableName} ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Module: {request.modulePath}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse BUILD.md
            yield f"data: {{\"type\": \"output\", \"line\": \"Parsing BUILD.md...\"}}\n\n"
            tables = parse_build_md_tables(module_path, request.publisherPrefix)
            
            # Find the specific table
            table = None
            for t in tables:
                if t['tableName'] == request.tableName:
                    table = t
                    break
            
            if not table:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Error: Table '{request.tableName}' not found in BUILD.md\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                return
            
            field_count = len(table['fields'])
            
            if field_count == 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"⊘ No planned fields found for this table\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 0}}\n\n"
                return
            
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Found {field_count} fields to create\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse fields from BUILD.md format to Field Creator format
            parsed_fields = []
            for field_line in table['fields']:
                try:
                    parsed_field = _parse_field_from_buildmd_format(field_line, request.publisherPrefix)
                    if parsed_field:
                        parsed_fields.append(parsed_field)
                except Exception as e:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not parse field: {field_line} - {str(e)}\"}}\n\n"
            
            if not parsed_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ No valid fields to create\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                return
            
            # Call existing create-fields endpoint logic
            create_request = CreateFieldsRequest(
                deployment=request.deployment,
                environment=request.environment,
                tableName=request.tableName,
                fields=parsed_fields
            )
            
            # Stream output from create_fields - call the generator directly
            success_count = 0
            fail_count = 0
            successfully_created_fields = []
            
            # Inline field creation (same logic as create_fields endpoint)
            # Get deployment client config
            config_path = PROJECT_ROOT / ".config" / "deployments.json"
            with open(config_path) as f:
                config_data = json.load(f)
            
            deployment_config = config_data["Deployments"][request.deployment]
            auth_config = deployment_config["Auth"]
            
            environment_url = auth_config["EnvironmentUrls"][request.environment]
            tenant_id = auth_config["TenantId"]
            client_id = auth_config["ClientId"]
            client_secret = auth_config["ClientSecret"]
            
            # Create Dataverse client
            yield f"data: {{\"type\": \"output\", \"line\": \"Connecting to Dataverse...\"}}\n\n"
            client = DataverseClient(
                environment_url=environment_url,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            client.authenticate()
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Connected successfully\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate choice fields have existing option sets
            choice_fields = [f for f in parsed_fields if f.get("type") in ["Choice", "Picklist"]]
            if choice_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating choice fields...\"}}\n\n"
                dataverse_option_sets = client.get_global_optionset_definitions()
                option_sets_response = await scan_option_sets()
                local_option_sets = option_sets_response.get("optionSets", [])
                all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                for os in local_option_sets:
                    if os["schemaName"] not in all_option_sets:
                        all_option_sets[os["schemaName"]] = os
                all_option_sets_list = list(all_option_sets.values())
                option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                missing_option_sets = []
                for field in choice_fields:
                    option_set_name = field.get("optionSetSchemaName")
                    if not option_set_name:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                    elif option_set_name in option_set_by_schema:
                        pass
                    elif option_set_name in option_set_by_display:
                        field["optionSetSchemaName"] = option_set_by_display[option_set_name]
                    else:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                if missing_option_sets:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_option_sets:
                        error_escaped = error.replace('"', '\\\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced option sets exist (use Choice Creator to create them)\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All choice field option sets found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate lookup fields have existing target tables
            lookup_fields = [f for f in parsed_fields if f.get("type") in ["Lookup", "Reference"]]
            if lookup_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating lookup fields...\"}}\n\n"
                all_tables = client.get_entity_definitions()
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                missing_tables = []
                for field in lookup_fields:
                    target_table = field.get("targetTableLogicalName")
                    if not target_table:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                    elif target_table in table_by_logical:
                        pass
                    elif target_table in table_by_display:
                        field["targetTableLogicalName"] = table_by_display[target_table]
                    else:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                if missing_tables:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_tables:
                        error_escaped = error.replace('"', '\\\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced tables exist\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All lookup field target tables found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Resolve table name to logical name
            all_tables = client.get_entity_definitions()
            table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
            table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
            table_logical_name = request.tableName
            if request.tableName in table_by_display:
                table_logical_name = table_by_display[request.tableName]
            elif request.tableName not in table_by_logical:
                yield f"data: {{\"type\": \"error\", \"message\": \"Table '{request.tableName}' not found in Dataverse\"}}\n\n"
                return
            
            # Separate Name field renames from regular field creations
            name_field = None
            fields_to_create = []
            for field in parsed_fields:
                if field.get('operation') == 'rename_name_field':
                    name_field = field
                else:
                    fields_to_create.append(field)
            
            # Process Name field rename first (if specified)
            if name_field:
                yield f"data: {{\"type\": \"output\", \"line\": \"Renaming table Name field...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  New display name: {name_field['displayName']}\"}}\n\n"
                result = client.update_name_field_display_name(
                    table_logical_name=table_logical_name,
                    new_display_name=name_field['displayName']
                )
                if result.get('success'):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Name field renamed successfully\"}}\n\n"
                    successfully_created_fields.append(name_field['displayName'])
                else:
                    error_msg = result.get('error', 'Unknown error')
                    # Properly escape for JSON: backslashes first, then quotes, remove newlines
                    error_msg = error_msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create fields
            for i, field in enumerate(fields_to_create, 1):
                schema_name = field.get("schemaName")
                display_name = field.get("displayName")
                field_type = field.get("type")
                
                yield f"data: {{\"type\": \"output\", \"line\": \"[{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  Type: {field_type}\"}}\n\n"
                
                # Create the field using resolved table logical name
                result = client.create_field(table_logical_name, field)
                
                if result.get("success"):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Created field: {display_name} ({schema_name})\"}}\n\n"
                    success_count += 1
                    successfully_created_fields.append(display_name)
                else:
                    error_msg = result.get("error", "Unknown error")
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    fail_count += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Update BUILD.md file: move successfully created fields to Completed Last Round
            if successfully_created_fields:
                try:
                    moved = move_fields_to_completed_last_round(
                        module_path,
                        request.tableName,
                        successfully_created_fields
                    )
                    if moved:
                        yield f"data: {{\"type\": \"output\", \"line\": \"✓ Updated BUILD.md: Moved {len(successfully_created_fields)} fields to Completed Last Round\"}}\n\n"
                    else:
                        yield f"data: {{\"type\": \"output\", \"line\": \"⚠ Warning: Could not update BUILD.md\"}}\n\n"
                except Exception as e:
                    yield f"data: {{\"type\": \"output\", \"line\": \"⚠ Warning: Could not update BUILD.md: {str(e)}\"}}\n\n"
            
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Complete ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Successfully created: {success_count} fields\"}}\n\n"
            if fail_count > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {fail_count} fields\"}}\n\n"
            
            exit_code = 0 if fail_count == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_single_table_creation(),
        media_type="text/event-stream"
    )

@router.post("/batch-create-fields-from-buildmd")
async def batch_create_fields_from_buildmd(request: BatchCreateFieldsRequest):
    """
    Batch create fields from BUILD.md file with interactive table-by-table control.
    Parses BUILD.md, extracts Planned sections, calls existing create-fields endpoint for each table.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables
    
    async def stream_batch_creation():
        try:
            # Parse BUILD.md to get tables
            module_path = PROJECT_ROOT / request.modulePath
            
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Batch Field Creation from BUILD.md ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Module: {request.modulePath}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse BUILD.md
            yield f"data: {{\"type\": \"output\", \"line\": \"Parsing BUILD.md...\"}}\n\n"
            tables = parse_build_md_tables(module_path, request.publisherPrefix)
            
            if not tables:
                yield f"data: {{\"type\": \"output\", \"line\": \"⚠ No tables with Planned fields found in BUILD.md\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 0}}\n\n"
                return
            
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Found {len(tables)} tables with Planned fields\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Track stats
            total_tables = len(tables)
            tables_completed = 0
            tables_failed = 0
            tables_skipped = 0
            total_fields_created = 0
            
            # Process each table
            for table_index, table in enumerate(tables, 1):
                table_name = table['tableName']
                field_count = len(table['fields'])
                
                yield f"data: {{\"type\": \"output\", \"line\": \"═══════════════════════════════════════\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"Table {table_index}/{total_tables}: {table_name}\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"{field_count} fields to process\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Interactive mode: pause for user input
                if request.mode == "interactive":
                    yield f"data: {{\"type\": \"prompt\", \"table\": \"{table_name.replace(chr(34), chr(92)+chr(34))}\", \"index\": {table_index}, \"total\": {total_tables}}}\n\n"
                    # Frontend will send continue signal via separate mechanism (not implemented yet - for now just proceed)
                
                # Parse fields from BUILD.md format to Field Creator format
                parsed_fields = []
                for field_line in table['fields']:
                    try:
                        parsed_field = _parse_field_from_buildmd_format(field_line, request.publisherPrefix)
                        if parsed_field:
                            parsed_fields.append(parsed_field)
                    except Exception as e:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not parse field: {field_line} - {str(e)}\"}}\n\n"
                
                if not parsed_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ⊘ No valid fields to create, skipping table\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    tables_skipped += 1
                    continue
                
                # Call existing create-fields endpoint logic
                create_request = CreateFieldsRequest(
                    deployment=request.deployment,
                    environment=request.environment,
                    tableName=table_name,
                    fields=parsed_fields
                )
                
                # Create fields for this table
                table_success_count = 0
                table_fail_count = 0
                successfully_created_fields = []
                
                # Get deployment client config (reuse from top-level scope if possible, or fetch here)
                config_path = PROJECT_ROOT / ".config" / "deployments.json"
                with open(config_path) as f:
                    config_data = json.load(f)
                
                deployment_config = config_data["Deployments"][request.deployment]
                auth_config = deployment_config["Auth"]
                
                environment_url = auth_config["EnvironmentUrls"][request.environment]
                tenant_id = auth_config["TenantId"]
                client_id = auth_config["ClientId"]
                client_secret = auth_config["ClientSecret"]
                
                # Create Dataverse client
                yield f"data: {{\"type\": \"output\", \"line\": \"  Connecting to Dataverse...\"}}\n\n"
                client = DataverseClient(
                    environment_url=environment_url,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
                client.authenticate()
                yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Connected successfully\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Validate choice fields have existing option sets
                choice_fields = [f for f in parsed_fields if f.get("type") in ["Choice", "Picklist"]]
                if choice_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Validating choice fields...\"}}\n\n"
                    dataverse_option_sets = client.get_global_optionset_definitions()
                    option_sets_response = await scan_option_sets()
                    local_option_sets = option_sets_response.get("optionSets", [])
                    all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                    for os in local_option_sets:
                        if os["schemaName"] not in all_option_sets:
                            all_option_sets[os["schemaName"]] = os
                    all_option_sets_list = list(all_option_sets.values())
                    option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                    option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                    missing_option_sets = []
                    for field in choice_fields:
                        option_set_name = field.get("optionSetSchemaName")
                        if not option_set_name:
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                        elif option_set_name in option_set_by_schema:
                            pass
                        elif option_set_name in option_set_by_display:
                            field["optionSetSchemaName"] = option_set_by_display[option_set_name]
                        else:
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                    if missing_option_sets:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Validation failed:\"}}\n\n"
                        for error in missing_option_sets:
                            error_escaped = error.replace('"', '\\\\"')
                            yield f"data: {{\"type\": \"output\", \"line\": \"    - {error_escaped}\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table (please create missing option sets first)\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                        tables_failed += 1
                        continue
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ All choice field option sets found\"}}\n\n"
                
                # Validate lookup fields have existing target tables
                lookup_fields = [f for f in parsed_fields if f.get("type") in ["Lookup", "Reference"]]
                if lookup_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Validating lookup fields...\"}}\n\n"
                    all_tables = client.get_entity_definitions()
                    table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                    table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                    missing_tables = []
                    for field in lookup_fields:
                        target_table = field.get("targetTableLogicalName")
                        if not target_table:
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                        elif target_table in table_by_logical:
                            pass
                        elif target_table in table_by_display:
                            field["targetTableLogicalName"] = table_by_display[target_table]
                        else:
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                    if missing_tables:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Validation failed:\"}}\n\n"
                        for error in missing_tables:
                            error_escaped = error.replace('"', '\\\\"')
                            yield f"data: {{\"type\": \"output\", \"line\": \"    - {error_escaped}\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table (please create missing target tables first)\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                        tables_failed += 1
                        continue
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ All lookup field target tables found\"}}\n\n"
                
                # Resolve table name to logical name
                all_tables = client.get_entity_definitions()
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                table_logical_name = table_name
                if table_name in table_by_display:
                    table_logical_name = table_by_display[table_name]
                elif table_name not in table_by_logical:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Error: Table '{table_name}' not found in Dataverse\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    tables_failed += 1
                    continue
                
                # Separate Name field renames from regular field creations
                name_field = None
                fields_to_create = []
                for field in parsed_fields:
                    if field.get('operation') == 'rename_name_field':
                        name_field = field
                    else:
                        fields_to_create.append(field)
                
                # Process Name field rename first (if specified)
                if name_field:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Renaming table Name field...\"}}\n\n"
                    result = client.update_name_field_display_name(
                        table_logical_name=table_logical_name,
                        new_display_name=name_field['displayName']
                    )
                    if result.get('success'):
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✓ Name field renamed to '{name_field['displayName']}'\"}}\n\n"
                        successfully_created_fields.append(name_field['displayName'])
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        # Properly escape for JSON: backslashes first, then quotes, remove newlines
                        error_msg = error_msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✗ Failed: {error_msg}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Create fields
                for i, field in enumerate(fields_to_create, 1):
                    schema_name = field.get("schemaName")
                    display_name = field.get("displayName")
                    field_type = field.get("type")
                    
                    yield f"data: {{\"type\": \"output\", \"line\": \"  [{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"    Type: {field_type}\"}}\n\n"
                    
                    # Create the field using resolved table logical name
                    result = client.create_field(table_logical_name, field)
                    
                    if result.get("success"):
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✓ Created field: {display_name} ({schema_name})\"}}\n\n"
                        table_success_count += 1
                        successfully_created_fields.append(display_name)
                    else:
                        error_msg = result.get("error", "Unknown error")
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✗ Failed: {error_msg}\"}}\n\n"
                        table_fail_count += 1
                    
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Update BUILD.md file: move successfully created fields to Completed Last Round
                if successfully_created_fields:
                    try:
                        from build_md_parser import move_fields_to_completed_last_round
                        module_full_path = PROJECT_ROOT / request.modulePath
                        moved = move_fields_to_completed_last_round(
                            module_full_path,
                            table_name,
                            successfully_created_fields
                        )
                        if moved:
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Updated BUILD.md: Moved {len(successfully_created_fields)} fields to Completed Last Round\"}}\n\n"
                    except Exception as e:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not update BUILD.md: {str(e)}\"}}\n\n"
                
                # Update stats
                total_fields_created += table_success_count
                if table_fail_count > 0:
                    tables_failed += 1
                else:
                    tables_completed += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Final summary
            yield f"data: {{\"type\": \"output\", \"line\": \"═══════════════════════════════════════\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Batch Creation Complete ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Tables processed: {total_tables}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Completed: {tables_completed}\"}}\n\n"
            if tables_failed > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {tables_failed}\"}}\n\n"
            if tables_skipped > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"⊘ Skipped: {tables_skipped}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Total fields created: {total_fields_created}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            exit_code = 0 if tables_failed == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_batch_creation(),
        media_type="text/event-stream"
    )

def _parse_field_from_buildmd_format(field_line: str, publisher_prefix: str) -> dict:
    """
    Parse a BUILD.md format field line into Field Creator format.
    
    Args:
        field_line: e.g., "Period Code: Text" or "Person: Lookup (Person)"
        publisher_prefix: e.g., "appbase_"
    
    Returns:
        Field definition dict for create_field endpoint
    """
    # Split on first colon
    if ': ' not in field_line:
        return None
    
    display_name, type_info = field_line.split(': ', 1)
    display_name = display_name.strip()
    type_info = type_info.strip()
    
    # Generate schema name
    from build_md_parser import generate_schema_name
    schema_name = generate_schema_name(display_name, publisher_prefix)
    
    # Parse type and parameters
    field_type = type_info
    option_set = None
    target_table = None
    
    # Handle Choice (OptionSet) and Lookup (Table) formats
    if '(' in type_info and ')' in type_info:
        paren_start = type_info.index('(')
        paren_end = type_info.rindex(')')
        field_type = type_info[:paren_start].strip()
        param = type_info[paren_start+1:paren_end].strip()
        
        if field_type == 'Choice':
            option_set = param
        elif field_type == 'Lookup':
            target_table = param
    
    # Normalize type names
    if field_type in ['Yes / No', 'Yes/No']:
        field_type = 'YesNo'
    
    # Build field definition
    # Special handling for Name field - it's a rename operation, not a field creation
    if field_type == 'Name':
        field_def = {
            'displayName': display_name,
            'operation': 'rename_name_field'
        }
    else:
        field_def = {
            'schemaName': schema_name,
            'displayName': display_name,
            'type': field_type,
            'required': False
        }
        
        if option_set:
            field_def['optionSetSchemaName'] = option_set
        if target_table:
            field_def['targetTableLogicalName'] = target_table
    
    return field_def

@router.get("/scan-modules")
async def scan_modules():
    """Scan workspace for modules with BUILD.md files"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import get_available_modules
    
    try:
        modules = get_available_modules(PROJECT_ROOT)
        return {"modules": modules}
    except Exception as e:
        return {"error": str(e), "modules": []}

@router.get("/preview-tables")
async def preview_tables(module_path: str, publisher_prefix: str = "appbase_"):
    """Preview tables and fields from a BUILD.md file without creating them"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables
    
    try:
        # Parse BUILD.md with all sections for detailed preview
        full_path = PROJECT_ROOT / module_path
        tables = parse_build_md_tables(full_path, publisher_prefix, include_all_sections=True)
        
        # Format response with counts
        preview = {
            "tableCount": len(tables),
            "tables": [
                {
                    "tableName": table["tableName"],
                    "fieldCount": len(table["fields"]),
                    "fields": table["fields"],  # Planned fields only (for backward compatibility)
                    "sections": table.get("sections", {
                        "completed": [],
                        "completedLastRound": [],
                        "planned": table["fields"]
                    })
                }
                for table in tables
            ]
        }
        
        return preview
    except Exception as e:
        return {"error": str(e), "tableCount": 0, "tables": []}

@router.post("/update-build-md")
async def update_build_md(
    module_path: str,
    table_name: str,
    field_names: List[str]
):
    """Move successfully created fields from Planned to Completed Last Round in BUILD.md"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import move_fields_to_completed_last_round
    
    try:
        full_path = PROJECT_ROOT / module_path
        success = move_fields_to_completed_last_round(full_path, table_name, field_names)
        
        if success:
            return {"success": True, "message": f"Moved {len(field_names)} fields to Completed Last Round"}
        else:
            return {"success": False, "error": "Failed to update BUILD.md"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/field-templates")
async def get_field_templates():
    """Get list of all saved field templates"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    templates = []
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file) as f:
                template_data = json.load(f)
                templates.append({
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                    "fieldCount": len(template_data.get("fields", []))
                })
        except Exception as e:
            print(f"Error reading template {template_file}: {e}", file=sys.stderr)
    
    return {"templates": templates}

@router.post("/field-templates")
async def save_field_template(request: FieldTemplateRequest):
    """Save a field template"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Sanitize filename
    safe_name = "".join(c for c in request.name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    template_data = {
        "name": request.name,
        "description": request.description,
        "publisherPrefix": request.publisherPrefix,
        "fields": request.fields
    }
    
    try:
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        return {"success": True, "message": f"Template '{request.name}' saved successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.delete("/field-templates/{name}")
async def delete_field_template(name: str):
    """Delete a field template"""
    templates_dir = Path(__file__).parent / "templates"
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    if template_file.exists():
        try:
            template_file.unlink()
            return {"success": True, "message": f"Template '{name}' deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Template '{name}' not found"}

@router.get("/field-templates/{name}")
async def get_field_template(name: str):
    """Get a specific field template"""
    templates_dir = Path(__file__).parent / "templates"
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    if template_file.exists():
        try:
            with open(template_file) as f:
                template_data = json.load(f)
            return template_data
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Template '{name}' not found"}

# ============================================================================
# GLOBAL CHOICE / OPTION SET MANAGEMENT
# ============================================================================

@router.get("/solutions/list")
async def list_solutions():
    """Scan all modules for Solution.xml files and extract solution information"""
    solutions = []
    
    # Scan all category/module folders
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
    
    for category_dir in PROJECT_ROOT.iterdir():
        if not category_dir.is_dir() or category_dir.name in exclude_folders:
            continue
        
        for module_dir in category_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            solution_xml = module_dir / "src" / "Other" / "Solution.xml"
            if solution_xml.exists():
                try:
                    tree = ET.parse(solution_xml)
                    root = tree.getroot()
                    
                    # Extract solution details
                    manifest = root.find(".//SolutionManifest")
                    if manifest is not None:
                        unique_name = manifest.find("UniqueName")
                        localized_name = manifest.find(".//LocalizedName")
                        publisher = manifest.find(".//Publisher")
                        
                        solution_info = {
                            "uniqueName": unique_name.text if unique_name is not None else "",
                            "displayName": localized_name.get("description") if localized_name is not None else "",
                            "category": category_dir.name,
                            "module": module_dir.name,
                            "path": str(module_dir.relative_to(PROJECT_ROOT))
                        }
                        
                        # Extract publisher prefix and option value prefix
                        if publisher is not None:
                            prefix_elem = publisher.find("CustomizationPrefix")
                            option_prefix_elem = publisher.find("CustomizationOptionValuePrefix")
                            solution_info["prefix"] = prefix_elem.text if prefix_elem is not None else ""
                            solution_info["optionValuePrefix"] = option_prefix_elem.text if option_prefix_elem is not None else ""
                        
                        solutions.append(solution_info)
                        
                except Exception as e:
                    print(f"Error parsing solution XML {solution_xml}: {e}", file=sys.stderr)
    
    return {"solutions": sorted(solutions, key=lambda s: (s.get("category", ""), s.get("module", "")))}

