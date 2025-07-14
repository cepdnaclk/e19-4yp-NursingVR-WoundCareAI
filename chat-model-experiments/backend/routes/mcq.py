from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import json

from services.chat_with_docs import talk_to_llm   
from services.play_ai import text_to_speech_and_play
from services.gpt_tts import text_to_speech_and_play_openai

from data.system_prompt_mcq import system_prompt


# MCQ chat ws
FILE_ID = "file-UTGTAsAD4G9XSfAasxYqRj"  # Example file ID, replace with actual file ID if needed

router = APIRouter()

@router.websocket("/mcq")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("MCQ WebSocket connection established")

    try:
        while True:
            try:
                message = await websocket.receive_text()
                print(f"MCQ message received: {message}")
                
                data = json.loads(message)
                questionId = data.get("questionId")
                question = data.get("question")
                answer = data.get("answer")
                
                print(f"Processing MCQ - ID: {questionId}, Answer: {answer}")
                
                response = talk_to_llm(input_text=f"Question number: {questionId} Answer: {answer}", system_prompt=system_prompt, file_id = FILE_ID)
                print(f"Response from LLM: {response.output_text}")
                
                text_to_speech_and_play_openai(response.output_text)
                
                await websocket.send_text(f"MCQ processed: {response.output_text}")
                
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