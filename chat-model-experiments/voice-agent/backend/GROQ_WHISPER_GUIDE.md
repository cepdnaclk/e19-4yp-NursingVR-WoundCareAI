# Groq Voice Agent Integration Guide

This guide shows you how to integrate Groq's Whisper API (STT) and PlayAI (TTS) into your voice agent for a complete Groq-powered voice stack.

## 🚀 Why Use Groq Voice Models?

### Groq Whisper (STT)
- **⚡ Lightning Fast**: Groq's inference is significantly faster than standard APIs
- **🎯 High Accuracy**: Uses OpenAI's Whisper models with excellent transcription quality
- **💰 Cost Effective**: Competitive pricing for speech-to-text
- **🌍 Multi-language**: Supports 99+ languages

### Groq PlayAI (TTS)  
- **🔊 High Quality**: Neural voice synthesis with natural-sounding speech
- **⚡ Fast Generation**: Quick audio generation for real-time applications
- **� Voice Options**: Multiple voice personas available
- **🔌 Easy Integration**: Compatible with OpenAI's API format

## 📋 Available Models

### STT Models
| Model | Description | Best For |
|-------|-------------|----------|
| `whisper-large-v3-turbo` | Fastest inference | Real-time applications |
| `whisper-large-v3` | Highest accuracy | Batch processing |

### TTS Models  
| Model | Description | Voices |
|-------|-------------|--------|
| `playai-tts` | PlayAI neural TTS | Fritz-PlayAI, and more |

## 🛠️ Setup Instructions

### 1. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/keys)
2. Create an account or log in
3. Generate an API key

### 2. Install Dependencies
```bash
pip install httpx
```

### 3. Set Environment Variable
Add to your `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

Or set temporarily in PowerShell:
```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Update Your Voice Agent

You now have 3 configuration options in your `main.py`:

#### Option 1: Default OpenAI (Fallback)
```python
pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks())
)
```

#### Option 2: Full Groq Stack (STT + TTS)
```python
from services.groq_whisper_stt import GroqVoiceModelProvider
from agents.voice import VoicePipelineConfig

groq_provider = GroqVoiceModelProvider(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    stt_model="whisper-large-v3-turbo",  # Fast STT
    tts_model="playai-tts",              # PlayAI TTS  
    tts_voice="Fritz-PlayAI",            # PlayAI voice
    tts_provider="groq"                  # Use Groq for TTS
)
config = VoicePipelineConfig(model_provider=groq_provider)
pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()),
    config=config
)
print("✅ Using Full Groq Stack: Whisper STT + PlayAI TTS")
```

#### Option 3: Hybrid (Groq STT + OpenAI TTS)
```python
groq_provider = GroqVoiceModelProvider(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    stt_model="whisper-large-v3-turbo",  # Fast Groq STT
    tts_provider="openai"                # OpenAI TTS fallback
)
config = VoicePipelineConfig(model_provider=groq_provider)
pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()),
    config=config
)
print("✅ Using Hybrid: Groq Whisper STT + OpenAI TTS")
```

## 🧪 Testing Your Integration

Run the test script to verify everything works:

```bash
python test_groq_integration.py
```

Expected output:
```
🧪 GROQ WHISPER STT INTEGRATION TEST
==================================================
🧪 Testing Groq Whisper STT...
✅ Model created: whisper-large-v3-turbo
🎵 Transcribing test audio (sine wave)...
✅ Groq API connection successful!

🧪 Testing Groq Voice Provider...
✅ STT Model: whisper-large-v3-turbo
✅ TTS Model: gpt-4o-mini-tts
✅ Groq Voice Provider is ready!

📊 TEST RESULTS:
   STT Model: ✅ PASS
   Voice Provider: ✅ PASS

🎉 All tests passed! Groq Whisper is ready to use.
```

## ⚙️ Configuration Options

### Model Selection
```python
# For fastest real-time transcription
groq_model="whisper-large-v3-turbo"

# For highest accuracy
groq_model="whisper-large-v3"
```

### Language Settings
```python
# In your STT settings
settings = STTModelSettings(
    language="en",          # ISO-639-1 language code
    temperature=0.0,        # Lower = more deterministic
    prompt="Custom context"  # Guide the model's output
)
```

### Error Handling
The implementation includes automatic retry logic and proper error handling for:
- Network connectivity issues
- API rate limits
- Invalid audio formats
- Authentication errors

## 🔧 Advanced Configuration

### Custom Audio Processing
If you need to customize audio processing:

```python
# In groq_whisper_stt.py, modify _write_wav_file method
def _write_wav_file(self, file, audio_data: np.ndarray, sample_rate: int):
    # Custom audio preprocessing here
    # e.g., noise reduction, normalization, etc.
    pass
```

### Streaming Support
Current implementation processes audio in chunks. For true streaming:

```python
# Extend GroqWhisperTranscriptionSession
class RealTimeGroqSession(StreamedTranscriptionSession):
    def __init__(self, ...):
        # Implement real-time audio buffering
        # and periodic transcription
        pass
```

## 📊 Performance Comparison

### STT Models
| Provider | Latency | Accuracy | Cost | Languages |
|----------|---------|----------|------|-----------|
| OpenAI Whisper | ~2-3s | Excellent | $$$ | 99+ |
| Groq Whisper | ~0.5-1s | Excellent | $$ | 99+ |
| Local Whisper | ~1-5s | Excellent | Free* | 99+ |

### TTS Models  
| Provider | Latency | Quality | Cost | Voices |
|----------|---------|---------|------|--------|
| OpenAI TTS | ~1-2s | Excellent | $$$ | 6 voices |
| Groq PlayAI | ~1-2s | Very Good | $$ | Growing |
| Local TTS | ~2-5s | Good | Free* | Limited |

### Recommended Configurations
| Use Case | STT | TTS | Benefits |
|----------|-----|-----|----------|
| **Speed Priority** | Groq Whisper | Groq PlayAI | Fastest overall |
| **Quality Priority** | Groq Whisper | OpenAI | Best quality mix |
| **Cost Priority** | Groq Whisper | OpenAI | Balanced cost/quality |
| **Reliability** | OpenAI | OpenAI | Most mature |

*Free but requires local compute resources

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: Groq API error 401: Unauthorized
   ```
   **Solution**: Check your `GROQ_API_KEY` environment variable

2. **Audio Format Error**
   ```
   Error: Groq API error 400: Invalid audio format
   ```
   **Solution**: Ensure audio is in supported format (wav, mp3, etc.)

3. **Network Timeout**
   ```
   Error: Request timeout
   ```
   **Solution**: Check internet connection, audio file size

4. **Import Error**
   ```
   ModuleNotFoundError: No module named 'httpx'
   ```
   **Solution**: Run `pip install httpx`

### Debug Mode
Enable debug logging by adding:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Switching Back to OpenAI

To revert to OpenAI STT:

```python
# Comment out Groq configuration
# groq_provider = GroqVoiceModelProvider(...)

# Use default OpenAI
pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks())
)
```

## 🎯 Best Practices

1. **Use turbo model for real-time**: `whisper-large-v3-turbo`
2. **Set appropriate language**: Improves accuracy and speed
3. **Handle errors gracefully**: Implement fallback to OpenAI
4. **Monitor API usage**: Check Groq console for usage stats
5. **Cache frequent phrases**: Use prompt parameter for context

## 📈 Next Steps

1. **Test with your voice agent**: Run actual voice conversations
2. **Monitor performance**: Compare latency with OpenAI
3. **Optimize settings**: Tune temperature and prompts
4. **Consider hybrid approach**: Groq for STT, different provider for TTS

## 🆘 Support

- **Groq Documentation**: [console.groq.com/docs](https://console.groq.com/docs)
- **API Reference**: [console.groq.com/docs/api-reference](https://console.groq.com/docs/api-reference)
- **Discord Community**: [discord.gg/groq](https://discord.gg/groq)

---

**Your voice agent is now powered by Groq's lightning-fast Whisper! 🚀**
