const recordButton = document.getElementById('record-button');
const resultDiv = document.getElementById('result');

let mediaRecorder;
let audioChunks = [];

recordButton.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        recordButton.style.backgroundColor = 'red';
    } else {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                let options = { mimeType: 'audio/webm' };

                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options = { mimeType: 'audio/ogg; codecs=opus' };
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options = { mimeType: '' };
                    }
                }

                mediaRecorder = new MediaRecorder(stream, options);
                mediaRecorder.start();
                recordButton.style.backgroundColor = 'green';

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
                    audioChunks = [];

                    // Send the audio blob to the ML client
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'audio.webm');

                    fetch('http://localhost:5001/classify', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            resultDiv.textContent = 'Error: ' + data.error;
                            console.error('Server error:', data.error);
                        } else {
                            resultDiv.textContent = `Sound classified as: ${data.classification} at ${data.timestamp}`;

                            // Send the result to the web app server to save it
                            fetch('/save_result', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    classification: data.classification,
                                    timestamp: data.timestamp
                                })
                            })
                            .then(res => res.json())
                            .then(saveData => {
                                if (saveData.status !== 'success') {
                                    console.error('Error saving result:', saveData.message);
                                }
                            })
                            .catch(error => {
                                console.error('Error saving result:', error);
                            });
                        }
                    })
                    .catch(error => {
                        resultDiv.textContent = 'Fetch error: ' + error;
                        console.error('Fetch error:', error);
                    });
                };
            })
            .catch(error => {
                resultDiv.textContent = 'Microphone access denied or error: ' + error;
            });
    }
});
