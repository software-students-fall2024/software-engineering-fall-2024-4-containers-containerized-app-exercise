const startButton = document.getElementById('start_recording');
const stopButton = document.getElementById('stop_recording');
const video = document.getElementById('camera-feed');
const canvas = document.getElementById('snapshot');
const ctx = canvas.getContext('2d');

let stream;
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera:", err);
    }
}

startCamera();

startButton.addEventListener('click', () => {
    startButton.disabled = true;
    stopButton.disabled = false;
    video.style.display = "block";
    canvas.style.display = "none";
    // Clear result section
    const element = document.getElementById('result_section');
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
    console.log("Recording started.");
});

stopButton.addEventListener('click', () => {
    startButton.disabled = false;
    stopButton.disabled = true;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');
    video.style.display = "none";
    canvas.style.display = "block";
    fetch('/upload_snapshot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "image": imageData }),
    })
        .then((response) => response.json())
        .then((data) => {
            const section = document.getElementById('result_section');
            const img = document.createElement('img');
            img.src = 'data:image/png;base64,' + data.output;
            img.alt = 'Processed Image';
            section.appendChild(img);

            const p = document.createElement('p');
            p.textContent = data.translation;
            section.appendChild(p);
        })
        .catch((err) => {
            console.error("Error saving snapshot: ", err);
        });
    console.log("Recording stopped.");
});
