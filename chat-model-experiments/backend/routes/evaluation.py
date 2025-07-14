from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from typing import Optional, List, Dict, Any


from services.chat_with_docs import talk_to_llm
from data.system_prompt_final_ev import qanda


router = APIRouter()

# Configuration for patient conversation evaluation
EVALUATION_CONFIG = {
    "conversation": {
        "log_file": "logs/nursing_questions_log.json",
        "system_prompt": qanda,
        "file_id": "file-FkWmcQ72YcZLF9aZaDSMZ2"
    },
    "wound_assesment":{
        "log_file": "logs/nursing_questions_log.json",
        "system_prompt": "sss",
        "file_id": "file-VbYLyGHrYZcqirh1ZQBZnR"
    }
}



def load_log_file(file_path: str) -> List[Dict[str, Any]]:
    """Load and return log file contents"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Log file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in log file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")

def filter_logs_by_agent(logs: List[Dict[str, Any]], agent_type: str) -> List[Dict[str, Any]]:
    """Filter logs by agent type"""
    return [log for log in logs if log.get('agent_type') == agent_type]

def format_logs_for_evaluation(logs: List[Dict[str, Any]]) -> str:
    """Format logs into a readable text for LLM evaluation"""
    formatted_text = "CONVERSATION LOGS FOR EVALUATION:\n\n"
    
    for i, log in enumerate(logs, 1):
        formatted_text += f"--- Interaction {i} ---\n"
        formatted_text += f"User Question: {log.get('user_question', 'N/A')}\n"
        formatted_text += f"LLM Response: {log.get('llm_response', 'N/A')}\n\n"
    
    return formatted_text

@router.post("/evaluate/patient-conversation")
async def evaluate_patient_conversation(agent_filter: Optional[str] = "history"):
    """Evaluate patient conversation logs"""
    try:
        # Load log file
        logs = load_log_file(EVALUATION_CONFIG["conversation"]["log_file"])
               
        if not logs:
            return JSONResponse(
                status_code=200,
                content={"evaluation": "No logs found for evaluation"}
            )
        
        # Format logs for evaluation (choose one of these options)
        # Option 1: Readable format
        formatted_logs = format_logs_for_evaluation(logs)
        
        # Option 2: JSON string format (uncomment to use)
        # formatted_logs = json.dumps(logs, indent=2)
        
        # Send to LLM for evaluation
        response = talk_to_llm(
            input_text=formatted_logs,
            system_prompt=EVALUATION_CONFIG["conversation"]["system_prompt"],
            file_id=EVALUATION_CONFIG["conversation"]["file_id"],
            response_format={"type": "json_object"}
        )

        print(f"Evaluation response: {response.output_text}")
        
        return JSONResponse(
            status_code=200,
            content={"evaluation": response.output_text}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

@router.get("/evaluate/available-agents")
async def get_available_agents():
    """Get list of available agent types from log files"""
    try:
        if not os.path.exists(EVALUATION_CONFIG["conversation"]["log_file"]):
            return JSONResponse(
                status_code=200,
                content={"agents": []}
            )
        
        logs = load_log_file(EVALUATION_CONFIG["conversation"]["log_file"])
        
        # Get unique agent types
        agent_types = list(set(log.get('agent_type', 'unknown') for log in logs))
        
        return JSONResponse(
            status_code=200,
            content={"agents": agent_types}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent types: {str(e)}")
