let sections = document.querySelectorAll("section");
let header = document.querySelectorAll("header");

window.onscroll = () => {
    selections.forEeach(sec => {
        let top = window.scrollY;
        let offset = sec.offsetTop - 150;
        let height = sec.offsetHeight;
        let id = sec.getAttribute("id");

        if (top >= offset && top < offset + height) {
            navLinks.forEach(links => {
                links.classList.remove("active");
                document.querySelector("header[href*=" + id + " ]").classList.add("active");
            })
        }
    })
}

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

// COUNTDOWN FLASHES
document.addEventListener('DOMContentLoaded', () => {
    // Define variables
    const yesButton = document.getElementById('yes-button');
    const countdown = document.getElementById('countdown');
    const choices = document.getElementById('choices');
    let hasPlayedOnce = false;          // Track if "Yes" button has been clicked
    let index = 0;
    const words = ["Get ready!", "Rock", "Paper", "Scissors", "Shoot!"];
    choices.style.display = 'none';     // Hide choices initially

    // startCountdown() function: begins game countdown if user agrees
    function startCountdown() {
        countdown.textContent = words[index];
        const interval = setInterval(() => {
            index++;
            if (index < words.length) {countdown.textContent = words[index];} 
            else {
                clearInterval(interval);
                choices.style.display = 'block';       // Show choices after countdown
                yesButton.textContent = "Play again!"; // Change yes-button after click
                index = 0;                             // Reset index for next game
            }
        }, 1000);
    }

    // startCountdown() on Yes button click
    yesButton.addEventListener('click', () => {
        choices.style.display = 'none'; // Hide choices at the start
        startCountdown();               // Begin countdown

        if (!hasPlayedOnce) {hasPlayedOnce = true;} // True after first click
    });
});