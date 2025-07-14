// Use the current host to connect WebSocket (works for both local and deployed)
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.host;

// MCQ WebSocket connection
const ws = new WebSocket(`${protocol}//${host}/mcq`);

// Second agent WebSocket connection
const ws2 = new WebSocket(`${protocol}//${host}/stuff_nurse`);

// MCQ WebSocket event handlers
ws.onopen = function(event) {
    console.log('MCQ WebSocket connected');
    document.getElementById("sendBtn").disabled = false;
};

ws.onmessage = function(event) {
    console.log('MCQ response from server:', event.data);
};

ws.onerror = function(error) {
    console.error('MCQ WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('MCQ WebSocket closed:', event.code, event.reason);
    document.getElementById("sendBtn").disabled = true;
};

// Second agent WebSocket event handlers
ws2.onopen = function(event) {
    console.log('Agent2 WebSocket connected');
    document.getElementById("sendAgent2Btn").disabled = false;
};

ws2.onmessage = function(event) {
    console.log('Agent2 response from server:', event.data);
};

ws2.onerror = function(error) {
    console.error('Agent2 WebSocket error:', error);
};

ws2.onclose = function(event) {
    console.log('Agent2 WebSocket closed:', event.code, event.reason);
    document.getElementById("sendAgent2Btn").disabled = true;
};

// MCQ button configuration
document.getElementById("sendBtn").onclick = function () {
  console.log("Sending MCQ data to WebSocket server...");
  const questionId = 2;
  const answer = "Cleaning the wound with saline(Docsity)";
  const question = "What is the first step in wound assessment?";

  const payload = {
    questionId: questionId,
    answer: answer,
    question: question,
  };

  ws.send(JSON.stringify(payload));
};

// Second agent button configuration
document.getElementById("sendAgent2Btn").onclick = function () {
  console.log("Sending data to Agent2 WebSocket server...");
  const requestId = Date.now();
  const query = "What are the key principles of wound care?";
  const context = "nursing_education";

  const payload = {
    requestId: requestId,
    query: query,
    context: context,
    timestamp: new Date().toISOString()
  };

  ws2.send(JSON.stringify(payload));
};
