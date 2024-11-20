const cameraBtn = document.getElementById('camera-btn');
const captureBtn = document.getElementById('capture-btn');
const video = document.getElementById('camera-feed');
const canvas = document.getElementById('snapshot');
const ctx = canvas.getContext('2d');
const d = document.querySelector('.desc');

let stream;
async function startCamera() {
try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
} catch (err) {
    console.error("Error accessing camera:", err);
}
}

cameraBtn.addEventListener('click', () => {
    startCamera();
    d.style.display = "none";
    cameraBtn.style.display = "none";
    captureBtn.style.display = "block";
    video.style.display = "block";
    canvas.style.display = "none";
    //clear result section
    const element = document.getElementById('result_section');
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
    console.log("Recording started.");
});

captureBtn.addEventListener('click', () => {
    d.textContent = "click start camera to redo";
    d.style.display = "block";
    cameraBtn.style.display = "block";
    captureBtn.style.display = "none";

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
        body: JSON.stringify({"image": imageData}),
    })
        .then((response) => response.json())
        .then((data) => {
            //console.log("Snapshot saved: ", data);

            // Create a new section element to append the image and text
            const section = document.getElementById('result_section');

            // Create and append the image element
            const img = document.createElement('img');
            img.src = 'data:image/png;base64,'+data.output; // Assuming the image URL is provided in the response data
            img.alt = 'Processed Image'; // Add alt text for the image
            section.appendChild(img);

            // Create and append the paragraph element with translation or any other data
            const p = document.createElement('p');
            p.textContent = data.translation; // Assuming the translation is part of the response data
            p.classList.add('translation');
            section.appendChild(p);
        })
        .catch((err) => {
            console.error("Error saving snapshot: ", err);
        });
    console.log("Recording stopped.");
});