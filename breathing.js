const phaseText = document.getElementById('phaseText');
const phaseTimerDisplay = document.getElementById('phaseTimer');
const totalTimerDisplay = document.getElementById('totalTimer');
const orb = document.getElementById('orb');
const pauseBtn = document.getElementById('pauseBtn');
const skipBtn = document.getElementById('skipBtn');
const backBtn = document.getElementById('backBtn');

// Configuration
const TOTAL_DURATION = 180; // 3 minutes
const INHALE_SECONDS = 5;
const EXHALE_SECONDS = 5;

// State
let isPaused = false;
let totalTimeLeft = TOTAL_DURATION;
let phaseTimeLeft = 0;
let currentPhase = 'INIT'; // INIT, INHALE, EXHALE, DONE
let gameLoopInterval = null;

// Speech Synthesis
const synth = window.speechSynthesis;

function speak(text) {
    if (synth.speaking) synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Voice Selection (Match Meditation logic)
    const voices = synth.getVoices();
    // Prioritize "Natural" voices (often high quality), then Jenny/Zira
    const preferredVoice = voices.find(v =>
        v.name.includes("Natural") ||
        v.name.includes("Microsoft Jenny") ||
        v.name.includes("Microsoft Zira") ||
        v.name.includes("Google US English") ||
        v.name.includes("Samantha")
    );

    if (preferredVoice) utterance.voice = preferredVoice;
    synth.speak(utterance);
}

function stopSpeech() {
    if (synth.speaking) synth.cancel();
}

function startSessionReal() {
    currentPhase = 'INHALE';
    phaseTimeLeft = INHALE_SECONDS;
    totalTimeLeft = TOTAL_DURATION;

    orb.classList.remove('exhale');
    orb.classList.add('inhale'); // Start expanding immediately

    speak("Get ready for breathing exercise... Breathe In"); // Initial cue

    updateUI();
    gameLoopInterval = setInterval(tick, 1000);
}

function tick() {
    if (isPaused) return;

    phaseTimeLeft--;
    totalTimeLeft--;

    if (totalTimeLeft < 0) {
        finishSession();
        return;
    }

    if (phaseTimeLeft < 0) {
        // Switch Phase
        if (currentPhase === 'INHALE') {
            currentPhase = 'EXHALE';
            phaseTimeLeft = EXHALE_SECONDS - 1;

            // Trigger Animation & Speech
            orb.classList.remove('inhale');
            orb.classList.add('exhale');
            speak("Breathe Out");
        } else {
            currentPhase = 'INHALE';
            phaseTimeLeft = INHALE_SECONDS - 1;

            // Trigger Animation & Speech
            orb.classList.remove('exhale');
            orb.classList.add('inhale');
            speak("Breathe In");
        }
    }

    updateUI();
}

function updateUI() {
    // Total Timer
    totalTimerDisplay.innerText = formatTime(totalTimeLeft);

    // Phase UI
    if (currentPhase === 'INHALE') {
        phaseText.innerText = "Breathe In";
    } else if (currentPhase === 'EXHALE') {
        phaseText.innerText = "Breathe Out";
    }

    // Phase Countdown
    phaseTimerDisplay.innerText = (phaseTimeLeft + 1).toString();
}

function finishSession() {
    clearInterval(gameLoopInterval);
    currentPhase = 'DONE';

    phaseText.innerText = "✅ Completed!";
    phaseTimerDisplay.innerText = "";
    totalTimerDisplay.innerText = "00:00";

    // Stop animation
    orb.classList.remove('inhale');
    orb.classList.remove('exhale');
    orb.style.transform = "scale(1)";

    skipBtn.innerText = "Done";
    pauseBtn.style.display = 'none';

    speak("Session completed. Great job.");
}

function formatTime(seconds) {
    if (seconds < 0) seconds = 0;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function togglePause() {
    isPaused = !isPaused;
    pauseBtn.innerText = isPaused ? "Resume" : "Pause";

    if (isPaused) {
        // Pause Speech
        if (synth.speaking) synth.pause();
    } else {
        // Resume Speech
        if (synth.paused) synth.resume();
    }
}

function quit() {
    stopSpeech();
    clearInterval(gameLoopInterval);
    window.location.href = "index.html";
}

// Handlers
pauseBtn.addEventListener('click', togglePause);
skipBtn.addEventListener('click', quit);
backBtn.addEventListener('click', quit);

// Wait for voices if needed
if (synth.getVoices().length === 0) {
    synth.onvoiceschanged = () => startSessionReal();
} else {
    startSessionReal();
}
