import json
import os
import threading
from datetime import datetime
from typing import Dict, Any, List
from services.response_api import talk_to_llm

class QuestionLogger:
    def __init__(self, log_file_path: str, system_prompt: str = "" ):
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
    
    def _log_interaction_thread(self, user_question: str, llm_response: str, conversation_type: str) -> None:
        """
        Internal method to handle validation and logging in a separate thread.
        """
        try:
            input = ""

            if conversation_type == 'patient_model':
                input = f"""Nurse's Question: {user_question} Patient's Response: {llm_response}"""
            elif conversation_type == 'staff_nurse_model':
                input = f"""Student nurse's Question: {user_question} Staff nurse's Response: {llm_response}"""
            else:
                print(f"[Logger] Unknown agent type: {conversation_type}")
                return

            # Validate the interaction using LLM
            if not self.validate_interaction(input):
                print(f"[Logger] Validation failed for interaction: {conversation_type}")
                return
                
            interaction_data = {
                "timestamp": datetime.now().isoformat(),
                "model": conversation_type,
                "user_question": user_question,
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
            return
    
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
    
    def _log_single_variable_thread(self, variable_name: str) -> None:
        """Internal method to handle variable logging in a separate thread."""
        try:
            # Use custom path or default
            file_path = self.log_file_path
            print(f"[Logger] Logging variable '{variable_name}' to {file_path}")
            
            # Load existing data or create new list
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"[Logger] Loaded existing log data: {len(data)} entries")
                except (json.JSONDecodeError, FileNotFoundError):
                    data = []
            else:
                data = []
            
            # Find existing entry for this variable name
            found_entry = None
            for entry in data:
                if entry.get('variable_name') == variable_name:
                    found_entry = entry
                    break
            
            if found_entry:
                # Update existing entry by incrementing value
                found_entry['value'] += 1
                found_entry['timestamp'] = datetime.now().isoformat()  # Update timestamp
                print(f"[Logger] Updated existing variable '{variable_name}' to value: {found_entry['value']}")
            else:
                # Create new entry if not found
                new_entry = {
                    "variable_name": variable_name,
                    "value": 1
                }
                data.append(new_entry)
                print(f"[Logger] Created new variable '{variable_name}' with value: 1")
            
            # Save updated data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"[Logger] Successfully logged variable '{variable_name}'")
            
        except Exception as e:
            print(f"[Logger] Error logging variable: {e}")
            return
             
    def log_single_variable(self, variable_name: str) -> None:
        """Log a single variable to JSON file in a separate thread."""
        print(f"[Logger] Starting to log variable: {variable_name}")
        # Start logging in a separate thread
        thread = threading.Thread(
            target=self._log_single_variable_thread,
            args=(variable_name,),
            daemon=True
        )
        thread.start()
    
    def is_log_file_available(self) -> bool:
        try:
            return os.path.exists(self.log_file_path) and os.path.isfile(self.log_file_path)
        except Exception as e:
            print(f"[Logger] Error checking file: {e}")
            return False
    
    def create_log_file(self, initial_data: List[Dict[str, Any]] = None) -> bool:
        try:        
            # Use initial data or empty list
            data = initial_data if initial_data is not None else []
            
            # Create and write to the file
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"[Logger] Error creating log file: {e}")
            return False
    
    def add_entry_to_file(self, variable_name: str, value: int):
        """Add or update an entry in the log file"""
        data = []
        
        if os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = []
        else:
            data = []
        
        # Find existing entry for this variable name
        found_entry = None
        for entry in data:
            if entry.get('variable_name') == variable_name:
                found_entry = entry
                break
        
        if found_entry:
            # Update existing entry with new value
            found_entry['value'] = value
            found_entry['timestamp'] = datetime.now().isoformat()  # Update timestamp
            print(f"[Logger] Updated existing variable '{variable_name}' to value: {value}")
        else:
            # Create new entry if not found
            new_entry = {
                "variable_name": variable_name,
                "value": value,
                "timestamp": datetime.now().isoformat()  # Add timestamp for new entries
            }
            data.append(new_entry)
            print(f"[Logger] Created new variable '{variable_name}' with value: {value}")
        
        # Save updated data
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"[Logger] Successfully saved variable '{variable_name}' with value: {value}")
    
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
                agent = interaction.get('conversation_type', 'unknown')
                if agent not in stats['agents']:
                    stats['agents'][agent] = 0
                stats['agents'][agent] += 1
                
            return stats
            
        except Exception as e:
            print(f"[Logger] Error reading log stats: {e}")
            return {"total_interactions": 0, "agents": {}}