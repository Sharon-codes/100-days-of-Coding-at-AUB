// Consolidated ApiClient (merged from api-client.js and app-client.js)
export class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.requestQueue = [];
        this.processing = false;
        this.maxConcurrent = 2;
    }

    async request(endpoint, method = 'POST', data = null) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ endpoint, method, data, resolve, reject });
            this._processQueue();
        });
    }

    async _processQueue() {
        if (this.processing || this.requestQueue.length === 0) return;
        this.processing = true;
        const requests = this.requestQueue.splice(0, this.maxConcurrent);
        
        try {
            await Promise.all(requests.map(req => this._executeRequest(req)));
        } finally {
            this.processing = false;
            if (this.requestQueue.length > 0) this._processQueue();
        }
    }

    async _executeRequest(req) {
        const { endpoint, method, data, resolve, reject } = req;
        
        try {
            // Check if we're online
            if (!navigator.onLine) {
                // If offline and we have cached data, return it
                const cachedResponse = this._getCachedResponse(endpoint, data);
                if (cachedResponse) {
                    resolve(cachedResponse);
                    return;
                }
                throw new Error('You are offline and no cached data is available.');
            }
            
            // For development/testing, use mock data
            if (process.env.NODE_ENV === 'development' || location.hostname === 'localhost') {
                await new Promise(resolve => setTimeout(resolve, 500)); // Mock delay
                let result;
                switch (endpoint) {
                    case '/summarize':
                        result = { summary: `Summary of: ${data.text.substring(0, 50)}...`, topics: ['mock'], confidence: 0.95 };
                        break;
                    case '/sentiment':
                        result = { dominant: 'positive', confidence: 0.85, sentences: [{ emotion: 'joy', text: data.text.substring(0, 50) }], id: Date.now() };
                        break;
                    case '/qa':
                        result = { answer: `Answer to: ${data.question}`, confidence: 90, context: data.text.substring(0, 50), metrics: { wordsAnalyzed: 10, sentencesAnalyzed: 2, matchQuality: 88 } };
                        break;
                    case '/related-questions':
                        result = ['Related Q1?', 'Related Q2?'];
                        break;
                    case '/follow-up':
                        result = 'Follow-up question?';
                        break;
                    default:
                        result = { error: 'Unknown endpoint' };
                }
                this._cacheResponse(endpoint, data, result);
                resolve(result);
                return;
            }
            
            // For production, make actual API calls
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: data ? JSON.stringify(data) : null
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Cache successful responses for offline use
            this._cacheResponse(endpoint, data, result);
            
            resolve(result);
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            reject(error);
        }
    }
    
    _getCacheKey(endpoint, data) {
        const dataString = data ? JSON.stringify(data) : '';
        return `api_cache_${endpoint}_${btoa(dataString)}`;
    }
    
    _getCachedResponse(endpoint, data) {
        if (!localStorage) return null;
        
        try {
            const cacheKey = this._getCacheKey(endpoint, data);
            const cachedItem = localStorage.getItem(cacheKey);
            
            if (cachedItem) {
                const { timestamp, result } = JSON.parse(cachedItem);
                
                // Check if cache is still valid (24 hours)
                if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
                    return result;
                } else {
                    // Remove expired cache
                    localStorage.removeItem(cacheKey);
                }
            }
        } catch (error) {
            console.error('Error retrieving from cache:', error);
        }
        
        return null;
    }
    
    _cacheResponse(endpoint, data, result) {
        if (!localStorage) return;
        
        try {
            const cacheKey = this._getCacheKey(endpoint, data);
            const cacheData = {
                timestamp: Date.now(),
                result
            };
            
            localStorage.setItem(cacheKey, JSON.stringify(cacheData));
        } catch (error) {
            console.error('Error storing in cache:', error);
        }
    }

    // API specific methods
    async summarizeText(text) { return this.request('/summarize', 'POST', { text }); }
    async analyzeSentiment(text) { return this.request('/sentiment', 'POST', { text }); }
    async answerQuestion(text, question) { return this.request('/qa', 'POST', { text, question }); }
    async getRelatedQuestions(text, question) { return this.request('/related-questions', 'POST', { text, question }); }
    async getFollowUpQuestion(text, answer) { return this.request('/follow-up', 'POST', { text, answer }); }
    
    // Utility methods
    clearCache() {
        if (!localStorage) return;
        
        try {
            const keysToRemove = [];
            
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('api_cache_')) {
                    keysToRemove.push(key);
                }
            }
            
            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log(`Cleared ${keysToRemove.length} cached API responses.`);
        } catch (error) {
            console.error('Error clearing cache:', error);
        }
    }
}

// Fixed chart-manager.js
export class ChartManager {
    constructor() {
        this.sentimentChart = null;
        this.loadChartLibrary();
    }

    // Dynamically load Chart.js if not already available
    loadChartLibrary() {
        if (window.Chart) return; // Already loaded
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = resolve;
            script.onerror = () => reject(new Error('Failed to load Chart.js'));
            document.head.appendChild(script);
        });
    }

    async createSentimentChart(result) {
        if (!window.Chart) {
            await this.loadChartLibrary();
        }
        
        const canvas = document.getElementById('sentimentChart');
        if (!canvas) {
            console.error('Sentiment chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        if (this.sentimentChart) this.sentimentChart.destroy(); // Clear previous chart

        this.sentimentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Dominant Emotion'],
                datasets: [{
                    label: result.dominant,
                    data: [result.confidence * 100],
                    backgroundColor: 'var(--accent-color, #4a90e2)',
                    borderColor: 'var(--secondary-color, #2c3e50)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, title: { display: true, text: 'Confidence (%)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

// Fixed history-manager.js
export class HistoryManager {
    constructor() {
        this.items = this.loadHistory();
        this.updateHistoryUI();
    }

    loadHistory() {
        try {
            return JSON.parse(localStorage.getItem('historyItems')) || [];
        } catch (error) {
            console.error('Error loading history:', error);
            return [];
        }
    }

    addItem(type, input, data) {
        const item = { type, input, data, id: Date.now() };
        this.items.push(item);
        try {
            localStorage.setItem('historyItems', JSON.stringify(this.items.slice(-10))); // Keep last 10
        } catch (error) {
            console.error('Error saving history:', error);
        }
        this.updateHistoryUI();
    }

    getLastItem(type) {
        const items = this.items.filter(item => item.type === type);
        return items.length > 0 ? items[items.length - 1] : null;
    }

    updateHistoryUI() {
        const historyItemsDiv = document.getElementById('historyItems');
        if (!historyItemsDiv) {
            console.warn('History container not found in DOM');
            return;
        }
        
        historyItemsDiv.innerHTML = this.items.map(item => `
            <div class="history-item" data-type="${item.type}" data-input="${item.input}">
                ${item.type.toUpperCase()}: ${item.input.substring(0, 30)}${item.input.length > 30 ? '...' : ''}
            </div>
        `).join('');
    }

    clearHistory() {
        this.items = [];
        localStorage.removeItem('historyItems');
        this.updateHistoryUI();
    }
}

// Fixed service-worker-registration.js
export function setupServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    } else {
        console.warn('Service Workers not supported');
    }
}

// Fixed speech.js
export function setupSpeechFeatures() {
    const speechSynthesisSupported = 'speechSynthesis' in window;
    const speechRecognitionSupported = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
    
    if (!speechSynthesisSupported && !speechRecognitionSupported) {
        console.warn('Speech features not supported in this browser');
        // Provide fallback
        window.speechManager = {
            speak: text => console.log('Speaking (fallback):', text),
            startVoiceInput: () => alert('Voice input not supported in this browser'),
            stopVoiceInput: () => {}
        };
        return;
    }

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    
    if (speechRecognitionSupported) {
        recognition = new SpeechRecognitionAPI();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
    }

    window.speechManager = {
        speak(text) {
            if (!speechSynthesisSupported) {
                console.log('Speaking (fallback):', text);
                return;
            }
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        },
        startVoiceInput(targetId) {
            if (!recognition) {
                alert('Voice input not supported in this browser');
                return;
            }
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.value = transcript;
                } else {
                    console.error(`Target element ${targetId} not found`);
                }
            };
            recognition.onerror = (event) => console.error('Speech recognition error:', event.error);
            recognition.start();
        },
        stopVoiceInput() {
            if (recognition) recognition.stop();
        }
    };

    // Setup voice button animations
    document.addEventListener('DOMContentLoaded', () => {
        const voiceBtns = document.querySelectorAll('.voice-input-btn');
        if (voiceBtns.length === 0) {
            console.warn('No voice input buttons found');
            return;
        }
        
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
            
            if (recognition) {
                recognition.onend = () => {
                    document.querySelectorAll('.voice-input-btn.active').forEach(activeBtn => {
                        activeBtn.classList.remove('active');
                    });
                };
            }
        });
    });
}

// Fixed ui.js
export function initializeUI() {
    console.log('UI initializing...');
    
    document.addEventListener('DOMContentLoaded', () => {
        // Set default placeholder styles
        const inputText = document.getElementById('inputText');
        const question = document.getElementById('question');
        
        if (inputText) {
            inputText.placeholder = 'Enter your text here for analysis...';
        } else {
            console.warn('inputText element not found');
        }
        
        if (question) {
            question.placeholder = 'Ask your question here...';
        } else {
            console.warn('question element not found');
        }
        // Update offline status
        updateOnlineStatus();
        
        // Add event listeners for online/offline status
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
    });
}

function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offlineIndicator');
    if (offlineIndicator) {
        offlineIndicator.classList.toggle('visible', !navigator.onLine);
    } else {
        console.warn('Offline indicator element not found');
    }
}

// Fixed events.js
export function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    document.addEventListener('DOMContentLoaded', () => {
        // History item clicks
        const historyContainer = document.getElementById('historyContainer');
        if (historyContainer) {
            historyContainer.addEventListener('click', (e) => {
                const historyItem = e.target.closest('.history-item');
                if (historyItem) {
                    const { type, input } = historyItem.dataset;
                    const inputText = document.getElementById('inputText');
                    
                    if (!inputText) {
                        console.error('inputText element not found');
                        return;
                    }
                    
                    if (type === 'qa') {
                        const question = document.getElementById('question');
                        if (!question) {
                            console.error('question element not found');
                            return;
                        }
                        
                        const parts = input.split('Q: ');
                        if (parts.length > 1) {
                            inputText.value = parts[1] || '';
                            question.value = parts[0] || '';
                        } else {
                            inputText.value = input;
                            question.value = '';
                        }
                        
                        if (window.answerQuestion) {
                            window.answerQuestion();
                        } else {
                            console.error('answerQuestion function not found');
                        }
                    } else {
                        inputText.value = input;
                        if (type === 'summary') {
                            if (window.summarizeText) {
                                window.summarizeText();
                            } else {
                                console.error('summarizeText function not found');
                            }
                        } else if (type === 'sentiment') {
                            if (window.analyzeSentiment) {
                                window.analyzeSentiment();
                            } else {
                                console.error('analyzeSentiment function not found');
                            }
                        }
                    }
                }
            });
        } else {
            console.warn('History container not found');
        }

        // Input validation on blur
        const inputText = document.getElementById('inputText');
        const question = document.getElementById('question');
        
        if (inputText) {
            inputText.addEventListener('blur', (e) => {
                if (!e.target.value.trim()) {
                    e.target.classList.add('is-invalid');
                } else {
                    e.target.classList.remove('is-invalid');
                }
            });
        }
        
        if (question) {
            question.addEventListener('blur', (e) => {
                if (!e.target.value.trim()) {
                    e.target.classList.add('is-invalid');
                } else {
                    e.target.classList.remove('is-invalid');
                }
            });
        }
    });
}

// Fixed app.js (main application file)
import { ApiClient } from './api-client.js';
import { HistoryManager } from './history-manager.js';
import { ChartManager } from './chart-manager.js';
import { setupSpeechFeatures } from './speech.js';
import { initializeUI } from './ui.js';
import { setupEventListeners } from './events.js';
import { setupServiceWorker } from './service-worker-registration.js';

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Application initializing...');
    
    // Initialize core services
    window.apiClient = new ApiClient();
    window.historyManager = new HistoryManager();
    window.chartManager = new ChartManager();
    
    // Setup features
    setupSpeechFeatures();
    initializeUI();
    setupEventListeners();
    setupServiceWorker();
    
    // Create rate limiter utility
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
                        lastRun = Date.now();
                        resolve(fn.apply(this, args));
                    }, delay - (now - lastRun));
                });
            }
        };
    };
    
    // Set up main function handlers
    window.summarizeText = window.createRateLimiter(async () => {
        const inputText = document.getElementById('inputText');
        const summaryResult = document.getElementById('summaryResult');
        const summaryConfidence = document.getElementById('summaryConfidence');
        
        if (!inputText) {
            console.error('inputText element not found');
            return;
        }
        
        const text = inputText.value;
        if (!text) {
            alert('Please enter text to summarize');
            return;
        }
        
        const btn = document.getElementById('summarizeBtn');
        if (!btn) {
            console.error('summarizeBtn element not found');
            return;
        }
        
        const originalText = btn.innerHTML;
        btn.innerHTML = '<div class="loader"></div>Processing...';
        btn.disabled = true;
        
        try {
            const result = await window.apiClient.summarizeText(text);
            window.historyManager.addItem('summary', text, result);
            
            if (summaryResult) {
                summaryResult.innerHTML = `
                    <div class="model-info mb-2"><small>📊 ${result.topics.length} Topics</small></div>
                    <div class="result-text">${result.summary}</div>
                    <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
                `;
                
                const speakBtn = summaryResult.querySelector('.speak-btn');
                if (speakBtn && window.speechManager) {
                    speakBtn.addEventListener('click', () => window.speechManager.speak(result.summary));
                }
            } else {
                console.error('summaryResult element not found');
            }
            
            if (summaryConfidence) {
                summaryConfidence.style.width = `${result.confidence * 100}%`;
            } else {
                console.error('summaryConfidence element not found');
            }
        } catch (error) {
            console.error('Summarization error:', error);
            if (summaryResult) {
                summaryResult.innerHTML = '<div class="alert alert-danger">Error processing request</div>';
            }
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }, 1000);

    window.analyzeSentiment = window.createRateLimiter(async () => {
        const inputText = document.getElementById('inputText');
        const sentimentResult = document.getElementById('sentimentResult');
        const sentimentConfidence = document.getElementById('sentimentConfidence');
        const sentimentCompare = document.getElementById('sentimentCompare');
        
        if (!inputText) {
            console.error('inputText element not found');
            return;
        }
        
        const text = inputText.value;
        if (!text) {
            alert('Please enter text for analysis');
            return;
        }
        
        const btn = document.getElementById('sentimentBtn');
        if (!btn) {
            console.error('sentimentBtn element not found');
            return;
        }
        
        const originalText = btn.innerHTML;
        btn.innerHTML = '<div class="loader"></div>Analyzing...';
        btn.disabled = true;
        
        try {
            const result = await window.apiClient.analyzeSentiment(text);
            window.historyManager.addItem('sentiment', text, result);
            
            if (sentimentResult) {
                sentimentResult.innerHTML = `
                    <div class="model-info mb-2"><small>📊 ${result.dominant} | ${(result.confidence * 100).toFixed(1)}%</small></div>
                    <div class="result-text">${result.sentences.map(s => `
                        <div class="mb-2"><span class="emotion-indicator" style="background-color: var(--emotion-${s.emotion}, #ddd)">${s.emotion}</span> ${s.text}</div>
                    `).join('')}</div>
                    <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
                `;
                
                const speakBtn = sentimentResult.querySelector('.speak-btn');
                if (speakBtn && window.speechManager) {
                    speakBtn.addEventListener('click', () => 
                        window.speechManager.speak(`Dominant emotion: ${result.dominant} with ${(result.confidence * 100).toFixed(1)}% confidence`)
                    );
                }
            } else {
                console.error('sentimentResult element not found');
            }
            
            if (sentimentConfidence) {
                sentimentConfidence.style.width = `${result.confidence * 100}%`;
            } else {
                console.error('sentimentConfidence element not found');
            }
            
            if (sentimentCompare) {
                const prev = window.historyManager.getLastItem('sentiment');
                if (prev && prev.id !== result.id) {
                    sentimentCompare.innerHTML = `
                        <div class="compare-item"><div class="compare-header">Current</div><div>${result.dominant}</div><div>${(result.confidence * 100).toFixed(1)}%</div></div>
                        <div class="compare-item"><div class="compare-header">Previous</div><div>${prev.data.dominant}</div><div>${(prev.data.confidence * 100).toFixed(1)}%</div></div>
                    `;
                } else {
                    sentimentCompare.innerHTML = '';
                }
            }
            
            if (window.chartManager) {
                window.chartManager.createSentimentChart(result);
            }
        } catch (error) {
            console.error('Sentiment error:', error);
            if (sentimentResult) {
                sentimentResult.innerHTML = '<div class="alert alert-danger">Error analyzing sentiment</div>';
            }
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }, 1000);

    window.answerQuestion = window.createRateLimiter(async () => {
        const inputText = document.getElementById('inputText');
        const questionInput = document.getElementById('question');
        const answerResult = document.getElementById('answerResult');
        const qaConfidence = document.getElementById('qaConfidence');
        const qaMetrics = document.getElementById('qaMetrics');
        
        if (!inputText || !questionInput) {
            console.error('Input elements not found');
            return;
        }
        
        const text = inputText.value;
        const question = questionInput.value;
        
        if (!text || !question) {
            alert('Please provide both text and question');
            return;
        }
        
        const btn = document.getElementById('qaBtn');
        if (!btn) {
            console.error('qaBtn element not found');
            return;
        }
        
        const originalText = btn.innerHTML;
        btn.innerHTML = '<div class="loader"></div>Finding Answer...';
        btn.disabled = true;
        
        try {
            const result = await window.apiClient.answerQuestion(text, question);
            window.historyManager.addItem('qa', `Q: ${question}`, result);
            
            if (answerResult) {
                answerResult.innerHTML = `
                    <div class="model-info mb-2"><small>📊 ${result.confidence}% Confidence</small></div>
                    <div class="result-text mb-2">${result.answer}</div>
                    <div class="text-muted small">Context: ${result.context}</div>
                    <button class="btn btn-sm btn-outline-primary speak-btn mt-2">🔊 Speak</button>
                `;
                
                const speakBtn = answerResult.querySelector('.speak-btn');
                if (speakBtn && window.speechManager) {
                    speakBtn.addEventListener('click', () => window.speechManager.speak(result.answer));
                }
            } else {
                console.error('answerResult element not found');
            }
            
            if (qaConfidence) {
                qaConfidence.style.width = `${result.confidence}%`;
            } else {
                console.error('qaConfidence element not found');
            }
            
            if (qaMetrics) {
                qaMetrics.innerHTML = `
                    <div>Words: ${result.metrics.wordsAnalyzed}</div>
                    <div>Sentences: ${result.metrics.sentencesAnalyzed}</div>
                    <div>Match: ${result.metrics.matchQuality}%</div>
                `;
            } else {
                console.error('qaMetrics element not found');
            }
            
            generateRelatedQuestions(text, question);
            generateFollowUpQuestion(text, result.answer);
        } catch (error) {
            console.error('Q&A error:', error);
            if (answerResult) {
                answerResult.innerHTML = '<div class="alert alert-danger">Error processing question</div>';
            }
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }, 1000);

    async function generateRelatedQuestions(text, question) {
        const relatedDiv = document.getElementById('relatedQuestions');
        const listDiv = document.getElementById('relatedQuestionsList');
        
        if (!relatedDiv || !listDiv) {
            console.error('Related questions elements not found');
            return;
        }
        
        try {
            const relatedQuestions = await window.apiClient.getRelatedQuestions(text, question);
            
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

    // ...existing code...
async function generateFollowUpQuestion(text, answer) {
    const followUpDiv = document.getElementById('followUpQuestion');
    if (!followUpDiv) {
        console.error('Follow-up question element not found');
        return;
    }
    
    try {
        const followUp = await window.apiClient.getFollowUpQuestion(text, answer);
        
        if (followUp) {
            followUpDiv.textContent = `Follow-up: ${followUp}`;
            followUpDiv.classList.remove('d-none');
            followUpDiv.onclick = () => {
                const questionInput = document.getElementById('question');
                if (questionInput) {
                    questionInput.value = followUp;
                }
            };
        } else {
            followUpDiv.classList.add('d-none');
        }
    } catch (error) {
        console.error('Follow-up question error:', error);
        followUpDiv.classList.add('d-none');
    }
}

// Log application start
console.log('Application loaded successfully');
});