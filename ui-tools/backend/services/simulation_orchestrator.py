"""
Simulation Orchestrator

Orchestrates the execution of simulation files by:
- Loading and validating simulations
- Processing steps sequentially
- Managing execution context
- Building and executing Web API calls (or dry-run)
- Generating execution reports
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.simulation_parser import SimulationParser, DataModelLoader
from services.execution_context import ExecutionContext, DryRunContext, create_execution_context
from services.record_operations import RecordOperations, DryRunRecordOperations


class SimulationExecutionError(Exception):
    """Raised when simulation execution fails"""
    
    def __init__(self, step: int, action_index: int, message: str):
        self.step = step
        self.action_index = action_index
        self.message = message
        super().__init__(f"Step {step}, Action {action_index}: {message}")


class ExecutionReport:
    """Report of simulation execution"""
    
    def __init__(self):
        self.success = False
        self.simulation_name = ""
        self.module = ""
        self.started_at = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None
        self.dry_run = False
        
        self.total_steps = 0
        self.completed_steps = 0
        self.failed_step: Optional[int] = None
        
        self.total_actions = 0
        self.completed_actions = 0
        self.failed_action: Optional[int] = None
        
        self.records_created = 0
        self.records_updated = 0
        
        self.errors: List[Dict[str, Any]] = []
        self.step_details: List[Dict[str, Any]] = []
        
        self.execution_log: List[Dict[str, Any]] = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "success": self.success,
            "simulation_name": self.simulation_name,
            "module": self.module,
            "dry_run": self.dry_run,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "steps": {
                "total": self.total_steps,
                "completed": self.completed_steps,
                "failed": self.failed_step
            },
            "actions": {
                "total": self.total_actions,
                "completed": self.completed_actions,
                "failed": self.failed_action
            },
            "records": {
                "created": self.records_created,
                "updated": self.records_updated
            },
            "errors": self.errors,
            "step_details": self.step_details,
            "execution_log": self.execution_log
        }


class SimulationOrchestrator:
    """
    Orchestrates the execution of simulation files.
    
    Handles:
    - Validation before execution
    - Sequential step processing
    - Template variable resolution
    - Web API payload building
    - Error handling and reporting
    """
    
    def __init__(self, simulation_path: Path, module_path: Path):
        """
        Initialize orchestrator.
        
        Args:
            simulation_path: Path to simulation YAML file
            module_path: Path to module directory
        """
        self.simulation_path = simulation_path
        self.module_path = module_path
        
        # Initialize components
        self.data_loader = DataModelLoader(module_path)
        self.parser = SimulationParser(simulation_path, module_path)
        
        # Will be set during execution
        self.context: Optional[ExecutionContext] = None
        self.record_ops: Optional[RecordOperations] = None
        self.simulation_data: Dict[str, Any] = {}
        
    def validate(self) -> Dict[str, Any]:
        """
        Validate the simulation before execution.
        
        Returns:
            Validation result dictionary
        """
        return self.parser.validate().to_dict()
    
    def execute_dry_run(self) -> ExecutionReport:
        """
        Execute simulation in dry-run mode (no actual API calls).
        
        Returns:
            Execution report
        """
        return self._execute(dry_run=True)
    
    def execute(self) -> ExecutionReport:
        """
        Execute simulation with actual API calls.
        
        Returns:
            Execution report
            
        Note:
            Currently not implemented - always does dry-run.
            Future: Will make actual Dataverse Web API calls.
        """
        # For now, always do dry-run
        # Future: Implement actual Web API client integration
        return self._execute(dry_run=True)
    
    def _execute(self, dry_run: bool = True) -> ExecutionReport:
        """
        Internal execution method.
        
        Args:
            dry_run: If True, simulate execution without API calls
            
        Returns:
            Execution report
        """
        report = ExecutionReport()
        report.dry_run = dry_run
        
        try:
            # Load and validate simulation
            if not self.parser.load_simulation():
                raise SimulationExecutionError(0, 0, "Failed to load simulation file")
            
            self.simulation_data = self.parser.simulation_data
            report.simulation_name = self.simulation_data.get("execution_name", "")
            report.module = self.simulation_data.get("module", "")
            
            # Validate before execution
            validation_result = self.validate()
            if not validation_result["is_valid"]:
                report.errors.append({
                    "type": "validation",
                    "message": "Simulation failed validation",
                    "details": validation_result
                })
                report.completed_at = datetime.utcnow().isoformat()
                return report
            
            # Load data models
            if not self.data_loader.load():
                raise SimulationExecutionError(0, 0, "Failed to load data models")
            
            # Create execution context and record operations
            self.context = create_execution_context(dry_run=dry_run)
            
            if dry_run:
                self.record_ops = DryRunRecordOperations(self.module_path, self.data_loader)
            else:
                self.record_ops = RecordOperations(self.module_path, self.data_loader)
            
            # Get steps
            steps = self.simulation_data.get("steps", [])
            report.total_steps = len(steps)
            
            # Process each step sequentially
            for step_data in steps:
                step_num = step_data.get("step", 0)
                
                try:
                    step_report = self._execute_step(step_data, step_num)
                    report.step_details.append(step_report)
                    report.completed_steps += 1
                    
                    # Track actions
                    report.total_actions += step_report["total_actions"]
                    report.completed_actions += step_report["completed_actions"]
                    report.records_created += step_report["records_created"]
                    report.records_updated += step_report["records_updated"]
                    
                except SimulationExecutionError as e:
                    report.failed_step = e.step
                    report.failed_action = e.action_index
                    report.errors.append({
                        "type": "execution",
                        "step": e.step,
                        "action": e.action_index,
                        "message": e.message
                    })
                    
                    # Stop on error (fail-fast)
                    if self.simulation_data.get("metadata", {}).get("stop_on_error", True):
                        break
            
            # Mark as successful if all steps completed
            if report.completed_steps == report.total_steps:
                report.success = True
            
            # Add execution context summary
            if self.context:
                report.execution_log = self.context.execution_log
            
            # Add dry-run specific data
            if dry_run and isinstance(self.record_ops, DryRunRecordOperations):
                dry_run_summary = self.record_ops.get_simulation_summary()
                report.to_dict()["dry_run_details"] = dry_run_summary
            
        except Exception as e:
            report.errors.append({
                "type": "fatal",
                "message": str(e)
            })
        
        finally:
            report.completed_at = datetime.utcnow().isoformat()
        
        return report
    
    def _execute_step(self, step_data: Dict[str, Any], step_num: int) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            step_data: Step data from simulation
            step_num: Step number
            
        Returns:
            Step execution report
        """
        step_report = {
            "step": step_num,
            "title": step_data.get("title", ""),
            "persona": step_data.get("persona", ""),
            "total_actions": 0,
            "completed_actions": 0,
            "records_created": 0,
            "records_updated": 0,
            "actions": []
        }
        
        actions = step_data.get("actions", [])
        step_report["total_actions"] = len(actions)
        
        for action_idx, action in enumerate(actions):
            try:
                action_report = self._execute_action(action, step_num, action_idx)
                step_report["actions"].append(action_report)
                step_report["completed_actions"] += 1
                
                if action.get("action") == "create":
                    step_report["records_created"] += 1
                elif action.get("action") == "update":
                    step_report["records_updated"] += 1
                    
            except Exception as e:
                raise SimulationExecutionError(step_num, action_idx, str(e))
        
        # Mark step as complete
        if self.context:
            self.context.mark_step_complete(step_num)
        
        return step_report
    
    def _execute_action(self, action: Dict[str, Any], step: int, action_idx: int) -> Dict[str, Any]:
        """
        Execute a single action (create or update).
        
        Args:
            action: Action data from simulation
            step: Current step number
            action_idx: Action index within step
            
        Returns:
            Action execution report
        """
        action_type = action.get("action", "")
        table = action.get("table", "")
        store_as = action.get("store_as")
        
        action_report = {
            "action": action_type,
            "table": table,
            "store_as": store_as,
            "success": False
        }
        
        if action_type == "create":
            # Use dry-run or real record operations
            if isinstance(self.record_ops, DryRunRecordOperations):
                response = self.record_ops.simulate_create(action, self.context, step)
            else:
                # Future: Make actual Web API call
                # For now, always dry-run
                response = self.record_ops.simulate_create(action, self.context, step)
            
            action_report["record_id"] = response.get("id")
            action_report["success"] = True
            
        elif action_type == "update":
            # Use dry-run or real record operations
            if isinstance(self.record_ops, DryRunRecordOperations):
                response = self.record_ops.simulate_update(action, self.context, step)
            else:
                # Future: Make actual Web API call
                response = self.record_ops.simulate_update(action, self.context, step)
            
            action_report["record_id"] = response.get("id")
            action_report["success"] = True
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
        
        return action_report


def execute_simulation(simulation_path: Path, module_path: Path, dry_run: bool = True) -> Dict[str, Any]:
    """
    Convenience function to execute a simulation.
    
    Args:
        simulation_path: Path to simulation YAML file
        module_path: Path to module directory
        dry_run: If True, simulate without API calls
        
    Returns:
        Execution report dictionary
    """
    orchestrator = SimulationOrchestrator(simulation_path, module_path)
    
    if dry_run:
        report = orchestrator.execute_dry_run()
    else:
        report = orchestrator.execute()
    
    return report.to_dict()
