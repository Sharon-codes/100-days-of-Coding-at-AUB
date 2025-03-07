// chart-manager.js
export class ChartManager {
    constructor() {
        this.sentimentChart = null;
        this.ensureChartLibrary();
    }

    ensureChartLibrary() {
        if (!window.Chart) {
            console.error('Chart.js not loaded. Ensure it’s included in the HTML.');
        }
    }

    createSentimentChart(result) {
        console.log('Creating sentiment chart with result:', result);
        const canvas = document.getElementById('sentimentChart');
        if (!canvas) {
            console.error('Sentiment chart canvas not found');
            return;
        }
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Failed to get 2D context for sentiment chart');
            return;
        }
        if (this.sentimentChart) {
            this.sentimentChart.destroy();
        }
        try {
            this.sentimentChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Dominant Emotion'],
                    datasets: [{
                        label: result.dominant,
                        data: [result.confidence * 100],
                        backgroundColor: '#4a90e2',
                        borderColor: '#2c3e50',
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
            console.log('Sentiment chart created successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    }
}