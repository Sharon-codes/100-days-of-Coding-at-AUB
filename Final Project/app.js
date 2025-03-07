// app.js
document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
});

function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offlineIndicator');
    if (offlineIndicator) {
        offlineIndicator.classList.toggle('d-none', navigator.onLine);
    }
}

// Rate limiter to prevent rapid clicks
window.createRateLimiter = (fn, delay) => {
    let lastRun = 0;
    let timeout = null;
    return function (...args) {
        const now = Date.now();
        clearTimeout(timeout);
        if (now - lastRun >= delay) {
            lastRun = now;
            return fn.apply(this, args);
        } else {
            return new Promise(resolve => {
                timeout = setTimeout(() => {
                    lastRun = now;
                    resolve(fn.apply(this, args));
                }, delay - (now - lastRun));
            });
        }
    };
};

// Summarize Text
window.summarizeText = window.createRateLimiter(async () => {
    console.log('summarizeText called');
    const text = document.getElementById('inputText')?.value;
    if (!text) {
        console.log('No text provided for summarization');
        alert('Please enter text to summarize');
        return;
    }
    const btn = document.getElementById('summarizeBtn');
    if (!btn) {
        console.error('summarizeBtn not found');
        return;
    }
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="loader"></div>Processing...';
    btn.disabled = true;
    try {
        console.log('Calling apiClient.summarizeText');
        const result = await window.apiClient.summarizeText(text);
        console.log('Received summarization result:', result);
        window.historyManager.addItem('summary', text, result);
        updateSummaryUI(result);
    } catch (error) {
        console.error('Summarization error:', error);
        const summaryResult = document.getElementById('summaryResult');
        if (summaryResult) {
            summaryResult.innerHTML = '<div class="alert alert-danger">Error processing request</div>';
        }
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}, 1000);

// Analyze Sentiment
window.analyzeSentiment = window.createRateLimiter(async () => {
    console.log('analyzeSentiment called');
    const text = document.getElementById('inputText')?.value;
    if (!text) {
        console.log('No text provided for sentiment analysis');
        alert('Please enter text for analysis');
        return;
    }
    const btn = document.getElementById('sentimentBtn');
    if (!btn) {
        console.error('sentimentBtn not found');
        return;
    }
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="loader"></div>Analyzing...';
    btn.disabled = true;
    try {
        console.log('Calling apiClient.analyzeSentiment');
        const result = await window.apiClient.analyzeSentiment(text);
        console.log('Received sentiment result:', result);
        window.historyManager.addItem('sentiment', text, result);
        updateSentimentUI(result);
    } catch (error) {
        console.error('Sentiment analysis error:', error);
        const sentimentResult = document.getElementById('sentimentResult');
        if (sentimentResult) {
            sentimentResult.innerHTML = '<div class="alert alert-danger">Error analyzing sentiment</div>';
        }
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}, 1000);

// Answer Question
window.answerQuestion = window.createRateLimiter(async () => {
    console.log('answerQuestion called');
    const text = document.getElementById('inputText')?.value;
    const question = document.getElementById('question')?.value;
    if (!text || !question) {
        console.log('Missing text or question for Q&A');
        alert('Please provide both text and question');
        return;
    }
    const btn = document.getElementById('qaBtn');
    if (!btn) {
        console.error('qaBtn not found');
        return;
    }
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="loader"></div>Finding Answer...';
    btn.disabled = true;
    try {
        console.log('Calling apiClient.answerQuestion');
        const result = await window.apiClient.answerQuestion(text, question);
        console.log('Received Q&A result:', result);
        window.historyManager.addItem('qa', `Q: ${question}`, result);
        updateQAUI(result);
        await Promise.all([
            generateRelatedQuestions(text, question),
            generateFollowUpQuestion(text, result.answer)
        ]);
    } catch (error) {
        console.error('Q&A error:', error);
        const answerResult = document.getElementById('answerResult');
        if (answerResult) {
            answerResult.innerHTML = '<div class="alert alert-danger">Error processing question</div>';
        }
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}, 1000);

// Generate Related Questions
async function generateRelatedQuestions(text, question) {
    console.log('Generating related questions for:', question);
    const relatedDiv = document.getElementById('relatedQuestions');
    const listDiv = document.getElementById('relatedQuestionsList');
    if (!relatedDiv || !listDiv) {
        console.error('Related questions elements not found');
        return;
    }
    try {
        const relatedQuestions = await window.apiClient.getRelatedQuestions(text, question);
        console.log('Received related questions:', relatedQuestions);
        if (relatedQuestions.length > 0) {
            listDiv.innerHTML = relatedQuestions.map(q => `
                <div class="related-question" onclick="document.getElementById('question').value='${q.replace(/'/g, "\\'")}';window.answerQuestion();">${q}</div>
            `).join('');
            relatedDiv.classList.remove('d-none');
        } else {
            relatedDiv.classList.add('d-none');
        }
    } catch (error) {
        console.error('Related questions error:', error);
        relatedDiv.classList.add('d-none');
    }
}

// Generate Follow-up Question
async function generateFollowUpQuestion(text, answer) {
    console.log('Generating follow-up question for answer:', answer);
    const followUpDiv = document.getElementById('followUpQuestion');
    if (!followUpDiv) {
        console.error('followUpQuestion element not found');
        return;
    }
    try {
        const followUp = await window.apiClient.getFollowUpQuestion(text, answer);
        console.log('Received follow-up question:', followUp);
        if (followUp) {
            followUpDiv.textContent = `Follow-up: ${followUp}`;
            followUpDiv.classList.remove('d-none');
            followUpDiv.onclick = () => {
                const questionInput = document.getElementById('question');
                if (questionInput) questionInput.value = followUp;
                window.answerQuestion();
            };
        } else {
            followUpDiv.classList.add('d-none');
        }
    } catch (error) {
        console.error('Follow-up question error:', error);
        followUpDiv.classList.add('d-none');
    }
}

// Update Summary UI
function updateSummaryUI(result) {
    try {
        const summaryResult = document.getElementById('summaryResult');
        if (!summaryResult) {
            console.error('summaryResult element not found');
            return;
        }
        summaryResult.innerHTML = `
            <div class="model-info mb-2"><small>📊 ${result.topics.length} Topics</small></div>
            <div class="result-text">${result.summary}</div>
            <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
        `;
        const confidenceMeter = document.getElementById('summaryConfidence');
        if (confidenceMeter) {
            confidenceMeter.style.width = `${result.confidence * 100}%`;
        } else {
            console.error('summaryConfidence element not found');
        }
        const speakBtn = summaryResult.querySelector('.speak-btn');
        if (speakBtn) {
            speakBtn.addEventListener('click', () => window.speechManager.speak(result.summary));
        }
    } catch (error) {
        console.error('Error in updateSummaryUI:', error);
        const summaryResult = document.getElementById('summaryResult');
        if (summaryResult) {
            summaryResult.innerHTML = '<div class="alert alert-danger">Error displaying summary</div>';
        }
    }
}

// Update Sentiment UI
function updateSentimentUI(result) {
    try {
        const sentimentResult = document.getElementById('sentimentResult');
        if (sentimentResult) {
            sentimentResult.innerHTML = `
                <div class="model-info mb-2"><small>📊 ${result.dominant} | ${(result.confidence * 100).toFixed(1)}%</small></div>
                <div class="result-text">${result.sentences.map(s => `
                    <div class="mb-2"><span class="emotion-indicator" style="background-color: var(--emotion-${s.emotion})">${s.emotion}</span> ${s.text}</div>
                `).join('')}</div>
                <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
            `;
            const speakBtn = sentimentResult.querySelector('.speak-btn');
            if (speakBtn) {
                speakBtn.addEventListener('click', () => 
                    window.speechManager.speak(`Dominant emotion: ${result.dominant} with ${(result.confidence * 100).toFixed(1)}% confidence`)
                );
            }
        }
        const sentimentConfidence = document.getElementById('sentimentConfidence');
        if (sentimentConfidence) {
            sentimentConfidence.style.width = `${result.confidence * 100}%`;
        }
        try {
            window.chartManager.createSentimentChart(result);
        } catch (chartError) {
            console.error('Error creating sentiment chart:', chartError);
        }
        const sentimentCompare = document.getElementById('sentimentCompare');
        if (sentimentCompare) {
            const prev = window.historyManager.getLastItem('sentiment');
            if (prev && prev.id !== result.id) {
                sentimentCompare.innerHTML = `
                    <div class="compare-item">Current: ${result.dominant} (${(result.confidence * 100).toFixed(1)}%)</div>
                    <div class="compare-item">Previous: ${prev.data.dominant} (${(prev.data.confidence * 100).toFixed(1)}%)</div>
                `;
            } else {
                sentimentCompare.innerHTML = '';
            }
        }
    } catch (error) {
        console.error('Error in updateSentimentUI:', error);
        const sentimentResult = document.getElementById('sentimentResult');
        if (sentimentResult) {
            sentimentResult.innerHTML = '<div class="alert alert-danger">Error displaying sentiment</div>';
        }
    }
}

// Update Q&A UI
function updateQAUI(result) {
    try {
        const answerResult = document.getElementById('answerResult');
        if (answerResult) {
            answerResult.innerHTML = `
                <div class="model-info mb-2"><small>📊 ${result.confidence}% Confidence</small></div>
                <div class="result-text mb-2">${result.answer}</div>
                <div class="text-muted small">Context: ${result.context}</div>
                <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
            `;
            const speakBtn = answerResult.querySelector('.speak-btn');
            if (speakBtn) {
                speakBtn.addEventListener('click', () => window.speechManager.speak(result.answer));
            }
        }
        const qaConfidence = document.getElementById('qaConfidence');
        if (qaConfidence) {
            qaConfidence.style.width = `${result.confidence}%`;
        }
        const qaMetrics = document.getElementById('qaMetrics');
        if (qaMetrics) {
            qaMetrics.innerHTML = `
                <div>Words: ${result.metrics.wordsAnalyzed}</div>
                <div>Sentences: ${result.metrics.sentencesAnalyzed}</div>
                <div>Match: ${result.metrics.matchQuality}%</div>
            `;
        }
    } catch (error) {
        console.error('Error in updateQAUI:', error);
        const answerResult = document.getElementById('answerResult');
        if (answerResult) {
            answerResult.innerHTML = '<div class="alert alert-danger">Error displaying answer</div>';
        }
    }
}