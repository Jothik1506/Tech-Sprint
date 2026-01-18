const instructionText = document.getElementById('instructionText');
const timerDisplay = document.getElementById('timerDisplay');
const pauseBtn = document.getElementById('pauseBtn');
const skipBtn = document.getElementById('skipBtn');
const backBtn = document.getElementById('backBtn');
const circle = document.querySelector('.meditationCircle');
const progressDots = [
    document.getElementById('dot1'),
    document.getElementById('dot2'),
    document.getElementById('dot3')
];

// Configuration
const MEDITATION_DURATION = 360; // 6 minutes (360 seconds)

// State
let isPaused = false;
let timeLeft = MEDITATION_DURATION;
let timerInterval = null;
let currentPhase = 'INIT'; // INIT, GUIDE, TIMER, DONE
let musicPending = false; // If 10s mark hits while paused

// Background Audio
let backgroundAudio = new Audio("assets/meditation_song1.wav");
backgroundAudio.loop = true;
// backgroundAudio.volume = 0.5; // Optional: Adjust volume if needed

function startBackgroundAudio() {
    if (backgroundAudio) {
        backgroundAudio.play().catch(e => console.log("Audio play failed (maybe autoplay policy)", e));
    }
}

function pauseBackgroundAudio() {
    if (backgroundAudio) {
        backgroundAudio.pause();
    }
}

function stopBackgroundAudio() {
    if (backgroundAudio) {
        backgroundAudio.pause();
        backgroundAudio.currentTime = 0;
    }
}

// Speech Synthesis
const synth = window.speechSynthesis;

function speak(text, onEndCallback) {
    if (synth.speaking) synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;  // Slightly faster than 0.8 for clarity
    utterance.pitch = 1.0; // Neutral
    utterance.volume = 1.0;

    // Use a gentle voice if available
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

    console.log("Selected voice:", utterance.voice ? utterance.voice.name : "Default (No preference found)");

    if (onEndCallback) {
        utterance.onend = onEndCallback;
    }

    synth.speak(utterance);
}

function stopSpeech() {
    if (synth.speaking) synth.cancel();
}

// Voice Guidance Functions
function speakIntro(onComplete) {
    speak("Calm yourself... and close your eyes. Relax your shoulders... and breathe naturally.", onComplete);
}

function speakCompletion() {
    speak("Gently open your eyes. You are calm, refreshed, and ready to focus.");
}

function speakMidSessionCue() {
    // Optional gentle reminder
    speak("Stay focused on your breath...");
}

// Main Flow
function startMeditation() {
    currentPhase = 'GUIDE';
    updateDots(0);
    instructionText.innerText = "Calm yourself and close your eyes.";
    timerDisplay.innerText = formatTime(MEDITATION_DURATION);

    // Add breathing animation
    circle.classList.add('breathing');

    // Start Intro Logic
    speakIntro(() => {
        if (currentPhase === 'GUIDE') {
            startTimerPhase();
        }
    });

    // Start music exactly 10s after start (independent of speech)
    setTimeout(() => {
        if (!isPaused && currentPhase !== 'DONE') {
            startBackgroundAudio();
        } else if (currentPhase !== 'DONE') {
            // If paused when timer hits, mark it to play on resume
            musicPending = true;
        }
    }, 10000);
}

function startTimerPhase() {
    currentPhase = 'TIMER';
    updateDots(1);
    instructionText.innerText = "Concentrate on your breathe.";
    timerDisplay.innerText = formatTime(timeLeft);

    // Speak once at the start of the timer
    speak("Concentrate on your breathe.");

    timerInterval = setInterval(() => {
        if (!isPaused) {
            timeLeft--;
            timerDisplay.innerText = formatTime(timeLeft);

            // Speak again after 3 minutes (at the 180s mark)
            if (timeLeft === 180) {
                speak("Concentrate on your breathe.");
            }

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                finishMeditation();
            }
        }
    }, 1000);
}

function finishMeditation() {
    currentPhase = 'DONE';
    updateDots(2);
    instructionText.innerText = "✅ Session completed";
    timerDisplay.innerText = "00:00";
    circle.classList.remove('breathing');

    skipBtn.innerText = "Done";
    pauseBtn.style.display = 'none';

    stopBackgroundAudio(); // Or fade out? Stopping for now.
    speakCompletion();
}

// Helpers
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function updateDots(activeIdx) {
    progressDots.forEach((d, i) => {
        d.classList.toggle('active', i <= activeIdx);
    });
}

function togglePause() {
    isPaused = !isPaused;
    pauseBtn.innerText = isPaused ? "Resume" : "Pause";

    if (isPaused) {
        // Pause Everything
        if (synth.speaking) synth.pause();
        pauseBackgroundAudio();
        circle.style.animationPlayState = 'paused';
    } else {
        // Resume Everything
        if (synth.paused) synth.resume();

        // Resume audio if it was playing or if it was pending start
        if (!backgroundAudio.paused || musicPending) {
            startBackgroundAudio();
            musicPending = false;
        }

        circle.style.animationPlayState = 'running';
    }
}

function quit() {
    stopSpeech();
    stopBackgroundAudio();
    if (timerInterval) clearInterval(timerInterval);
    window.location.href = "index.html";
}

// Event Listeners
pauseBtn.addEventListener('click', togglePause);
skipBtn.addEventListener('click', quit);
backBtn.addEventListener('click', quit);

// Music Selection Logic
const musicOptions = document.querySelectorAll('.musicOption');
musicOptions.forEach(opt => {
    opt.addEventListener('click', () => {
        // UI Update
        musicOptions.forEach(o => o.classList.remove('active'));
        opt.classList.add('active');

        // Audio Update
        const songId = opt.getAttribute('data-song');
        const songPath = songId === '1' ? "assets/meditation_song1.wav" : "assets/meditation_song2.wav";

        // If audio is already initialized
        if (backgroundAudio) {
            const wasPlaying = !backgroundAudio.paused;
            backgroundAudio.src = songPath;
            backgroundAudio.loop = true;

            // If it was already playing (meaning we passed the 10s mark), resume immediately
            // If it wasn't playing (before 10s mark), the timeout logic will handle start
            if (wasPlaying) {
                backgroundAudio.play().catch(e => console.log("Play error:", e));
            }
        } else {
            // Should not happen as we init globally, but safe fallback
            backgroundAudio = new Audio(songPath);
            backgroundAudio.loop = true;
        }
    });
});

// Cleanup
window.addEventListener('beforeunload', () => {
    stopSpeech();
    stopBackgroundAudio();
    if (timerInterval) clearInterval(timerInterval);
});

// Initialization
if (synth.getVoices().length === 0) {
    synth.onvoiceschanged = () => startMeditation();
} else {
    startMeditation();
}
