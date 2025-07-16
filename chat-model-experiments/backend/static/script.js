// hello babes

let mediaRecorder;
let audioChunks = [];
let requestStartTime = null;
let currentRecordingWebSocket = null;

// Use the current host to connect WebSocket (works for both local and deployed)
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.host;

// Audio chat WebSocket (existing)
const ws = new WebSocket(`${protocol}//${host}/history`);

// MCQ WebSocket
const wsMCQ = new WebSocket(`${protocol}//${host}/mcq`);

// Agent2 WebSocket
const wsStuffNurse = new WebSocket(`${protocol}//${host}/stuff_nurse`);

// Set binary type to handle binary data properly
ws.binaryType = 'blob'; // This ensures binary data comes as Blob
wsStuffNurse.binaryType = 'blob'; // Set binary type for Agent2 as well

// Audio chat WebSocket event handlers
ws.onopen = function(event) {
    console.log('Audio WebSocket connected');
};

ws.onmessage = function(event) {
    // Calculate response time if we have a start time
    if (requestStartTime !== null) {
        const responseTime = Date.now() - requestStartTime;
        console.log(`🕒 Response Time: ${responseTime}ms`);
        requestStartTime = null; // Reset for next request
    }
    
    console.log('Message from audio server:', typeof event.data, 'instanceof Blob:', event.data instanceof Blob);
    
    if (event.data instanceof Blob) {
        // Handle audio data (binary data comes as Blob)
        console.log('Received audio data, size:', event.data.size);
        playAudioFromBlob(event.data);
    } else if (event.data instanceof ArrayBuffer) {
        // Handle audio data (if somehow comes as ArrayBuffer)
        console.log('Received audio data as ArrayBuffer, size:', event.data.byteLength);
        playAudioFromBytes(event.data);
    } else {
        // Handle text message
        console.log('Text message:', event.data);
    }
};

ws.onerror = function(error) {
    console.error('Audio WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('Audio WebSocket closed:', event.code, event.reason);
};

// MCQ WebSocket event handlers
wsMCQ.onopen = function(event) {
    console.log('MCQ WebSocket connected');
    const btn = document.getElementById("sendBtn");
    if (btn) btn.disabled = false;
};

wsMCQ.onmessage = function(event) {
    if (event.data instanceof Blob) {
        // Handle audio data (binary data comes as Blob)
        console.log('Received audio data, size:', event.data.size);
        playAudioFromBlob(event.data);
    } else if (event.data instanceof ArrayBuffer) {
        // Handle audio data (if somehow comes as ArrayBuffer)
        console.log('Received audio data as ArrayBuffer, size:', event.data.byteLength);
        playAudioFromBytes(event.data);
    } else {
        // Handle text message
        console.log('Text message:', event.data);
    }
};

wsMCQ.onerror = function(error) {
    console.error('MCQ WebSocket error:', error);
};

wsMCQ.onclose = function(event) {
    console.log('MCQ WebSocket closed:', event.code, event.reason);
    const btn = document.getElementById("sendBtn");
    if (btn) btn.disabled = true;
};

// Agent2 WebSocket event handlers
wsStuffNurse.onopen = function(event) {
    console.log('Agent2 WebSocket connected');
    const btn = document.getElementById("recordAgent2Btn");
    if (btn) btn.disabled = false;
};

wsStuffNurse.onmessage = function(event) {
    console.log('Agent2 response from server:', event.data);
    
    if (event.data instanceof Blob) {
        // Handle audio data (binary data comes as Blob)
        console.log('Received Agent2 audio data, size:', event.data.size);
        playAudioFromBlob(event.data);
    } else if (event.data instanceof ArrayBuffer) {
        // Handle audio data (if somehow comes as ArrayBuffer)
        console.log('Received Agent2 audio data as ArrayBuffer, size:', event.data.byteLength);
        playAudioFromBytes(event.data);
    } else {
        // Handle text message
        console.log('Agent2 text message:', event.data);
    }
};

wsStuffNurse.onerror = function(error) {
    console.error('Agent2 WebSocket error:', error);
};

wsStuffNurse.onclose = function(event) {
    console.log('Agent2 WebSocket closed:', event.code, event.reason);
    const btn = document.getElementById("recordAgent2Btn");
    if (btn) btn.disabled = true;
};

// Reusable function to play audio from Blob
function playAudioFromBlob(audioBlob) {
    try {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play().then(() => {
            console.log('Audio playback started');
        }).catch(error => {
            console.error('Error playing audio:', error);
        });
        
        // Clean up the URL after playback
        audio.addEventListener('ended', () => {
            URL.revokeObjectURL(audioUrl);
        });
    } catch (error) {
        console.error('Error creating audio from blob:', error);
    }
}

// Reusable function to play audio from bytes
function playAudioFromBytes(audioBuffer) {
    try {
        const audioBlob = new Blob([audioBuffer], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play().then(() => {
            console.log('Audio playback started');
        }).catch(error => {
            console.error('Error playing audio:', error);
        });
        
        // Clean up the URL after playback
        audio.addEventListener('ended', () => {
            URL.revokeObjectURL(audioUrl);
        });
    } catch (error) {
        console.error('Error creating audio from bytes:', error);
    }
}

// Reusable function to start audio recording
async function startAudioRecording(targetWebSocket, recordButton, stopButton) {
    audioChunks = [];
    currentRecordingWebSocket = targetWebSocket;
    
    try {
        // Request higher quality audio
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 16000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            } 
        });
        
        // Use better audio format if supported
        const options = {};
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options.mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
            options.mimeType = 'audio/wav';
        }
        
        mediaRecorder = new MediaRecorder(stream, options);
        console.log('Recording with MIME type:', mediaRecorder.mimeType);
        
        mediaRecorder.start();
        console.log('Recording started');

        mediaRecorder.ondataavailable = (event) => {
            console.log('Audio chunk received, size:', event.data.size);
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            console.log('Recording stopped, processing...');
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            console.log('Audio blob created, size:', audioBlob.size, 'type:', audioBlob.type);
            
            // Send audio when recording stops (triggered by stop button)
            audioBlob.arrayBuffer().then((buffer) => {
                console.log('Sending audio buffer, size:', buffer.byteLength);
                
                // Mark the start time when sending the request
                requestStartTime = Date.now();
                console.log('🚀 Request sent at:', new Date(requestStartTime).toISOString());
                
                currentRecordingWebSocket.send(buffer); // Send recorded audio as binary
            }).catch(error => {
                console.error('Error converting audio to buffer:', error);
            });
        };

        recordButton.disabled = true;
        stopButton.disabled = false;
        
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error accessing microphone: ' + error.message);
    }
}

// Reusable function to stop audio recording and send audio
function stopAudioRecording(recordButton, stopButton) {
    try {
        console.log('Stopping recording...');
        mediaRecorder.stop(); // This will trigger onstop event which sends the audio
        
        // Stop all tracks to release microphone
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        stopButton.disabled = true;
        recordButton.disabled = false;
        
    } catch (error) {
        console.error('Error stopping recording:', error);
    }
}

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('WebSocket closed:', event.code, event.reason);
};



// Initialize buttons and event handlers when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize buttons as disabled until connections are established
    const sendBtn = document.getElementById("sendBtn");
    const recordAgent2Btn = document.getElementById("recordAgent2Btn");
    const stopAgent2Btn = document.getElementById("stopAgent2Btn");
    
    if (sendBtn) sendBtn.disabled = true;
    if (recordAgent2Btn) recordAgent2Btn.disabled = true;
    if (stopAgent2Btn) stopAgent2Btn.disabled = true;

    // Original audio chat button handlers
    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    
    if (recordBtn) {
        console.log("Setting up Agent2 button handler");
        recordBtn.onclick = async function () {
            await startAudioRecording(ws, this, document.getElementById("stopBtn"));
        };
    }
    
    if (stopBtn) {
        stopBtn.onclick = function () {
            stopAudioRecording(document.getElementById("recordBtn"), this);
        };
    }

    // MCQ button handler
    if (sendBtn) {
        sendBtn.onclick = function () {
            console.log("Sending MCQ data to WebSocket server...");
            const questionId = 1;
            const answer = "Surgical Wound";
            const question = "What is the type of wound shown in the scenario? (Select all that apply)";

            const payload = {
                questionId: questionId,
                answer: answer,
                question: question,
            };

            wsMCQ.send(JSON.stringify(payload));
        };
    }

    // Agent2 button handlers
    if (recordAgent2Btn) {
        console.log("Setting up Agent2 button handler");
        recordAgent2Btn.onclick = async function () {
            console.log("agent 2 button clicked");
            await startAudioRecording(wsStuffNurse, this, document.getElementById("stopAgent2Btn"));
        };
    }

    if (stopAgent2Btn) {
        stopAgent2Btn.onclick = function () {
            stopAudioRecording(document.getElementById("recordAgent2Btn"), this);
        };
    }
});
