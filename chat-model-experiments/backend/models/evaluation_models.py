from pydantic import BaseModel

class log(BaseModel):
    """Base model for log entries"""
    timestamp: str
    agent_type: str
    user_question: str
    llm_type: str

class ConversationLog(BaseModel):
    """Model for conversation logs"""
    score: int
    logs: list[log]
    
    
class FinalEvaluationResult(BaseModel):
    """Model for final evaluation data"""
    score: int
    feedback: str
    
class MCQFeedback(BaseModel):
    """Model for single MCQ feedback"""
    correct: bool
    feedback: str