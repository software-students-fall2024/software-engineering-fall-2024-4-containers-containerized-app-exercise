let sections = document.querySelectorAll("section");
let header = document.querySelectorAll("header");

// REPLAY BUTTON
document.addEventListener("DOMContentLoaded", () => {
    const replayButton = document.getElementById("replayButton");

    replayButton.addEventListener("click", (event) => {
        event.preventDefault();
        // ADD RESET GAME LOGIC HERE
        console.log("Replay button clicked");
        resetGame();
    });
});

// RESET GAME
function resetGame() {
    // CODE TO RESET GAME: CLEARING SCORES, RESETTING UI, ETC...
    console.log("Game reset");
}

// GAME PLAYTHROUGH (CAMERA BOX, COUNTDOWN, CURRENT STATS)
document.addEventListener("DOMContentLoaded", () => {
    // Define variables
    const cameraBox = document.getElementById("camera-box");
    const yesButton = document.getElementById("yes-button");
    const countdownDisplay = document.getElementById("countdown");
    const choicesDisplay = document.getElementById("choices");
    const videoElement = document.createElement("video");

    videoElement.setAttribute("autoplay", true);
    videoElement.setAttribute("playsinline", true);
    videoElement.setAttribute("muted", true);

    let cameraInitialized = false;
    choicesDisplay.style.display = "none"; // Hide results at first

    // Start camera
    function startCamera() {
        navigator.mediaDevices
            .getUserMedia({ video: true })
            .then((stream) => {
                videoElement.srcObject = stream;
                cameraBox.innerHTML = ""; 
                cameraBox.appendChild(videoElement);
                cameraInitialized = true;

                startGameTimer(); // Start game after camera allowed
            })
            // If camera permissions not allowed
            .catch((err) => {
                console.error("Error accessing the camera:", err);
                cameraBox.innerHTML = "Unable to access the camera. Please enable permissions.";
                cameraInitialized = false;
            });
    }

    // Start game countdown
    function startGameTimer() {
        const timerText = ["Rock...", "Paper...", "Scissors...", "Shoot!"];
        let index = 0;

        const interval = setInterval(() => {
            countdownDisplay.innerText = timerText[index];
            index++;

            if (index === timerText.length) {
                clearInterval(interval);
                captureFrame();
            }
        }, 1000); // 1 second intervals
    }

    // Capture current frame from camera feed
    function captureFrame() {
        if (!cameraInitialized) return;

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        /* // Convert image to Base64 and send it to back-end
        const frame = canvas.toDataURL("image/jpeg");
        fetch("/process_frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: frame }),
        })
            .then((response) => response.json())
            .then((data) => {
                const userChoice = data.result;             // Get user's choice
                const computerChoice = getComputerChoice(); // Generate random computer choice
                displayResults(userChoice, computerChoice); // Display results directly
            })
            .catch((err) => {
                //choicesDisplay.innerHTML = "Error processing your move.";
                choicesDisplay.style.display = "block";
            }); */
    }

    // IFF >1 round
    yesButton.addEventListener("click", () => {
        startCamera(); // Start camera and game logic

        // Update button after first round
        yesButton.textContent = "Play again!";
        countdownDisplay.style.display = "block"; // Reset countdown
        choicesDisplay.style.display = "none";    // Hide previous results
    });
});