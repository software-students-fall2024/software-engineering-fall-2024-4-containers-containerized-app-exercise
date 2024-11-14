window.onload = function(){
    const toggleButton = document.getElementById("toggle-recording");
    const statusElement = document.getElementById("status");
    const resultElement = document.getElementById("result"); // Element to display transcription result
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let audioStream;
    toggleButton.addEventListener("click",function(){
        if (isRecording){
            // Stop recording
            mediaRecorder.stop();
            toggleButton.textContent = "Start Recording";
            statusElement.textContent = "Recording stopped. Processing audio...";
        }
        else{
            // Start recording
            navigator.mediaDevices.getUserMedia({audio:true})
                .then(function(stream){
                    // Set up the media recorder
                    audioStream = stream;
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = function(event){
                        audioChunks.push(event.data);
                    };
                    mediaRecorder.onstop = function() {
                        // When recording stops, process the audio data
                        const audioBlob = new Blob(audioChunks, {type:'audio/wav'});

                        // Send the audio blob to the ml-client via a POST request
                        const formData = new FormData();
                        formData.append("audio",audioBlob,"recording.wav");

                        // Make the POST request to ml-client to process the audio
                        fetch("http://ml-client:5000/transcribe", {  // Use the ml-client's Docker service name and port
                            method: "POST",
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.error){
                                resultElement.textContent = "Error: " + data.error;
                            }
                            else{
                                // Display the transcription and store the transcription ID
                                const transcriptionId = data.id;
                                resultElement.textContent = "Transcription: " + data.transcription;
                            }
                        })
                        .catch(function(error){
                            console.error("Error sending audio to ML client:", error);
                            resultElement.textContent = "Error processing the audio.";
                        })
                        audioChunks = []; // Clear audio chunks for the next recording
                    };
                    // Start recording
                    mediaRecorder.start();
                    toggleButton.textContent = "Stop Recording";
                    statusElement.textContent = "Recording in progress...";
                    isRecording = true;
                })
                .catch(function(error){
                    console.error("Error accessing microphone:", error);
                    statusElement.textContent = "ErrorL Unable to access the microphone.";
                })
        }
    })
}