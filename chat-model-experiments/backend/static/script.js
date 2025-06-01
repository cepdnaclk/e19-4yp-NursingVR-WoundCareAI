let mediaRecorder;
let audioChunks = [];

const ws = new WebSocket("ws://localhost:8000/history");

document.getElementById("recordBtn").onclick = async function () {
  audioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.start();

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    audioBlob.arrayBuffer().then((buffer) => {
      ws.send(buffer); // Send recorded audio as binary
    });
    console.log("audioBlob", audioBlob);
  };

  this.disabled = true;
  document.getElementById("stopBtn").disabled = false;
};

document.getElementById("stopBtn").onclick = function () {
  mediaRecorder.stop();
  this.disabled = true;
  document.getElementById("recordBtn").disabled = false;
};
