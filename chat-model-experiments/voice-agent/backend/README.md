# Voice Agent Backend

A FastAPI backend for real-time voice conversations with low latency, integrated with the OpenAI agents framework.

## Features

- **WebSocket-based real-time communication**
- **Voice recording and playback** in the browser
- **Streaming audio responses** for minimal latency
- **Multi-agent support** with handoffs (English ↔ Spanish)
- **Function calling** (weather queries)
- **Health check endpoint**
- **Ready for Fly.io deployment**

## Agent Capabilities

### Main Assistant Agent
- General conversation and questions
- Weather queries using the `get_weather` tool
- Automatic handoff to Spanish agent when user speaks Spanish

### Spanish Agent
- Handles Spanish language conversations
- Seamless handoff from main agent

### Example Interactions
- "Tell me a joke"
- "What's the weather in Tokyo?"
- "Hola, como estas?" (triggers handoff to Spanish agent)

## Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. **Run the application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Open your browser** and go to `http://localhost:8000`

## Usage

1. **Allow microphone access** when prompted
2. **Hold the "Hold to Record" button** and speak
3. **Release the button** to send the audio
4. **The response will stream back** and play automatically

## Deployment to Fly.io

1. **Install Fly CLI and authenticate:**
```bash
flyctl auth login
```

2. **Deploy the application:**
```bash
flyctl deploy
```

## API Endpoints

- `GET /` - Home page with voice interface
- `WS /ws` - WebSocket endpoint for voice conversation
- `GET /health` - Health check endpoint

## Architecture

### Audio Processing Pipeline
1. **Frontend** captures audio (WebM format)
2. **Backend** converts WebM to numpy array using librosa
3. **Voice Pipeline** processes audio through agents
4. **Response** converted back to WAV and streamed to frontend

### Low Latency Optimizations
- **WebSocket communication** for real-time data exchange
- **Audio streaming** in chunks as soon as available
- **Optimized audio encoding** (WebM with Opus codec)
- **Immediate audio playback** using Web Audio API
- **Minimal buffering** and processing delays

## Integration with OpenAI Implementation

This backend integrates the agent configuration from the `openai-implementation` folder:

- **Agent definitions** with proper instructions and models
- **Function tools** (weather API)
- **Multi-agent handoffs** (English ↔ Spanish)
- **Workflow callbacks** for monitoring

The original console-based interaction has been adapted for web-based real-time communication while preserving all agent capabilities.
