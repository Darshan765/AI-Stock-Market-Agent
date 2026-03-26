// Elements
const stockInput = document.getElementById('stock-input');
const analyzeBtn = document.getElementById('analyze-btn');
const tickerContainer = document.getElementById('ticker-container');
const loadingOverlay = document.getElementById('loading-overlay');
const resultsContainer = document.getElementById('results-container');
const emptyState = document.getElementById('empty-state');

// Load live prices on mount
document.addEventListener('DOMContentLoaded', fetchLivePrices);

// Listen to Enter key
stockInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        analyzeStock();
    }
});

analyzeBtn.addEventListener('click', analyzeStock);

async function fetchLivePrices() {
    try {
        const response = await fetch('/api/live-prices');
        const data = await response.json();
        
        tickerContainer.innerHTML = ''; // Clear loading pulse
        
        for (const [symbol, price] of Object.entries(data)) {
            const pill = document.createElement('div');
            pill.className = 'price-pill';
            
            const symSpan = document.createElement('span');
            symSpan.className = 'sym';
            symSpan.textContent = symbol;
            
            const prSpan = document.createElement('span');
            prSpan.className = 'pr';
            if (price !== null) {
                prSpan.textContent = `$${price.toFixed(2)}`;
            } else {
                prSpan.textContent = 'N/A';
                prSpan.style.color = 'var(--color-red)';
            }
            
            pill.appendChild(symSpan);
            pill.appendChild(prSpan);
            tickerContainer.appendChild(pill);
        }
    } catch (e) {
        console.error("Error fetching live prices:", e);
        tickerContainer.innerHTML = '<div style="color:var(--color-red);font-size:0.9rem;">Failed to load live prices</div>';
    }
}

async function analyzeStock() {
    const query = stockInput.value.trim();
    if (!query) return;

    // UI State: Loading
    emptyState.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    loadingOverlay.classList.remove('hidden');
    
    // Reset steps
    document.querySelectorAll('.step').forEach(el => {
        el.classList.remove('active', 'done');
    });
    
    try {
        setStep('step-data');
        // Simulated progress mapping since it's a single API call on the backend
        setTimeout(() => setStep('step-rsi', true), 1500);
        setTimeout(() => setStep('step-news', true), 3000);
        setTimeout(() => setStep('step-ai', true), 4500);

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stock: query })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'API Error');
        
        // Populate Data
        document.getElementById('analyzed-stock-name').textContent = `Analysis for: ${data.stock}`;
        
        // RSI
        document.getElementById('res-rsi').textContent = data.rsi !== null ? data.rsi : 'N/A';
        const rsiColor = data.rsi !== null ? (data.rsi < 30 ? 'var(--color-green)' : (data.rsi > 70 ? 'var(--color-red)' : 'var(--color-yellow)')) : 'var(--text-muted)';
        document.getElementById('res-rsi').style.color = rsiColor;

        // Sentiment
        const sentVal = data.sentiment.compound;
        document.getElementById('res-sentiment').textContent = sentVal.toFixed(2);
        const sentColor = sentVal > 0.1 ? 'var(--color-green)' : (sentVal < -0.1 ? 'var(--color-red)' : 'var(--color-yellow)');
        document.getElementById('res-sentiment').style.color = sentColor;
        document.getElementById('ind-sentiment').textContent = sentVal > 0.1 ? '(Positive)' : (sentVal < -0.1 ? '(Negative)' : '(Neutral)');
        document.getElementById('ind-sentiment').style.color = sentColor;

        // Price
        document.getElementById('res-price').textContent = data.price !== null ? `$${data.price.toFixed(2)}` : 'N/A';

        // News
        const newsList = document.getElementById('res-news');
        newsList.innerHTML = '';
        data.news.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            newsList.appendChild(li);
        });

        // AI Recommendation
        const explContainer = document.getElementById('res-explanation');
        explContainer.innerHTML = '';
        const decisionText = data.llm.decision || "No recommendation available.";
        
        // Very basic markdown parsing for bullet points and bold text
        const parsedText = decisionText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\*/g, '<br>•');
            
        explContainer.innerHTML = parsedText;

        // Try to parse out BUY/SELL/HOLD for the badge
        const badge = document.getElementById('ai-decision-badge');
        const upperDec = decisionText.toUpperCase();
        badge.className = 'badge'; // reset
        if (upperDec.includes('BUY')) {
            badge.textContent = 'BUY';
            badge.classList.add('buy');
        } else if (upperDec.includes('SELL')) {
            badge.textContent = 'SELL';
            badge.classList.add('sell');
        } else {
            badge.textContent = 'HOLD';
            badge.classList.add('hold');
        }

        // Show Results
        loadingOverlay.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        alert('Failed to analyze stock: ' + error.message);
        loadingOverlay.classList.add('hidden');
        emptyState.classList.remove('hidden');
    }
}

function setStep(stepId, markPrevDone = false) {
    if (markPrevDone) {
        const active = document.querySelector('.step.active');
        if (active) {
            active.classList.remove('active');
            active.classList.add('done');
        }
    }
    const step = document.getElementById(stepId);
    if (step) {
        step.classList.remove('done');
        step.classList.add('active');
    }
}
