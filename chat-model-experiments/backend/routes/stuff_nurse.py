from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import time
from io import BytesIO
from services.whisper import send_audio_to_whisper
from services.play_ai import text_to_speech_bytes
from services.chat_with_docs import talk_to_llm
from services.question_logger import QuestionLogger

from data.system_prompt_staff_nurse import system_prompt
from data.system_prompt_evaluation import staff_nurse_convo

FILE_ID = "file-VbYLyGHrYZcqirh1ZQBZnR"
CONVERSATION_TYPE = 'staff_nurse_conversation'

router = APIRouter()

@router.websocket("/stuff_nurse")
async def stuff_nurse_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Stuff Nurse WebSocket connection established")
    
    previous_response_id = None
    logger = QuestionLogger(system_prompt=staff_nurse_convo)
    
    try:
        while True:
            # Wait for audio data from client
            data = await websocket.receive_bytes()
            print(f"Stuff Nurse received audio data: {len(data)} bytes")
            
            try:
                # Transcribe audio to text
                text = send_audio_to_whisper(BytesIO(data), filename="audio.wav")
                print(f"Stuff Nurse transcribed: {text}")
                
                if text:
                    # Get response from LLM
                    response = talk_to_llm(text, system_prompt, FILE_ID, previous_response_id)
                    previous_response_id = response.id
                    response_text = response.output_text
                    print(f"Stuff Nurse LLM response: {response_text}")

                    logger.log_interaction(text, response_text, CONVERSATION_TYPE)

                    audio_bytes = text_to_speech_bytes(response_text)

                    await websocket.send_bytes(audio_bytes)

                else:
                    print("Stuff Nurse: No transcription result")
                    
            except Exception as e:
                print(f"Stuff Nurse processing error: {e}")
                
    except WebSocketDisconnect:
        print("Stuff Nurse WebSocket connection closed")
    except Exception as e:
        print(f"Stuff Nurse WebSocket error: {e}")
        await websocket.close()