"""
Utility Functions - Shared helper functions used across routers and main module.

This module contains reusable helper functions for:
- Reading solution metadata (display name, version)
- Streaming PowerShell script output
"""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import json
import asyncio
import shutil
from config import PROJECT_ROOT


# Track active processes for potential cancellation
active_processes = {}


def read_solution_display_name(module_path: Path) -> str:
    """Read display name from Solution.xml file"""
    solution_xml_path = module_path / "src" / "Other" / "Solution.xml"
    
    if not solution_xml_path.exists():
        return None
    
    try:
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find the LocalizedName element with description attribute
        localized_name = root.find(".//LocalizedName[@languagecode='1033']")
        if localized_name is not None:
            display_name = localized_name.get('description')
            if display_name:
                display_name = display_name.strip()
                # Remove "App Base - " prefix if present
                if display_name.startswith("App Base - "):
                    display_name = display_name[11:]  # Remove "App Base - " (11 characters)
                return display_name
        
        return None
    except Exception as e:
        print(f"Error reading display name from {solution_xml_path}: {e}", file=sys.stderr)
        return None


def read_solution_version(module_path: Path) -> str:
    """Read version from Solution.xml file"""
    solution_xml_path = module_path / "src" / "Other" / "Solution.xml"
    
    if not solution_xml_path.exists():
        print(f"Version file not found: {solution_xml_path}", file=sys.stderr)
        return "1.0.0.0"  # Default version if not found
    
    try:
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find the Version element (no namespace in these files)
        version_elem = root.find(".//{http://www.w3.org/2001/XMLSchema-instance}Version")
        if version_elem is None:
            # Try without namespace
            version_elem = root.find(".//Version")
        
        if version_elem is not None and version_elem.text:
            version = version_elem.text.strip()
            
            # Normalize to 4-part version
            parts = version.split('.')
            while len(parts) < 4:
                parts.append('0')
            
            normalized = '.'.join(parts[:4])
            # print(f"Read version {version} -> {normalized} from {solution_xml_path}", file=sys.stderr)
            return normalized
        
        print(f"Version element not found in {solution_xml_path}", file=sys.stderr)
        return "1.0.0.0"
    except Exception as e:
        print(f"Error reading version from {solution_xml_path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return "1.0.0.0"


async def stream_powershell_output(script_path: str, *args, operation_id: str = None):
    """Stream PowerShell script output in real-time using subprocess with threading"""
    import subprocess
    import threading
    from queue import Queue
    
    try:
        # Try pwsh first, fall back to powershell
        powershell_cmd = "pwsh"
        if not shutil.which("pwsh"):
            powershell_cmd = "powershell"
        
        # Build PowerShell command
        cmd = [powershell_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
        
        # print(f"[DEBUG] Running command: {' '.join(cmd)}")
        
        # Use synchronous subprocess (Windows-compatible)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,
            cwd=str(PROJECT_ROOT)
        )
        
        # Track process for cancellation if operation_id provided
        if operation_id:
            active_processes[operation_id] = process
        
        # Use a queue to communicate between threads
        output_queue = Queue()
        
        def read_output():
            """Read output in a separate thread"""
            try:
                for line in process.stdout:
                    output_queue.put(('line', line.rstrip()))
            except Exception as e:
                output_queue.put(('error', str(e)))
            finally:
                output_queue.put(('done', None))
        
        # Start reading thread
        reader_thread = threading.Thread(target=read_output, daemon=True)
        reader_thread.start()
        
        # Stream output from queue
        while True:
            # Check queue with timeout to allow asyncio event loop to run
            try:
                import queue
                msg_type, msg_data = output_queue.get(timeout=0.1)
                
                if msg_type == 'line':
                    if msg_data:
                        yield f"data: {json.dumps({'type': 'output', 'line': msg_data})}\n\n"
                elif msg_type == 'error':
                    yield f"data: {json.dumps({'type': 'error', 'message': msg_data})}\n\n"
                    break
                elif msg_type == 'done':
                    break
                    
                await asyncio.sleep(0)  # Yield control to event loop
            except:
                # Timeout - continue loop to allow event loop to process
                await asyncio.sleep(0.01)
        
        # Wait for process to complete
        process.wait()
        
        # Remove from active processes
        if operation_id and operation_id in active_processes:
            del active_processes[operation_id]
        
        # Send completion status
        yield f"data: {json.dumps({'type': 'complete', 'exitCode': process.returncode})}\n\n"
        
    except Exception as e:
        error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        print(f"[ERROR] Stream exception: {error_msg}")  # Debug logging
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
