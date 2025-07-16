from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import json

from services.chat_with_docs import talk_to_llm   
from services.play_ai import text_to_speech_bytes
from services.question_logger import QuestionLogger

from data.system_prompt_mcq import system_prompt
from models.evaluation_models import MCQFeedback


# MCQ chat ws
FILE_ID = "file-SojR7yGezXDhFY5Fpyqgtm"  
LOG_FILE_PATH = "logs/main_log.json"

router = APIRouter()

@router.websocket("/mcq")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("MCQ WebSocket connection established")
    
    logger = QuestionLogger(log_file_path=LOG_FILE_PATH)

    try:
        while True:
            try:
                message = await websocket.receive_text()
                print(f"MCQ message received: {message}")
                
                data = json.loads(message)
                questionId = data.get("questionId")
                answer = data.get("answer")
                
                print(f"Processing MCQ - ID: {questionId}, Answer: {answer}")
                
                response = talk_to_llm(input_text=f"Question number: {questionId} Answer: {answer}", 
                                       system_prompt=system_prompt, file_id = FILE_ID, response_format=MCQFeedback)

                parsed_response = response.output_parsed if hasattr(response, 'output_parsed') else response.dict()
                print(f"MCQ response: {parsed_response}")
                
                # log mcq correct answer
                if parsed_response.correct == True:
                    logger.log_single_variable(variable_name="correct_answers")
                                                       
                 # Generate audio and send to frontend
                audio_bytes = text_to_speech_bytes(parsed_response.feedback)
                    
                    # Send audio to frontend
                await websocket.send_bytes(audio_bytes)
                
            except WebSocketDisconnect:
                print("MCQ WebSocket disconnected")
                break
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                await websocket.send_text(f"Error: Invalid JSON format")
            except Exception as e:
                print(f"Error processing MCQ: {e}")
                await websocket.send_text(f"Error: {str(e)}")
                
    except WebSocketDisconnect:
        print("MCQ WebSocket disconnected")
    except Exception as e:
        print(f"MCQ WebSocket error: {e}")