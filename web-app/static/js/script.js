window.onload = function(){
    const toggleButton = document.getElementById("toggle-recording");
    const statusElement = document.getElementById("status");
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
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const audio = new Audio(audioUrl);
                        audio.play(); // You can also append it to a <audio> element to play
                        // Optinally, save or upload the recording here
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