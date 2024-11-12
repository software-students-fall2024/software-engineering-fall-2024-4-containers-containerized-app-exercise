function analyzeSentence() {
  const sentence = document.getElementById('sentenceInput').value;

  fetch('/checkSentiment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ sentence })
  })
  .then(response => response.json())
  .then(data => {
    const analysis = data.analysis;
    displaySentiment(analysis);
  })
  .catch(error => console.error('Error:', error));
}

function displaySentiment(analysis) {
  const visualization = document.getElementById('visualization');
  visualization.textContent = `Sentiment Analysis: ${JSON.stringify(analysis)}`;
}

// Speech recognition
function startDictation() {
  if ('webkitSpeechRecognition' in window) {

      const recognition = new webkitSpeechRecognition();

      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.lang = 'en-US';
      recognition.start();

      recognition.onresult = function(e) {
          document.getElementById('sentenceInput').value = e.results[0][0].transcript;
          recognition.stop();
      };

      recognition.onerror = function(e) {
          recognition.stop();
      };
  } else {
      alert('Speech recognition not supported in this browser.');
  }
}
