// PERSON 4: AI Insights Visualization
// Real-time visualization of AI analysis results

// Animate score bars
function animateScoreBars() {
    const bars = document.querySelectorAll('.score-bar-fill');
    bars.forEach((bar, index) => {
        setTimeout(() => {
            bar.style.width = bar.style.width;
        }, index * 100);
    });
}

// Create visual indicators for sentiment
function visualizeSentiment(sentiment) {
    const emoji = {
        'Positive': '😊',
        'Neutral': '😐',
        'Negative': '😞'
    };
    
    return emoji[sentiment] || '🤔';
}

// Create trend indicator
function visualizeTrend(trendScore) {
    if (trendScore > 75) return '🚀 Hot Trend';
    if (trendScore > 50) return '📈 Trending';
    if (trendScore > 25) return '📊 Moderate';
    return '📉 Low Trend';
}

// Animate numbers counting up
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = current.toFixed(1);
    }, 16);
}

// Create sparkline for metrics
function createSparkline(values) {
    const max = Math.max(...values);
    const normalized = values.map(v => (v / max) * 100);
    
    return normalized.map((v, i) => {
        const height = v;
        return `<div class="sparkline-bar" style="height: ${height}%"></div>`;
    }).join('');
}

// Highlight key insights with icons
function highlightInsights(insights) {
    const icons = {
        'traction': '⭐',
        'innovation': '💡',
        'trend': '📈',
        'risk': '⚠️',
        'opportunity': '✨'
    };
    
    return insights.map(insight => {
        let icon = '•';
        for (const [key, value] of Object.entries(icons)) {
            if (insight.toLowerCase().includes(key)) {
                icon = value;
                break;
            }
        }
        return `${icon} ${insight}`;
    });
}

// Create recommendation badge
function createRecommendationBadge(recommendation) {
    const colors = {
        'Strong Invest': '#10b981',
        'Invest': '#3b82f6',
        'Monitor': '#f59e0b',
        'Pass': '#ef4444'
    };
    
    const color = colors[recommendation] || '#6b7280';
    return `<span style="background: ${color}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">${recommendation}</span>`;
}

// Initialize visualizations when results are displayed
document.addEventListener('DOMContentLoaded', () => {
    // Observer for when results section becomes visible
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.id === 'results' && mutation.target.style.display !== 'none') {
                setTimeout(animateScoreBars, 300);
            }
        });
    });
    
    const resultsElement = document.getElementById('results');
    if (resultsElement) {
        observer.observe(resultsElement, {
            attributes: true,
            attributeFilter: ['style']
        });
    }
});
