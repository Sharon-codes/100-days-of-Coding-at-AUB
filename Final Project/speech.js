// speech.js
export function setupSpeechFeatures() {
    if (!('speechSynthesis' in window) || !('webkitSpeechRecognition' in window)) {
        console.warn('Speech features not fully supported in this browser');
        return;
    }

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    window.speechManager = {
        speak(text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        },
        startVoiceInput(targetId) {
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById(targetId).value = transcript;
            };
            recognition.onerror = (event) => console.error('Speech recognition error:', event.error);
            recognition.start();
        },
        stopVoiceInput() {
            recognition.stop();
        }
    };

    // Voice button animations
    const voiceBtns = document.querySelectorAll('.voice-input-btn');
    voiceBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.id === 'voiceInputBtn' ? 'inputText' : 'question';
            if (btn.classList.contains('active')) {
                window.speechManager.stopVoiceInput();
                btn.classList.remove('active');
            } else {
                window.speechManager.startVoiceInput(targetId);
                btn.classList.add('active');
            }
        });
        recognition.onend = () => btn.classList.remove('active');
    });
}