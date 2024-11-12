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
      displaySentiment(data.sentiment);
    })
    .catch(error => console.error('Error:', error));
  }
  
  function displaySentiment(sentiment) {
    const visualization = document.getElementById('visualization');
    visualization.textContent = `Sentiment: ${sentiment}`;
  }
  