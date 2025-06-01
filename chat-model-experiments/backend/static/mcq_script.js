const ws = new WebSocket("ws://localhost:8000/mcq");

document.getElementById("sendBtn").onclick = function () {
  console.log("Sending data to WebSocket server...");
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
