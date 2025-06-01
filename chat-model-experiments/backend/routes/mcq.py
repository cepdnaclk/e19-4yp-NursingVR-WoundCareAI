from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import json

from services.chat_with_docs import talk_to_llm   
from services.play_ai import text_to_speech_and_play
from services.gpt_tts import text_to_speech_and_play_openai


# MCQ chat ws

router = APIRouter()

@router.websocket("/mcq")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            questionId = data.get("questionId")
            question = data.get("question")
            answer = data.get("answer")
            response = talk_to_llm(input_text=f"Question number: {questionId} Answer: {answer}")
            print(f"Response from LLM: {response.output_text}")
            text_to_speech_and_play_openai(response.output_text)

    except WebSocketDisconnect:
        print("WebSocket disconnected")