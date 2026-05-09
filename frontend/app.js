// Venture Scout - Professional Frontend Logic

const API_BASE = 'http://localhost:5000/api';
let currentAnalysis = null;

// Analyze repository
async function analyzeRepository() {
    const repoUrl = document.getElementById('repoUrl').value.trim();
    
    if (!repoUrl) {
        alert('Please enter a GitHub repository URL');
        return;
    }
    
    // Validate URL format
    if (!repoUrl.includes('github.com')) {
        alert('Please enter a valid GitHub repository URL');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    // Scroll to loading
    document.getElementById('loading').scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    try {
        const response = await fetch(`${API_BASE}/full-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ repo_url: repoUrl })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentAnalysis = result.data;
            displayResults(result.data);
        } else {
            alert('Analysis failed: ' + result.error);
            document.getElementById('loading').style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze repository. Please ensure the backend server is running.');
        document.getElementById('loading').style.display = 'none';
    }
}

// Display analysis results
function displayResults(data) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'flex';
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    
    // Display all sections
    displayScore(data.scoring, data.trend_analysis);
    displayRepoInfo(data.repo_info);
    displayAIAnalysis(data.ai_analysis);
    displaySentiment(data.sentiment_analysis);
    displayTrends(data.trend_analysis);
    displayScoreBreakdown(data.scoring);
    displayMemo(data.investment_memo);
    displayInsights(data.recommendation);
    displayRisksOpportunities(data.recommendation);
}

// Display score card
function displayScore(scoring, trends) {
    const score = scoring.final_score;
    const grade = scoring.grade;
    const recommendation = scoring.recommendation;
    
    document.getElementById('finalScore').textContent = score.toFixed(0);
    document.getElementById('grade').textContent = grade;
    document.getElementById('recommendation').textContent = recommendation;
    
    // Risk level
    const riskScore = scoring.breakdown.risk;
    let riskLevel = 'Low';
    if (riskScore < 50) riskLevel = 'High';
    else if (riskScore < 70) riskLevel = 'Medium';
    document.getElementById('riskLevel').textContent = riskLevel;
    
    // Market timing
    document.getElementById('marketTiming').textContent = trends.market_timing || 'Unknown';
    
    // Color code score
    const scoreElement = document.querySelector('.score-value');
    if (score >= 80) {
        scoreElement.style.color = '#10b981';
    } else if (score >= 65) {
        scoreElement.style.color = '#3b82f6';
    } else if (score >= 50) {
        scoreElement.style.color = '#f59e0b';
    } else {
        scoreElement.style.color = '#ef4444';
    }
}

// Display repository information
function displayRepoInfo(info) {
    const html = `
        <div class="info-grid">
            <div class="info-item">
                <strong>Repository</strong>
                <span>${info.name}</span>
            </div>
            <div class="info-item">
                <strong>Stars</strong>
                <span>${info.stars.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <strong>Forks</strong>
                <span>${info.forks.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <strong>Language</strong>
                <span>${info.language}</span>
            </div>
            <div class="info-item" style="grid-column: 1 / -1;">
                <strong>Description</strong>
                <span>${info.description || 'No description available'}</span>
            </div>
            <div class="info-item" style="grid-column: 1 / -1;">
                <strong>URL</strong>
                <a href="${info.url}" target="_blank" style="color: #667eea;">${info.url}</a>
            </div>
        </div>
    `;
    document.getElementById('repoInfo').innerHTML = html;
}

// Display AI analysis
function displayAIAnalysis(analysis) {
    const html = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
                <strong style="color: #1f2937;">Technology Summary</strong>
                <p style="margin-top: 0.5rem;">${analysis.technology_summary || 'Analysis in progress...'}</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div>
                    <strong style="color: #1f2937;">Innovation Score</strong>
                    <p style="margin-top: 0.25rem; font-size: 1.5rem; font-weight: 600; color: #667eea;">
                        ${analysis.innovation_score || 'N/A'}/100
                    </p>
                </div>
                <div>
                    <strong style="color: #1f2937;">Technical Complexity</strong>
                    <p style="margin-top: 0.25rem; font-size: 1.5rem; font-weight: 600; color: #667eea;">
                        ${analysis.technical_complexity || 'N/A'}
                    </p>
                </div>
                <div>
                    <strong style="color: #1f2937;">Scalability</strong>
                    <p style="margin-top: 0.25rem;">${analysis.scalability_potential || 'N/A'}</p>
                </div>
                <div>
                    <strong style="color: #1f2937;">AI Recommendation</strong>
                    <p style="margin-top: 0.25rem;">${analysis.recommendation || 'N/A'}</p>
                </div>
            </div>
        </div>
    `;
    document.getElementById('aiAnalysis').innerHTML = html;
}

// Display sentiment analysis
function displaySentiment(sentiment) {
    const overall = sentiment.overall_sentiment;
    const score = sentiment.sentiment_score;
    
    const html = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span class="sentiment-badge ${overall.toLowerCase()}">${overall}</span>
                <span style="font-size: 1.25rem; font-weight: 600;">${score}/100</span>
            </div>
            <div>
                <strong style="color: #1f2937;">Polarity</strong>
                <p style="margin-top: 0.25rem;">${sentiment.overall_polarity}</p>
            </div>
        </div>
    `;
    document.getElementById('sentimentAnalysis').innerHTML = html;
}

// Display trend analysis
function displayTrends(trends) {
    const categories = trends.trending_categories || [];
    const html = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div>
                    <strong style="color: #1f2937;">Trend Score</strong>
                    <p style="font-size: 1.5rem; font-weight: 600; color: #667eea; margin-top: 0.25rem;">
                        ${trends.trend_score}/100
                    </p>
                </div>
                <div>
                    <strong style="color: #1f2937;">Trend Strength</strong>
                    <p style="margin-top: 0.25rem;">${trends.trend_strength}</p>
                </div>
                <div>
                    <strong style="color: #1f2937;">Growth Velocity</strong>
                    <p style="margin-top: 0.25rem;">${trends.growth_velocity}</p>
                </div>
                <div>
                    <strong style="color: #1f2937;">Market Timing</strong>
                    <p style="margin-top: 0.25rem;">${trends.market_timing}</p>
                </div>
            </div>
            <div>
                <strong style="color: #1f2937;">Categories</strong>
                <div style="margin-top: 0.5rem;">
                    ${categories.map(cat => `<span class="category-badge">${cat}</span>`).join('')}
                </div>
            </div>
        </div>
    `;
    document.getElementById('trendAnalysis').innerHTML = html;
}

// Display score breakdown
function displayScoreBreakdown(scoring) {
    const breakdown = scoring.breakdown;
    let html = '<div class="score-bars">';
    
    for (const [factor, score] of Object.entries(breakdown)) {
        const capitalizedFactor = factor.charAt(0).toUpperCase() + factor.slice(1);
        html += `
            <div class="score-bar-item">
                <div class="score-bar-label">${capitalizedFactor}</div>
                <div class="score-bar-container">
                    <div class="score-bar-fill" style="width: ${score}%"></div>
                </div>
                <div class="score-bar-value">${score.toFixed(0)}</div>
            </div>
        `;
    }
    
    html += '</div>';
    document.getElementById('scoreBreakdown').innerHTML = html;
}

// Display investment memo
function displayMemo(memo) {
    const memoText = memo.memo || 'Generating investment memo...';
    document.getElementById('investmentMemo').innerHTML = `<pre>${memoText}</pre>`;
}

// Display key insights
function displayInsights(recommendation) {
    const insights = recommendation.key_insights || [];
    const html = `
        <ul>
            ${insights.map(insight => `<li>${insight}</li>`).join('')}
        </ul>
    `;
    document.getElementById('keyInsights').innerHTML = html;
}

// Display risks and opportunities
function displayRisksOpportunities(recommendation) {
    const risks = recommendation.risks || [];
    const opportunities = recommendation.opportunities || [];
    
    const risksHtml = risks.length > 0 ? `
        <ul style="list-style: none; display: flex; flex-direction: column; gap: 1rem;">
            ${risks.map(risk => `
                <li style="padding: 1rem; background: #fef2f2; border-radius: 8px;">
                    <strong style="color: #ef4444;">${risk.type}</strong>
                    <span style="color: #6b7280; font-size: 0.875rem;"> (${risk.severity})</span>
                    <p style="margin-top: 0.5rem; color: #374151;">${risk.description}</p>
                </li>
            `).join('')}
        </ul>
    ` : '<p style="color: #6b7280;">No significant risks identified</p>';
    
    const oppsHtml = opportunities.length > 0 ? `
        <ul style="list-style: none; display: flex; flex-direction: column; gap: 1rem;">
            ${opportunities.map(opp => `
                <li style="padding: 1rem; background: #f0fdf4; border-radius: 8px;">
                    <strong style="color: #10b981;">${opp.type}</strong>
                    <span style="color: #6b7280; font-size: 0.875rem;"> (${opp.potential})</span>
                    <p style="margin-top: 0.5rem; color: #374151;">${opp.description}</p>
                </li>
            `).join('')}
        </ul>
    ` : '<p style="color: #6b7280;">Analyzing opportunities...</p>';
    
    document.getElementById('risks').innerHTML = risksHtml;
    document.getElementById('opportunities').innerHTML = oppsHtml;
}

// Load trending projects
async function loadTrending() {
    try {
        const response = await fetch(`${API_BASE}/trending?limit=6`);
        const result = await response.json();
        
        if (result.success) {
            displayTrendingProjects(result.data);
        }
    } catch (error) {
        console.error('Error loading trending:', error);
    }
}

// Display trending projects
function displayTrendingProjects(projects) {
    const html = projects.map(project => `
        <div class="project-card" onclick="document.getElementById('repoUrl').value='${project.repo_url}'; document.getElementById('repoUrl').scrollIntoView({behavior: 'smooth'});">
            <h4>${project.repo_name || project.name}</h4>
            <p>${(project.description || '').substring(0, 100)}${project.description && project.description.length > 100 ? '...' : ''}</p>
            <div class="project-stats">
                <span>⭐ ${project.stars.toLocaleString()}</span>
                <span>🔱 ${project.forks.toLocaleString()}</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('trendingProjects').innerHTML = html;
}

// Auto-load trending on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTrending();
});
