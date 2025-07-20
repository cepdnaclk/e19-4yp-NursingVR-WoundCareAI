import json
from typing import List

def convert_pydantic_to_str(filtered_logs):

    if hasattr(filtered_logs, 'model_dump'):
        # Single Pydantic model
        filtered_logs_str = json.dumps(filtered_logs.model_dump(), indent=2)
    elif hasattr(filtered_logs, 'dict'):
        # Single Pydantic model (older version)
        filtered_logs_str = json.dumps(filtered_logs.dict(), indent=2)
    elif isinstance(filtered_logs, list):
        # List of Pydantic models - convert each to dict
        converted_list = [log.model_dump() if hasattr(log, 'model_dump') else log.dict() for log in filtered_logs]
        filtered_logs_str = json.dumps(converted_list, indent=2)
    elif isinstance(filtered_logs, dict):
        # Regular dictionary
        filtered_logs_str = json.dumps(filtered_logs, indent=2)
    else:
        # Fallback to string representation
        filtered_logs_str = str(filtered_logs)
    
    return filtered_logs_str

def generate_simple_step_status_text(matrix: List[bool]) -> str:
    """Simple version without step names"""
    if not matrix:
        return "No steps defined."
    
    status_lines = []
    for i, completed in enumerate(matrix):
        status = "completed" if completed else "not completed"
        status_lines.append(f"{i}. {status}")
    
    return ",\n".join(status_lines)