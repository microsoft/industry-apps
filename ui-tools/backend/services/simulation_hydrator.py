"""
Generic simulation hydration engine for volume test data generation.

This service is completely module-agnostic - it works for ANY module
(disputes, court cases, HR, assets, etc.) by using configuration-driven
approach with no hardcoded entity names or field names.
"""

import yaml
import re
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
import sys

logger = logging.getLogger(__name__)

# Add dataverse-client directory to path
dataverse_client_dir = Path(__file__).parent.parent.parent / "dataverse-client"
sys.path.insert(0, str(dataverse_client_dir))

from client import DataverseClient


class SimulationHydrator:
    """
    Generic hydration engine for filling template event streams with real data.
    
    Completely module-agnostic - works for any business process by reading
    configuration from template files and querying Dataverse for actual records.
    """
    
    def __init__(self, workspace_root: Path, dataverse_client: Optional[DataverseClient] = None):
        """
        Initialize hydration engine.
        
        Args:
            workspace_root: Root directory of workspace
            dataverse_client: Optional pre-initialized DataverseClient
        """
        self.workspace_root = workspace_root
        self.client = dataverse_client
        self.record_pools: Dict[str, List[Dict]] = {}
        
    # ========================================================================
    # Record Pool Management
    # ========================================================================
    
    def load_record_pools(self, module_path: str, client: DataverseClient) -> Dict[str, int]:
        """
        Load existing records from Dataverse to use as persona pool.
        
        Queries standard entities (contacts, accounts) and any custom entities
        mentioned in the module's data models.
        
        Args:
            module_path: Relative path to module (e.g., 'workforce/dispute-resolution')
            client: Initialized DataverseClient
            
        Returns:
            Dictionary with counts of records loaded per entity type
        """
        self.client = client
        self.record_pools = {}
        counts = {}
        
        # Always load contacts (used in most processes)
        try:
            logger.info("Loading contacts from Dataverse...")
            contacts = client.query_records("contacts", top=100)
            self.record_pools["contacts"] = contacts or []
            counts["contacts"] = len(self.record_pools["contacts"])
            logger.info(f"Loaded {counts['contacts']} contacts")
        except Exception as e:
            logger.warning(f"Could not load contacts: {e}")
            self.record_pools["contacts"] = []
            counts["contacts"] = 0
        
        # Load accounts
        try:
            logger.info("Loading accounts from Dataverse...")
            accounts = client.query_records("accounts", top=50)
            self.record_pools["accounts"] = accounts or []
            counts["accounts"] = len(self.record_pools["accounts"])
            logger.info(f"Loaded {counts['accounts']} accounts")
        except Exception as e:
            logger.warning(f"Could not load accounts: {e}")
            self.record_pools["accounts"] = []
            counts["accounts"] = 0
        
        # Load module-specific entities by scanning data models
        module_dir = self.workspace_root / module_path
        data_models_dir = module_dir / "design" / "data-models"
        
        if data_models_dir.exists():
            for yaml_file in data_models_dir.glob("*.yaml"):
                try:
                    table_data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                    schema_name = table_data.get("schema_name", "")
                    plural_name = table_data.get("plural_name", "")
                    
                    if not plural_name:
                        # Generate plural if not specified
                        plural_name = schema_name + "s" if schema_name else ""
                    
                    if plural_name and "organizationunit" in schema_name.lower():
                        # Load organization units if this module uses them
                        try:
                            logger.info(f"Loading {plural_name} from Dataverse...")
                            records = client.query_records(plural_name, top=50)
                            self.record_pools[schema_name] = records or []
                            counts[schema_name] = len(self.record_pools[schema_name])
                            logger.info(f"Loaded {counts[schema_name]} {schema_name}")
                        except Exception as e:
                            logger.warning(f"Could not load {plural_name}: {e}")
                            self.record_pools[schema_name] = []
                            counts[schema_name] = 0
                    
                    # Load compliance frameworks if module uses them
                    if "complianceframework" in schema_name.lower():
                        try:
                            logger.info(f"Loading {plural_name} from Dataverse...")
                            records = client.query_records(plural_name, top=20)
                            self.record_pools[schema_name] = records or []
                            counts[schema_name] = len(self.record_pools[schema_name])
                            logger.info(f"Loaded {counts[schema_name]} {schema_name}")
                        except Exception as e:
                            logger.warning(f"Could not load {plural_name}: {e}")
                            self.record_pools[schema_name] = []
                            counts[schema_name] = 0
                            
                except Exception as e:
                    logger.warning(f"Error processing {yaml_file.name}: {e}")
                    continue
        
        return counts
    
    def _filter_records_by_criteria(self, records: List[Dict], criteria: str) -> List[Dict]:
        """
        Filter records based on criteria string.
        
        Supports:
        - Field contains value: "jobtitle contains 'Engineer'"
        - Field equals value: "department='Human Resources'"
        - OR conditions: "jobtitle contains 'Engineer' OR jobtitle contains 'Analyst'"
        
        Args:
            records: List of record dictionaries
            criteria: Filter criteria string
            
        Returns:
            Filtered list of records
        """
        if not criteria or not records:
            return records
        
        filtered = []
        
        for record in records:
            # Split by OR for multiple conditions (any can match)
            or_conditions = [c.strip() for c in criteria.split(" OR ")]
            
            match = False
            for condition in or_conditions:
                # Parse condition: "field contains 'value'" or "field='value'"
                if " contains " in condition:
                    field, value = condition.split(" contains ", 1)
                    field = field.strip()
                    value = value.strip().strip("'\"")
                    
                    record_value = record.get(field, "")
                    if isinstance(record_value, str) and value.lower() in record_value.lower():
                        match = True
                        break
                        
                elif "=" in condition:
                    field, value = condition.split("=", 1)
                    field = field.strip()
                    value = value.strip().strip("'\"")
                    
                    record_value = record.get(field, "")
                    if isinstance(record_value, str) and record_value.lower() == value.lower():
                        match = True
                        break
            
            if match:
                filtered.append(record)
        
        return filtered
    
    def select_personas(self, persona_mapping: Dict[str, str]) -> Dict[str, Dict]:
        """
        Select actual records from pools to fulfill persona roles.
        
        Args:
            persona_mapping: Dictionary mapping persona keys to selection criteria
                Example: {
                    'PERSONA_COMPLAINANT': 'contacts[jobtitle contains "Engineer"]',
                    'ORG_UNIT': 'org_units[type="Department"]'
                }
        
        Returns:
            Dictionary mapping persona keys to selected records
        """
        selected = {}
        
        for persona_key, selector in persona_mapping.items():
            try:
                # Parse selector: "entity_name[criteria]"
                match = re.match(r'(\w+)\[(.+)\]', selector)
                if not match:
                    logger.warning(f"Invalid selector format for {persona_key}: {selector}")
                    continue
                
                entity_name = match.group(1)
                criteria = match.group(2)
                
                # Get pool for this entity type
                pool = self.record_pools.get(entity_name, [])
                
                if not pool:
                    logger.warning(f"No records in pool for {entity_name}")
                    continue
                
                # Filter by criteria
                candidates = self._filter_records_by_criteria(pool, criteria)
                
                if not candidates:
                    # Fallback to unfiltered pool
                    logger.warning(f"No matches for criteria '{criteria}', using any {entity_name}")
                    candidates = pool
                
                if candidates:
                    # Randomly select one
                    selected_record = random.choice(candidates)
                    selected[persona_key] = selected_record
                    logger.debug(f"Selected {persona_key}: {selected_record.get('fullname', selected_record.get('name', 'unknown'))}")
                else:
                    logger.warning(f"No candidates available for {persona_key}")
                    
            except Exception as e:
                logger.error(f"Error selecting persona {persona_key}: {e}")
                continue
        
        return selected
    
    # ========================================================================
    # Date Generation
    # ========================================================================
    
    def generate_dates(self, date_config: Dict[str, Any]) -> Dict[str, datetime]:
        """
        Generate realistic date progression based on rules.
        
        Args:
            date_config: Date generation configuration
                Example: {
                    'base_date': 'random(2025-01-01, 2026-04-24)',
                    'business_days': True,
                    'offsets': {
                        'DATE_FILING': 'base_date',
                        'DATE_INVESTIGATION_START': '3-5 days after DATE_FILING'
                    }
                }
        
        Returns:
            Dictionary mapping date keys to datetime objects
        """
        dates = {}
        
        # Parse and generate base date
        base_date_expr = date_config.get('base_date', '')
        base_date = self._parse_base_date(base_date_expr)
        dates['base_date'] = base_date
        
        business_days = date_config.get('business_days', True)
        offsets = date_config.get('offsets', {})
        
        # Generate dates based on offset rules
        for date_key, rule in offsets.items():
            try:
                if rule == 'base_date':
                    dates[date_key] = base_date
                else:
                    # Parse offset rule: "5-7 days after DATE_FILING"
                    dates[date_key] = self._apply_date_offset(dates, rule, business_days)
            except Exception as e:
                logger.error(f"Error generating date for {date_key}: {e}")
                dates[date_key] = base_date
        
        return dates
    
    def _parse_base_date(self, expr: str) -> datetime:
        """
        Parse base date expression.
        
        Supports:
        - 'random(2025-01-01, 2026-04-24)' - Random date in range
        - '2026-01-15' - Specific date
        - 'current_date' - Today
        
        Args:
            expr: Date expression string
            
        Returns:
            Datetime object
        """
        if expr.startswith('random('):
            # Extract date range
            match = re.match(r'random\(([^,]+),\s*([^)]+)\)', expr)
            if match:
                start_str = match.group(1).strip()
                end_str = match.group(2).strip()
                
                # Parse dates
                if end_str == 'current_date':
                    end_date = datetime.now()
                else:
                    end_date = datetime.fromisoformat(end_str)
                
                start_date = datetime.fromisoformat(start_str)
                
                # Random date in range
                delta = end_date - start_date
                random_days = random.randint(0, delta.days)
                return start_date + timedelta(days=random_days)
        
        elif expr == 'current_date':
            return datetime.now()
        
        else:
            # Parse as ISO date
            return datetime.fromisoformat(expr)
        
        # Fallback
        return datetime.now()
    
    def _apply_date_offset(self, dates: Dict[str, datetime], rule: str, business_days: bool) -> datetime:
        """
        Apply date offset rule.
        
        Args:
            dates: Dictionary of already-generated dates
            rule: Offset rule (e.g., "5-7 days after DATE_FILING")
            business_days: Whether to skip weekends
            
        Returns:
            Calculated datetime
        """
        # Parse rule: "N-M days after DATE_KEY"
        match = re.match(r'(\d+)-(\d+)\s+days?\s+after\s+(\w+)', rule)
        if not match:
            logger.warning(f"Could not parse offset rule: {rule}")
            return datetime.now()
        
        min_days = int(match.group(1))
        max_days = int(match.group(2))
        ref_date_key = match.group(3)
        
        ref_date = dates.get(ref_date_key)
        if not ref_date:
            logger.warning(f"Reference date {ref_date_key} not found")
            return datetime.now()
        
        # Random offset in range
        offset_days = random.randint(min_days, max_days)
        
        if business_days:
            # Add business days (skip weekends)
            result_date = ref_date
            days_added = 0
            while days_added < offset_days:
                result_date += timedelta(days=1)
                # Skip Saturday (5) and Sunday (6)
                if result_date.weekday() < 5:
                    days_added += 1
            return result_date
        else:
            # Add calendar days
            return ref_date + timedelta(days=offset_days)
    
    # ========================================================================
    # Parameter Selection
    # ========================================================================
    
    def select_parameters(self, param_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select random values for parameters based on configuration.
        
        Args:
            param_config: Parameter configuration with options and weights
                Example: {
                    'INCIDENT_TYPE': {
                        'options': ['Harassment', 'Discrimination'],
                        'weights': [0.6, 0.4]
                    }
                }
        
        Returns:
            Dictionary mapping parameter keys to selected values
        """
        selected = {}
        
        for param_key, config in param_config.items():
            try:
                if isinstance(config, dict):
                    if 'options' in config:
                        # Weighted random choice
                        options = config['options']
                        weights = config.get('weights', [1.0] * len(options))
                        selected[param_key] = random.choices(options, weights=weights)[0]
                    
                    elif 'min' in config and 'max' in config:
                        # Random integer in range
                        selected[param_key] = random.randint(config['min'], config['max'])
                    
                    elif 'default' in config:
                        # Use default
                        selected[param_key] = config['default']
                
            except Exception as e:
                logger.error(f"Error selecting parameter {param_key}: {e}")
                continue
        
        return selected
    
    # ========================================================================
    # Placeholder Filling
    # ========================================================================
    
    def fill_placeholders(self, template: Dict[str, Any], 
                         personas: Dict[str, Dict],
                         dates: Dict[str, datetime],
                         parameters: Dict[str, Any],
                         case_numbers: Dict[str, str]) -> Dict[str, Any]:
        """
        Recursively fill all {{PLACEHOLDER}} values in template.
        
        Args:
            template: Template dictionary with placeholders
            personas: Selected persona records
            dates: Generated dates
            parameters: Selected parameters
            case_numbers: Generated case numbers
            
        Returns:
            Hydrated template with placeholders filled
        """
        def replace_value(value):
            """Recursively replace placeholders in a value."""
            if isinstance(value, str) and '{{' in value:
                # Replace persona placeholders
                for persona_key, record in personas.items():
                    # Full name
                    value = value.replace(f'{{{{{persona_key}}}}}', 
                                        record.get('fullname', record.get('name', 'Unknown')))
                    
                    # ID reference
                    value = value.replace(f'{{{{{persona_key}.id}}}}', 
                                        record.get('contactid', record.get('accountid', 'unknown')))
                    
                    # Individual fields
                    value = value.replace(f'{{{{{persona_key}_FIRST}}}}',
                                        record.get('firstname', 'Unknown'))
                    value = value.replace(f'{{{{{persona_key}_LAST}}}}',
                                        record.get('lastname', 'Unknown'))
                    value = value.replace(f'{{{{{persona_key}_EMAIL}}}}',
                                        record.get('emailaddress1', 'unknown@example.com'))
                    value = value.replace(f'{{{{{persona_key}_PHONE}}}}',
                                        record.get('telephone1', '555-0000'))
                    value = value.replace(f'{{{{{persona_key}_JOBTITLE}}}}',
                                        record.get('jobtitle', 'Employee'))
                    
                    # Contact ID specifically named
                    if persona_key.startswith('PERSONA_'):
                        contact_key = 'CONTACT_' + persona_key[8:]  # Remove PERSONA_ prefix
                        value = value.replace(f'{{{{{contact_key}.id}}}}',
                                            record.get('contactid', record.get('accountid', 'unknown')))
                
                # Replace date placeholders
                for date_key, date_val in dates.items():
                    value = value.replace(f'{{{{{date_key}}}}}', 
                                        date_val.isoformat())
                
                # Replace parameter placeholders
                for param_key, param_val in parameters.items():
                    value = value.replace(f'{{{{{param_key}}}}}', 
                                        str(param_val))
                
                # Replace case number placeholders
                for num_key, num_val in case_numbers.items():
                    value = value.replace(f'{{{{{num_key}}}}}', num_val)
                
                return value
            
            elif isinstance(value, dict):
                return {k: replace_value(v) for k, v in value.items()}
            
            elif isinstance(value, list):
                return [replace_value(v) for v in value]
            
            else:
                return value
        
        return replace_value(template)
    
    # ========================================================================
    # Case Number Generation
    # ========================================================================
    
    def generate_case_numbers(self, module_path: str, template_name: str) -> Dict[str, str]:
        """
        Generate unique case numbers for this hydration.
        
        Args:
            module_path: Module path
            template_name: Template name
            
        Returns:
            Dictionary with generated case numbers
        """
        # Extract module prefix (e.g., DSP for disputes, CC for court cases)
        module_name = Path(module_path).name
        prefix_map = {
            'dispute-resolution': 'DSP',
            'court-case-management': 'CC',
            'hr-administration': 'HR',
            'asset-management': 'AST',
        }
        
        prefix = prefix_map.get(module_name, 'TST')
        year = datetime.now().year
        
        # Generate random case number (in production, would query for next sequential)
        case_num = random.randint(1, 9999)
        
        return {
            'CASE_NUMBER': f"{prefix}-{year}-{case_num:04d}",
            'CASE_NUMBER_INTAKE': f"INT-{year}-{case_num:04d}",
            'INVESTIGATION_NUMBER': f"INV-{prefix}-{year}-{case_num:04d}",
            'DETERMINATION_NUMBER': f"DET-{prefix}-{year}-{case_num:04d}",
        }
    
    # ========================================================================
    # Stage Truncation
    # ========================================================================
    
    def truncate_to_stage(self, event_stream: Dict[str, Any], target_stage: str) -> Dict[str, Any]:
        """
        Truncate event stream at specified stage marker.
        
        Args:
            event_stream: Hydrated event stream
            target_stage: Stage to truncate at (e.g., 'investigation_complete')
            
        Returns:
            Truncated event stream
        """
        stage_markers = event_stream.get('stage_markers', {})
        target_event_id = stage_markers.get(target_stage)
        
        if target_event_id is None:
            logger.warning(f"Stage marker '{target_stage}' not found, returning full stream")
            return event_stream
        
        # Filter events up to and including target event ID
        original_events = event_stream.get('events', [])
        truncated_events = [e for e in original_events if e.get('event_id', 999) <= target_event_id]
        
        event_stream['events'] = truncated_events
        event_stream['truncated_at_stage'] = target_stage
        event_stream['original_event_count'] = len(original_events)
        event_stream['truncated_event_count'] = len(truncated_events)
        
        logger.info(f"Truncated from {len(original_events)} to {len(truncated_events)} events at stage '{target_stage}'")
        
        return event_stream
    
    # ========================================================================
    # Main Hydration
    # ========================================================================
    
    def hydrate_template(self, template_path: Path, 
                        stage: Optional[str] = None) -> Dict[str, Any]:
        """
        Hydrate a template with real data.
        
        Args:
            template_path: Path to template YAML file
            stage: Optional stage to truncate at
            
        Returns:
            Hydrated event stream ready for execution
        """
        # Load template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        if not self.client or not self.record_pools:
            raise ValueError("Record pools not loaded. Call load_record_pools() first.")
        
        hydration_config = template.get('hydration', {})
        
        # Step 1: Select personas
        persona_mapping = hydration_config.get('persona_mapping', {})
        personas = self.select_personas(persona_mapping)
        logger.info(f"Selected {len(personas)} personas")
        
        # Step 2: Generate dates
        date_config = hydration_config.get('date_generation', {})
        dates = self.generate_dates(date_config)
        logger.info(f"Generated {len(dates)} dates")
        
        # Step 3: Select parameters
        param_config = hydration_config.get('parameters', {})
        parameters = self.select_parameters(param_config)
        logger.info(f"Selected {len(parameters)} parameters")
        
        # Step 4: Generate case numbers
        module_path = template.get('module', '')
        template_name = template.get('event_stream_template', 'unknown')
        case_numbers = self.generate_case_numbers(module_path, template_name)
        
        # Step 5: Fill all placeholders
        hydrated = self.fill_placeholders(template, personas, dates, parameters, case_numbers)
        
        # Step 6: Convert from template to executable event stream
        hydrated['is_template'] = False
        hydrated['event_stream_name'] = f"{template_name}-{uuid4().hex[:8]}"
        hydrated['hydration_timestamp'] = datetime.now().isoformat()
        hydrated['hydrated_from_template'] = str(template_path)
        
        # Step 7: Truncate if stage specified
        if stage:
            hydrated = self.truncate_to_stage(hydrated, stage)
        
        return hydrated
    
    # ========================================================================
    # Batch Generation
    # ========================================================================
    
    def generate_batch(self, template_path: Path, count: int,
                      stage_distribution: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Generate multiple hydrated event streams from one template.
        
        Args:
            template_path: Path to template file
            count: Number of variations to generate
            stage_distribution: Dict mapping stage names to percentages
                Example: {'intake_complete': 10, 'investigation_complete': 25, ...}
        
        Returns:
            List of hydrated event streams
        """
        streams = []
        
        # Normalize distribution to weights
        total = sum(stage_distribution.values())
        stages = list(stage_distribution.keys())
        weights = [stage_distribution[s] / total for s in stages]
        
        for i in range(count):
            try:
                # Select random stage based on distribution
                stage = random.choices(stages, weights=weights)[0]
                
                # Hydrate template with random selections
                hydrated = self.hydrate_template(template_path, stage=stage)
                
                # Add batch metadata
                hydrated['batch_index'] = i + 1
                hydrated['batch_total'] = count
                
                streams.append(hydrated)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{count} variations...")
                    
            except Exception as e:
                logger.error(f"Error generating variation {i + 1}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(streams)}/{count} variations")
        return streams
