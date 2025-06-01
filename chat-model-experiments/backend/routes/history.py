from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from io import BytesIO

from services.whisper import send_audio_to_whisper
from services.response_api import talk_to_llm   
from services.play_ai import text_to_speech_and_play    

# History gathering chat ws

router = APIRouter()

@router.websocket("/history")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:

        previous_response_id = None

        while True:
            message = await websocket.receive()
            if "bytes" in message:
                audio_bytes = message["bytes"]
                text = send_audio_to_whisper(BytesIO(audio_bytes), filename="audio.wav")
                response = talk_to_llm(previous_response_id=previous_response_id, input_text=text)
                print(f"Response from LLM: {response.output_text}")
                previous_response_id = response.id

                text_to_speech_and_play(response.output_text)

                await websocket.send_text("Audio file received and processed!")
            elif "text" in message:
                await websocket.send_text(f"Text message received: {message['text']}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")