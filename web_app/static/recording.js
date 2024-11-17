const recordButton = document.getElementById("recordButton");
const nameInput = document.getElementById("nameInput");
const statusText = document.getElementById("status");

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

recordButton.addEventListener("click", async () => {
  if (!isRecording) {
    recordButton.textContent = "Stop Recording";
    statusText.textContent = "Recording...";
    isRecording = true;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];

      const formData = new FormData();
      formData.append("audio", audioBlob);
      formData.append("name", nameInput.value);

      try {
        const response = await fetch(UPLOAD_URL, {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          statusText.textContent = "Audio uploaded successfully!";
        } else {
          statusText.textContent = "Failed to upload audio.";
        }
      } catch (error) {
        statusText.textContent = "Error uploading audio.";
        console.error("Error uploading audio:", error);
      }
    };

    mediaRecorder.start();
  } else {
    recordButton.textContent = "Start Recording";
    statusText.textContent = "Processing...";
    isRecording = false;

    if (mediaRecorder) {
      mediaRecorder.stop();
    }
  }
});
