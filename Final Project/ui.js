// ui.js
export function initializeUI() {
    // Add any initial UI setup here
    console.log('UI initialized');

    // Set default placeholder styles
    const inputText = document.getElementById('inputText');
    const question = document.getElementById('question');
    inputText.placeholder = 'Enter your text here for analysis...';
    question.placeholder = 'Ask your question here...';

    // Update offline status
    updateOnlineStatus();
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
}

function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offlineIndicator');
    offlineIndicator.classList.toggle('visible', !navigator.onLine);
}