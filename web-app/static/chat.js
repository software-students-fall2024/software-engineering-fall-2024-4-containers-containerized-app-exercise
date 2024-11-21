let mediaRecorder; // Global variable to track the recorder


const mlClientUrl = "http://127.0.0.1:5001";
// Function to handle sending a text message
async function sendMessage(event) {
  event.preventDefault();
  const messageInput = document.getElementById("message");
  const userMessage = messageInput.value;
  if (!userMessage) return;

  const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
  });

  const chatLog = document.getElementById("chat-log");
  if (response.ok) {
      const data = await response.json();
      chatLog.innerHTML += `<div><b>You:</b> ${userMessage}</div>`;
      chatLog.innerHTML += `<div><b>${data.character_name}:</b> ${data.character_message}</div>`;
  } else {
      chatLog.innerHTML += `<div class="error">Failed to get a response. Try again.</div>`;
  }
  messageInput.value = "";
}

async function recordAudio() {
  console.log("Starting audio recording...");

  try {
    // Request access to the microphone
    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    let mediaRecorder = new MediaRecorder(stream);
    let chunks = [];

    // Collect audio data chunks
    mediaRecorder.ondataavailable = (event) => {
      chunks.push(event.data);
    };

    // Handle the stop event
    mediaRecorder.onstop = async () => {
      // Create a Blob from the recorded chunks
      let blob = new Blob(chunks, { type: "audio/wav" });
      console.log("Audio recording completed.");

      // Send the audio blob to the Flask backend
      const formData = new FormData();
      formData.append("audio", blob, "recording.wav");

      try {
        const response = await fetch("/convert-to-wav", {
          method: "POST",
          body: formData, // Send FormData
        });

        if (response.ok) {
          const data = await response.json();
          console.log("Conversion successful:", data);
          alert(`WAV File saved at: ${data.wav_file_path}`);
        } else {
          console.error("Error from server:", await response.text());
          alert("Failed to convert the file. Check the logs.");
        }
      } catch (error) {
        console.error("Error sending audio to backend:", error);
        alert("An error occurred while sending the audio to the backend.");
      }
    };

    // Start recording
    mediaRecorder.start();
    console.log("Recording started...");

    // Stop recording after 10 seconds
    setTimeout(() => {
      mediaRecorder.stop();
    }, 10000);
  } catch (error) {
    console.error("Error accessing audio stream:", error);
    alert("Failed to access the microphone. Please check permissions.");
  }
}
