document.getElementById('evaluateBtn').addEventListener('click', function() {
    startEvaluation();
})


// Add this function to handle evaluation request
async function startEvaluation() {
    try {
        const response = await fetch('/evaluate/patient-conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Get evaluation data from response headers
        const evaluationData = JSON.parse(response.headers.get('X-Evaluation-Data') || '{}');
        
        // Get audio blob from response
        const audioBlob = await response.blob();
        // Play the audio
        playAudioFromBlob(audioBlob);
        
    } catch (error) {
        console.error('Evaluation error:', error);
    }
}

// Function to play audio from blob
function playAudioFromBlob(audioBlob) {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
  
    audio.onloadeddata = function() {
        console.log('Audio loaded, starting playback');
        audio.play().catch(e => console.error('Audio playback failed:', e));
    };
    
    audio.onended = function() {
        URL.revokeObjectURL(audioUrl); // Clean up memory
    };
    
    audio.onerror = function(e) {
        console.error('Audio error:', e);
        URL.revokeObjectURL(audioUrl);
    };
}

// Function to display evaluation results
function displayEvaluationResult(evaluationData) {
    const evaluationDiv = document.getElementById('evaluation-result');
    evaluationDiv.innerHTML = `
        <h3>Evaluation Result</h3>
        <p><strong>Score:</strong> ${evaluationData.score || 'N/A'}</p>
        <p><strong>Feedback:</strong> ${evaluationData.feedback || 'N/A'}</p>
    `;
}