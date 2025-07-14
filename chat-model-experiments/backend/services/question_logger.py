import json
import os
import threading
from datetime import datetime
from typing import Dict, Any
from services.response_api import talk_to_llm

class QuestionLogger:
    def __init__(self, log_file_path: str = "logs/nursing_questions_log.json", system_prompt: str = "" ):
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.log_file_path = log_file_path
        self.validation_system_prompt = system_prompt
        
    def validate_interaction(self, validation_input: str) -> bool:
        """
        Use talk_to_llm to validate if the question and answer match.
        Returns True if they match, False otherwise.
        """
        try:
            
            print(f"[Logger] Validating interaction: {validation_input}")
            validation_response = talk_to_llm(
                input_text=validation_input,
                system_prompt=self.validation_system_prompt
            )

            print(f"[Logger] Validation response: {validation_response.output_text}")
            
            validation_result = validation_response.output_text.strip().upper()
            
            return validation_result == "MATCH"
            
        except Exception as e:
            print(f"[Logger] Validation error: {e}")
            return False
    
    def _log_interaction_thread(self, user_question: str, llm_response: str, agent_type: str):
        """
        Internal method to handle validation and logging in a separate thread.
        """
        try:
            input = ""

            if agent_type == 'patient_conversation':
                input = f"""Nurse's Question: {user_question} Patient's Response: {llm_response}"""
            elif agent_type == 'staff_nurse_conversation':
                input = f"""Student nurse's Question: {user_question} Staff nurse's Response: {llm_response}"""
            else:
                print(f"[Logger] Unknown agent type: {agent_type}")
                return

            # Validate the interaction using LLM
            if not self.validate_interaction(input):
                return
                
            interaction_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_type": agent_type,
                "user_question": user_question,
                "llm_response": llm_response
            }
            
            # Load existing data or create new list
            if os.path.exists(self.log_file_path):
                try:
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    data = []
            else:
                data = []
                
            # Add new interaction
            data.append(interaction_data)
            
            # Save updated data
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[Logger] Error in background logging: {e}")
    
    def log_interaction(self, user_question: str, llm_response: str, agent_type: str) -> None:
        """
        Log the interaction if it passes validation.
        Runs in a separate thread to avoid blocking the main application.
        """
        # Start logging in a separate thread
        thread = threading.Thread(
            target=self._log_interaction_thread,
            args=(user_question, llm_response, agent_type),
            daemon=True
        )
        thread.start()
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about logged interactions."""
        if not os.path.exists(self.log_file_path):
            return {"total_interactions": 0, "agents": {}}
            
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            stats = {
                "total_interactions": len(data),
                "agents": {},
                "recent_interactions": len([d for d in data if 
                    (datetime.now() - datetime.fromisoformat(d['timestamp'])).days < 1])
            }
            
            for interaction in data:
                agent = interaction.get('agent_type', 'unknown')
                if agent not in stats['agents']:
                    stats['agents'][agent] = 0
                stats['agents'][agent] += 1
                
            return stats
        except Exception as e:
            print(f"[Logger] Error reading log stats: {e}")
            return {"total_interactions": 0, "agents": {}}
