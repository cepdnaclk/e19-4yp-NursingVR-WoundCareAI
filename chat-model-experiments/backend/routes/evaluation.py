from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
import json
import os
from typing import Optional, List, Dict, Any

from services.chat_with_docs import talk_to_llm
from services.play_ai import text_to_speech_bytes
from data.system_prompt_final_ev import qanda, remove_logs_system_prompt

from models.evaluation_models import ConversationLog, FinalEvaluationResult
from utils.conversions import convert_pydantic_to_str


router = APIRouter()

# Configuration for patient conversation evaluation
EVALUATION_CONFIG = {
    "conversation": {
        "log_file": "logs/nursing_questions_log.json",
        "system_prompt": [remove_logs_system_prompt, qanda],
        "file_id": "file-FkWmcQ72YcZLF9aZaDSMZ2"
    },
    "wound_assesment":{
        "log_file": "logs/nursing_questions_log.json",
        "system_prompt": "sss",
        "file_id": "file-FkWmcQ72YcZLF9aZaDSMZ2"
    }
}

NUMBER_OF_QUESTIONS = 8
FILE_PATH_MCQ = "logs/main_log.json"

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
        
        # Format logs for evaluation
        json_logs = json.dumps(logs, indent=2) 
        
        # Send to LLM for get filtered logs.
        response = talk_to_llm(
            input_text=json_logs,
            system_prompt=EVALUATION_CONFIG["conversation"]["system_prompt"][0],
            file_id=EVALUATION_CONFIG["conversation"]["file_id"],
            response_format=ConversationLog
        )

        # access the response.logs from conversationLog object (Works only for this response format)
        
        filtered_logs =  response.output_parsed.logs if hasattr(response.output_parsed, 'logs') else response.dict()
        
        filtered_logs_str = convert_pydantic_to_str(filtered_logs)
        print(filtered_logs_str)        
        
        # Send to LLM for final evaluation
        response = talk_to_llm(
            input_text=filtered_logs_str,
            system_prompt=EVALUATION_CONFIG["conversation"]["system_prompt"][1],
            file_id=EVALUATION_CONFIG["conversation"]["file_id"],
            response_format=FinalEvaluationResult
        )
        
        # Extract the parsed output and convert it to dict
        evaluation_data = response.output_parsed.model_dump() if hasattr(response.output_parsed, 'model_dump') else response.output_parsed.dict()

            
        print(f"Evaluation Data: {evaluation_data['feedback']}")    
        # Generate audio and send to frontend
        audio_bytes = text_to_speech_bytes(evaluation_data['feedback'])
        
        
        
        # Send audio to frontend
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=evaluation_feedback.mp3",
                "X-Evaluation-Data": json.dumps(evaluation_data['feedback']) 
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

@router.get("/evaluate/mcq")
async def evaluate_mcq():
    """Evaluate MCQ session"""
    print("Evaluating MCQ session...")
    correct_answers = get_variable_value(log_file_path=FILE_PATH_MCQ, variable_name="correct_answers")
    
    mcq_marks = (correct_answers/ NUMBER_OF_QUESTIONS) * 100 
    
    return JSONResponse(
        status_code=200,
        content={
            "evaluation": "MCQ evaluation completed",
            "marks": mcq_marks,
            "feedback": f"You answered {correct_answers} out of {NUMBER_OF_QUESTIONS} questions correctly."
        }
    )
    

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


def get_variable_value(variable_name: str,  log_file_path: str) -> int:
    """
    Get the current value of a specific variable from the log file.
    Uses the existing load_log_file function.
    """
    try:   
        # Load data using the existing function
        data = load_log_file(log_file_path)
        
        # Find the variable entry
        for entry in data:
            if entry.get('variable_name') == variable_name:
                value = entry.get('value', 0)
                print(f"[Logger] Found variable '{variable_name}' with value: {value}")
                return value
                
        print(f"[Logger] Variable '{variable_name}' not found in log file")
        return 0
        
    except Exception as e:
        print(f"[Logger] Error getting variable value: {e}")
        return 0
