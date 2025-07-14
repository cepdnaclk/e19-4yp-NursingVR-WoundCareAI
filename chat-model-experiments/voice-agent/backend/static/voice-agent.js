/**
 * Voice Agent Frontend JavaScript
 * Basic functionality for WebSocket communication and audio recording
 */

class VoiceAgent {
    constructor() {
        this.websocket = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        
        // Audio playback queue
        this.audioQueue = [];
        this.isPlaying = false;
        this.audioContext = null;
        
        // Timing tracking
        this.requestStartTime = null;
        this.firstResponseTime = null;
        this.dialogCount = 0;
        
        this.recordButton = document.getElementById('recordButton');
        this.statusDiv = document.getElementById('status');
        
        this.init();
    }
    
    async init() {
        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.updateStatus('Ready');
            
            // Initialize WebSocket
            this.connectWebSocket();
            
            // Setup event listeners
            this.setupEventListeners();
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.updateStatus('Error: Microphone access denied');
        }
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.updateStatus('Connected');
        };
        
        this.websocket.onmessage = (event) => {
            if (event.data instanceof Blob) {
                this.handleAudioResponse(event.data);
            } else if (typeof event.data === 'string') {
                try {
                    const message = JSON.parse(event.data);
                    this.handleTextMessage(message);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            }
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateStatus('Disconnected');
            setTimeout(() => this.connectWebSocket(), 1000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection error');
        };
    }
    
    setupEventListeners() {
        this.recordButton.addEventListener('mousedown', () => this.startRecording());
        this.recordButton.addEventListener('mouseup', () => this.stopRecording());
        this.recordButton.addEventListener('touchstart', () => this.startRecording());
        this.recordButton.addEventListener('touchend', () => this.stopRecording());
    }
    
    startRecording() {
        if (this.isRecording || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        this.isRecording = true;
        this.audioChunks = [];
        this.recordButton.textContent = 'Recording...';
        this.updateStatus('Recording...');
        
        // Use smaller timeslices for real-time streaming
        this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/webm' });
        
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
                // Optional: Send chunks in real-time for streaming
                // Uncomment the line below for real-time streaming:
                // this.sendAudioChunk(event.data);
            }
        };
        
        this.mediaRecorder.onstop = () => {
            this.sendAudioData();
        };
        
        // Start recording - will create one chunk when stopped
        this.mediaRecorder.start();
    }
    
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }
        
        this.isRecording = false;
        this.recordButton.textContent = 'Hold to Record';
        this.updateStatus('Processing...');
        
        this.mediaRecorder.stop();
    }
    
    async sendAudioData() {
        if (this.audioChunks.length === 0) {
            this.updateStatus('No audio recorded');
            return;
        }
        
        const audioBlob = new Blob(this.audioChunks);
        const arrayBuffer = await audioBlob.arrayBuffer();
        console.log(`array buffer size: ${arrayBuffer.byteLength}`);
        
        if (this.websocket.readyState === WebSocket.OPEN) {
            // Record the start time for latency measurement
            this.requestStartTime = performance.now();
            this.dialogCount++;
            this.firstResponseTime = null;
            
            console.log(`Dialog ${this.dialogCount}: Request sent at ${this.requestStartTime.toFixed(2)}ms`);
            
            // Send the complete audio recording as binary data
            this.websocket.send(arrayBuffer);
            this.updateStatus('Waiting for response...');
        } else {
            this.updateStatus('Connection lost');
        }
    }
    
    async handleAudioResponse(audioBlob) {
        try {
            // Calculate latency for first response
            if (this.requestStartTime && !this.firstResponseTime) {
                this.firstResponseTime = performance.now();
                const latency = this.firstResponseTime - this.requestStartTime;
                console.log(`Dialog ${this.dialogCount}: First response latency: ${latency.toFixed(2)}ms`);
                
                // Update status with latency info
                this.updateStatus(`Playing response... (${latency.toFixed(0)}ms latency)`);
            }
            
            const arrayBuffer = await audioBlob.arrayBuffer();
            
            // Initialize audio context if not already done
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            // Add to queue
            this.audioQueue.push(audioBuffer);
            
            // Start playing if not already playing
            if (!this.isPlaying) {
                this.playNextAudioChunk();
            }
            
        } catch (error) {
            console.error('Error handling audio response:', error);
            this.updateStatus('Error playing response');
        }
    }
    
    playNextAudioChunk() {
        if (this.audioQueue.length === 0) {
            this.isPlaying = false;
            this.updateStatus('Ready');
            return;
        }
        
        this.isPlaying = true;
        this.updateStatus('Playing response...');
        
        const audioBuffer = this.audioQueue.shift();
        const source = this.audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.audioContext.destination);
        
        source.onended = () => {
            // Play next chunk when current one ends
            this.playNextAudioChunk();
        };
        
        source.start();
    }
    
    // Method to get timing statistics
    getTimingStats() {
        return {
            dialogCount: this.dialogCount,
            lastLatency: this.firstResponseTime && this.requestStartTime ? 
                this.firstResponseTime - this.requestStartTime : null
        };
    }
    
    handleTextMessage(message) {
        switch (message.type) {
            case 'status':
                this.updateStatus(message.content);
                break;
            case 'error':
                console.error('Server error:', message.content);
                this.updateStatus(`Error: ${message.content}`);
                break;
            case 'transcript':
                console.log('Transcript:', message.content);
                // You can display the transcript to the user
                break;
            default:
                console.log('Unknown message type:', message);
        }
    }
    
    updateStatus(message) {
        this.statusDiv.textContent = message;
    }
}

// Initialize the voice agent when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceAgent();
});
