from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from io import BytesIO
import time

from services.whisper import send_audio_to_whisper
from services.response_api import talk_to_llm   
from services.play_ai import text_to_speech_bytes   
from services.question_logger import QuestionLogger

from data.sytem_prompt import system_prompt
from data.system_prompt_evaluation import patient_convo


# History gathering chat ws
CONVERSATION_TYPE = 'patient_conversation'
LOG_FILE_PATH = "logs/nursing_questions_log.json"

router = APIRouter()

@router.websocket("/history")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        previous_response_id = None
        logger = QuestionLogger(log_file_path=LOG_FILE_PATH, system_prompt=patient_convo)

        while True:
            try:
                message = await websocket.receive()
                print(f"Received message: {type(message)}, keys: {message.keys()}")
                
                if "bytes" in message:
                    audio_bytes = message["bytes"]
                    print(f"Audio received, size: {len(audio_bytes)} bytes")
                    
                    # Save audio to temporary file for debugging
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_file.write(audio_bytes)
                        temp_filename = temp_file.name 
                    
                    try:
                        text = send_audio_to_whisper(BytesIO(audio_bytes), filename="audio.wav")
                        print(f"Transcribed text: {text}")                     
                        # Clean up temp file
                        os.unlink(temp_filename)
            
                    except Exception as whisper_error:
                        print(f"Whisper transcription error: {whisper_error}")
                        os.unlink(temp_filename)
                        await websocket.send_text(f"Transcription error: {str(whisper_error)}")
                        continue
                    
                    response = talk_to_llm(previous_response_id=previous_response_id, input_text=text,  system_prompt=system_prompt)
                    print(f"Response from LLM: {response.output_text}")
                    previous_response_id = response.id

                    # Log interaction if it passes quality validation
                    logger.log_interaction(text, response.output_text, CONVERSATION_TYPE)

                    
                    # Generate audio and send to frontend
                    audio_bytes = text_to_speech_bytes(response.output_text)
                    
                    # Send audio to frontend
                    await websocket.send_bytes(audio_bytes)

                elif "text" in message:
                    text_data = message["text"]
                    print(f"Text message received: {text_data}")
                    await websocket.send_text(f"Text message received: {text_data}")
                else:
                    print(f"Unknown message type: {message}")
                    
            except WebSocketDisconnect:
                print("WebSocket disconnected")
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                await websocket.send_text(f"Error: {str(e)}")
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")