from pydantic import BaseModel
from typing import Optional, List

class log(BaseModel):
    """Base model for log entries"""
    timestamp: str
    agent_type: str
    user_question: str

class ConversationLog(BaseModel):
    """Model for conversation logs"""
    logs: list[log]
    feedback: str
    
    
class FinalEvaluationResult(BaseModel):
    """Model for final evaluation data"""
    questions_not_covered: List[str]
    feedback: str
    
class MCQFeedback(BaseModel):
    """Model for single MCQ feedback"""
    correct: bool
    feedback: str
    

# step evaluation request model
class EvaluationStepRequest(BaseModel):
    matrix: Optional[List[bool]] = None