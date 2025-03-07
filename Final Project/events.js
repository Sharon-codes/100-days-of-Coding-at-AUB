// events.js
export function setupEventListeners() {
    console.log('Event listeners set up');

    // History item clicks
    document.getElementById('historyContainer').addEventListener('click', (e) => {
        const historyItem = e.target.closest('.history-item');
        if (historyItem) {
            const { type, input } = historyItem.dataset;
            if (type === 'qa') {
                document.getElementById('inputText').value = input.split('Q: ')[1] || '';
                document.getElementById('question').value = input.split('Q: ')[0] || '';
                window.answerQuestion();
            } else {
                document.getElementById('inputText').value = input;
                if (type === 'summary') window.summarizeText();
                else if (type === 'sentiment') window.analyzeSentiment();
            }
        }
    });

    // Input validation on blur
    document.getElementById('inputText').addEventListener('blur', (e) => {
        if (!e.target.value.trim()) e.target.classList.add('is-invalid');
        else e.target.classList.remove('is-invalid');
    });
    document.getElementById('question').addEventListener('blur', (e) => {
        if (!e.target.value.trim()) e.target.classList.add('is-invalid');
        else e.target.classList.remove('is-invalid');
    });
}