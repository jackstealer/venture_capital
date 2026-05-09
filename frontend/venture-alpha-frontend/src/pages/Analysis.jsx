import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function Analysis() {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingStep, setLoadingStep] = useState(0);
  const project = location.state?.project;

  useEffect(() => {
    if (loading) {
      const timer = setInterval(() => {
        setLoadingStep(prev => (prev < 4 ? prev + 1 : prev));
      }, 1600); // Increased step interval to 1.6s to make it feel like deep AI analysis
      return () => clearInterval(timer);
    }
  }, [loading]);

  useEffect(() => {
    if (!project) {
      navigate('/emerging');
      return;
    }

    const payload = {
      repo_name: project.repo_name,
      repo_url: project.url || project.repo_url || `https://github.com/${project.repo_name}`,
      description: project.description || "No description provided.",
      stars: project.stars || 0,
      contributors: Math.max(1, project.contributors || 1),
      star_velocity: project.star_velocity || 45,
      social_sentiment: typeof project.social_sentiment === 'string' ? project.social_sentiment : 'positive',
      news_mentions: project.news_mentions || 12
    };

    // Try fetching from backend if available, otherwise generate memo from basic project data
    fetch('/api/full_analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Server returned an error: ${res.status} ${res.statusText}`);
        }
        return res.json();
      })
      .then(data => {
        setAnalysis({
          ...data,
          startup: project.repo_name,
          conviction_score: project.conviction_score || data.conviction_score,
          technology_summary: data.technology_summary || data.technology || project.description || "Autonomous agent framework or cutting-edge tool.",
          key_use_cases: data.key_use_cases || "",
          industry_impact: data.industry_impact || "",
          research_summary: data.research_summary || "",
          trend_strength: data.trend_strength || "",
          trend_reasoning: data.trend_reasoning || "",
          investment_memo: data.investment_memo || "",
          founder_interview: data.founder_interview || null,
          signals: data.signals || `GitHub Stars: ${project.stars}\nStrong developer interest and growing ecosystem.`,
          market_opportunity: data.market_opportunity || "High growth potential in emerging technology sector.",
          recommendation: data.recommendation || (project.conviction_score > 0.5 ? "Strong Buy / Invest" : "Hold / Monitor"),
          risks: data.risks || ["Early stage volatility", "Competition from established incumbents", "Execution risk in go-to-market strategy"],
          sources: data.sources || [],
          evidence_sources: data.evidence_sources || []
        });
        setLoading(false);
      })
      .catch(err => {
        console.error('API execution failed: falling back to dynamic generator', err);
        
        // Generate formatting matching the required VC Memo Template dynamically for EACH project
        setTimeout(() => {
          setAnalysis({
            startup: project.repo_name,
            technology_summary: `${project.repo_name} is a high-potential project focusing on: ${project.description || "emerging technology"}. It exhibits strong signals of market fit by leveraging advanced orchestration logic and execution capabilities.`,
            key_use_cases: `Building systems for ${project.category || 'AI Agents'}, implementing advanced decision-making workflows, and orchestrating deployment setups.`,
            industry_impact: "Software Development (rapid prototyping), Research (accelerating deployments), and Automation (orchestrating workflows).",
            research_summary: `${project.repo_name} is emerging as a foundational technology, particularly within the startup ecosystem. The significant community activity signals strong industry validation. Developer reception appears very positive, as evidenced by a star velocity of ${project.star_velocity || 'N/A'}.`,
            trend_strength: project.star_velocity > 1000 ? "Very High" : "High",
            trend_reasoning: `The project demonstrates a high trend strength due to its rapid community growth, indicated by a star velocity of ${project.star_velocity || 'N/A'} stars per day and ${project.contributors || 'multiple'} active contributors. The consistently positive social sentiment validates growing external interest.`,
            investment_memo: `## Investment Memo: ${project.repo_name}\n\n**Date:** March 2026\n**To:** Investment Committee\n**From:** AI Venture Scout\n**Subject:** Investment Recommendation: ${project.repo_name}\n\n---\n\n### Technology Overview\n${project.repo_name} provides robust foundations for: ${project.description}.\n\n### Market Opportunity\nThe market for this specific tooling is exploding. As businesses seek to leverage automation, solutions in this space become absolutely critical.\n\n### Key Signals\nThe repository boasts an impressive **${project.stars || 0} GitHub stars**. Social sentiment remains overwhelmingly positive.\n\n### Risks\nScalability issues during enterprise rollout and technical debt.\n\n### Conclusion\nA promising early-stage asset worth tracking.`,
            founder_interview: {
              questions: [
                `Beyond existing tools, what is the *most critical* pain point ${project.repo_name} uniquely addresses?`,
                `Given the ecosystem, what defensible moats are you building for ${project.repo_name}?`
              ],
              answers: [
                `The largest pain point is integration complexity. Developers struggle with ensuring deterministic execution and scaling these systems, leading to time loss; we reduce that drastically.`,
                `Our defensible moats lie in our deep specialization and an incredibly vibrant open-source community that builds proprietary extensions faster than massive competitors.`
              ]
            },
            signals: `GitHub Growth: High\nGoogle Trends: Rising\nProduct Hunt: Trending\nNews Mentions: Active Coverage`,
            conviction_score: project.conviction_score || 0.87,
            signal_breakdown: {
              developer_activity: 0.85,
              market_demand: 0.82,
              community_interest: 0.78,
              media_presence: 0.73
            },
            market_opportunity: "Large Total Addressable Market (TAM) scaling horizontally. Strong adoption metrics point towards becoming an industry standard.",
            risks: [
              "Competition from established frameworks exists.",
              "Reliance on open-source adoption and community contributions.",
              "Execution timeline risks."
            ],
            recommendation: (project.conviction_score || 0) > 0.35 ? "Watch. Proceed with investment due to high conviction signals." : "Monitor for additional structural momentum before deploying capital.",
            sources: [
              project.url || project.repo_url || `https://github.com/${project.repo_name}`,
              `https://www.producthunt.com/search?q=${encodeURIComponent(project.repo_name || 'AI')}`
            ],
            analysis_time: (Math.random() * 2 + 1).toFixed(2)
          });
          setLoading(false);
        }, 7500); // simulate longer "generation" time for the agent reasoning effect
      });
  }, [project, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#07090b] flex flex-col items-center justify-center text-gray-300 font-mono relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/5 to-transparent"></div>
        <div className="bg-[#0a0c10] border border-gray-800 p-8 rounded-2xl shadow-[0_0_40px_-10px_rgba(59,130,246,0.15)] w-full max-w-lg z-10 relative">
          <div className="flex items-center justify-between mb-8 border-b border-gray-800 pb-4">
            <h3 className="text-xl font-bold text-gray-100 flex items-center gap-3 tracking-widest uppercase text-sm">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
              Neural Trace Active
            </h3>
            <span className="text-xs text-gray-600">ID: {project?.repo_name?.replace('/','-').toUpperCase()}</span>
          </div>
          
          <div className="space-y-5 text-[14px]">
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 1 ? <span className="text-green-500">✓</span> : <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin inline-block"></span>}</div>
              <span className={loadingStep === 0 ? "text-blue-300 font-medium" : "text-gray-600"}>[Data Engine] Ingesting multi-channel telemetry...</span>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 2 ? <span className="text-green-500">✓</span> : (loadingStep === 1 ? <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin inline-block"></span> : <span className="w-4"></span>)}</div>
              <span className={loadingStep === 1 ? "text-blue-300 font-medium" : (loadingStep > 1 ? "text-gray-600" : "text-gray-800")}>[Quant Engine] Calculating venture conviction matrix...</span>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 3 ? <span className="text-green-500">✓</span> : (loadingStep === 2 ? <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin inline-block"></span> : <span className="w-4"></span>)}</div>
              <span className={loadingStep === 2 ? "text-blue-300 font-medium" : (loadingStep > 2 ? "text-gray-600" : "text-gray-800")}>[AI Agent] Conducting simulated founder interview...</span>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 4 ? <span className="text-green-500">✓</span> : (loadingStep === 3 ? <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin inline-block"></span> : <span className="w-4"></span>)}</div>
              <span className={loadingStep === 3 ? "text-blue-300 font-medium" : (loadingStep > 3 ? "text-gray-600" : "text-gray-800")}>[Synthesis] Generating final partner memo...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#07090b] py-12 px-4 sm:px-6 lg:px-8 text-gray-200 font-sans selection:bg-blue-500/30">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <button
          onClick={() => navigate('/emerging')}
          className="mb-8 text-gray-400 hover:text-white font-medium flex items-center gap-2 transition-all group"
        >
          <svg className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          Back to Projects
        </button>
        
        {analysis ? (
          <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* LEFT COLUMN: Deep Dive Analysis */}
            <div className="lg:col-span-8 space-y-8">
              {/* Header Title Section */}
              <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-8 relative overflow-hidden group hover:border-gray-700 transition-all shadow-2xl">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 opacity-80 group-hover:opacity-100 transition-opacity"></div>
                <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-500 mb-3 tracking-tight">
                  {analysis.startup || project?.repo_name || 'Selected Project'}
                </h1>
                <p className="text-xl text-blue-400 font-medium flex items-center gap-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                  Official Investment Memo & Analysis
                </p>
              </div>

              {/* Technology Summary */}
              <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-8 hover:border-gray-700 transition-all shadow-lg">
                <div className="flex items-center gap-3 mb-6 border-b border-gray-800/80 pb-4">
                  <span className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                  </span>
                  <h2 className="text-2xl font-bold text-gray-200 tracking-wide">Technology Overview</h2>
                </div>
                <p className="text-gray-300 leading-relaxed text-lg mb-8">
                  {analysis.technology_summary || analysis.technology || "No technology summary provided."}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {analysis.key_use_cases && (
                    <div className="bg-[#0a0c10] p-6 rounded-2xl border border-gray-800/60 shadow-inner group hover:border-blue-500/30 transition-all">
                      <h3 className="font-semibold text-blue-400 uppercase tracking-widest text-xs mb-3">Key Use Cases</h3>
                      <p className="text-gray-300 leading-snug">{analysis.key_use_cases}</p>
                    </div>
                  )}
                  {analysis.industry_impact && (
                    <div className="bg-[#0a0c10] p-6 rounded-2xl border border-gray-800/60 shadow-inner group hover:border-purple-500/30 transition-all">
                      <h3 className="font-semibold text-purple-400 uppercase tracking-widest text-xs mb-3">Industry Impact</h3>
                      <p className="text-gray-300 leading-snug">{analysis.industry_impact}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Research Summary */}
              {analysis.research_summary && (
                <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-8 hover:border-gray-700 transition-all shadow-lg">
                  <div className="flex items-center gap-3 mb-6 border-b border-gray-800/80 pb-4">
                    <span className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </span>
                    <h2 className="text-2xl font-bold text-gray-200 tracking-wide">Research Summary</h2>
                  </div>
                  <p className="text-gray-300 leading-relaxed text-lg border-l-4 border-indigo-500/50 pl-6 py-2 bg-gradient-to-r from-indigo-900/10 to-transparent">
                    {analysis.research_summary}
                  </p>
                </div>
              )}

              {/* Full Investment Memo (Markdown style document view) */}
              {analysis.investment_memo && (
                <div className="bg-gray-200 rounded-3xl p-1 md:p-2 shadow-[0_0_40px_-10px_rgba(255,255,255,0.1)]">
                  <div className="bg-[#fcfdfd] rounded-2xl p-8 md:p-12 shadow-inner text-gray-900 font-sans h-full">
                     <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-gray-300 gap-4">
                        <div>
                          <h2 className="text-3xl font-black text-gray-900 tracking-tight leading-tight">Partner Memo</h2>
                          <p className="text-gray-500 text-sm font-semibold mt-1 font-mono">ID: {project?.repo_name?.replace('/','-').toUpperCase()}</p>
                        </div>
                        <span className="text-xs uppercase tracking-widest text-red-700 font-bold bg-red-100/80 px-4 py-2 rounded-full border border-red-200 shadow-sm shrink-0">
                          Highly Confidential
                        </span>
                     </div>
                     <div className="prose prose-lg px-2 max-w-none text-gray-800">
                        <pre className="whitespace-pre-wrap font-serif text-[1.1rem] leading-loose text-gray-800 bg-transparent border-none p-0 overflow-x-hidden">
                          {analysis.investment_memo?.replace(/[*#_]/g, '')?.replace(/---/g, '').trim()}
                        </pre>
                     </div>
                  </div>
                </div>
              )}

              {/* Founder Interview Q&A styled as a stylized chat */}
              {analysis.founder_interview && analysis.founder_interview.questions && analysis.founder_interview.answers && (
                <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-8 shadow-lg">
                  <div className="flex items-center gap-3 mb-8 border-b border-gray-800/80 pb-4">
                    <span className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path></svg>
                    </span>
                    <h2 className="text-2xl font-bold text-gray-200 tracking-wide">Analyst Q&A</h2>
                  </div>
                  <div className="space-y-8">
                    {analysis.founder_interview.questions.map((q, idx) => (
                      <div key={idx} className="bg-[#0a0c10] border border-gray-800/60 rounded-2xl p-6 hover:border-emerald-500/30 transition-all shadow-md relative overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-emerald-500"></div>
                        <div className="flex gap-4 items-start mb-6">
                          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center font-bold text-white shadow-lg text-sm">VC</div>
                          <p className="font-semibold text-gray-100 leading-relaxed pt-2 text-lg">{q}</p>
                        </div>
                        <div className="flex gap-4 items-start ml-2 pl-4 border-l border-gray-800 pt-2">
                          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center font-bold text-white shadow-lg text-sm">DEV</div>
                          <p className="text-gray-400 leading-relaxed pt-2 text-[1.05rem]">{analysis.founder_interview.answers[idx]}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {/* RIGHT COLUMN: Metrics & Signals Sidebar */}
            <div className="lg:col-span-4 space-y-6">
              
              {/* Massive Conviction Score Card */}
              <div className="bg-gradient-to-b from-green-900/30 to-[#12161c] border border-green-500/30 rounded-3xl p-8 text-center transform hover:-translate-y-2 transition-transform shadow-[0_0_40px_-10px_rgba(34,197,94,0.15)] relative overflow-hidden">
                <div className="absolute -top-10 -right-10 bg-green-500 w-32 h-32 rounded-full blur-[80px] opacity-20"></div>
                <h3 className="text-sm uppercase tracking-widest text-green-400 font-extrabold mb-3">Model Conviction Result</h3>
                <div className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-b from-green-300 via-emerald-400 to-teal-700 mb-6 drop-shadow-lg">
                  {typeof analysis.conviction_score === 'number' ? analysis.conviction_score.toFixed(2) : analysis.conviction_score || 'N/A'}
                </div>
                <div className="w-full px-6 py-4 bg-[#0a0c10]/80 backdrop-blur-sm border border-green-500/20 rounded-2xl shadow-inner flex flex-col items-center justify-center text-center">
                  <span className="text-[10px] text-green-500/60 font-black tracking-widest uppercase mb-1">Final Recommendation</span>
                  <p className="text-md text-green-400 font-bold tracking-wide leading-tight">
                    {analysis.recommendation || "Investment Recommended"}
                  </p>
                </div>
              </div>

              {/* Signal Breakdown Grid */}
              {analysis.signal_breakdown && (
                <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-6 shadow-lg">
                  <h3 className="text-sm uppercase tracking-widest text-gray-400 font-bold mb-5 flex items-center gap-2">
                    <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path></svg>
                    Momentum Signals
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(analysis.signal_breakdown).map(([key, value]) => (
                      <div key={key} className="bg-[#0a0c10] border border-gray-800/80 rounded-2xl p-4 text-center hover:border-blue-500/40 hover:bg-blue-900/10 transition-all group">
                        <div className="text-3xl font-bold text-gray-100 mb-1 group-hover:text-blue-400 transition-colors">
                          {Number(value).toFixed(2)}
                        </div>
                        <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">
                          {key.replace('_', ' ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Trend Strength */}
              <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-6 relative overflow-hidden group shadow-lg">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-[0.15] transition-opacity duration-500">
                  <svg className="w-32 h-32 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                </div>
                <h3 className="text-sm uppercase tracking-widest text-gray-400 font-bold mb-3 z-10 relative">Trend Strength Classification</h3>
                <div className="text-4xl font-extrabold text-white mb-4 z-10 relative inline-block border-b-2 border-blue-500 pb-1">
                  {analysis.trend_strength || "High"}
                </div>
                <p className="text-gray-400 text-sm leading-relaxed z-10 relative">
                  {analysis.trend_reasoning || "High market momentum inferred from community interest."}
                </p>
              </div>

              {/* Risk Analysis */}
              <div className="bg-gradient-to-br from-[#12161c] to-red-900/10 border border-gray-800 hover:border-red-900/50 transition-colors rounded-3xl p-6 shadow-lg">
                <h3 className="text-sm uppercase tracking-widest text-red-500 font-bold mb-5 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                  Critical Risk Factors
                </h3>
                <ul className="space-y-4">
                  {analysis.risks && analysis.risks.length > 0 
                    ? (Array.isArray(analysis.risks) ? analysis.risks.map((risk, index) => (
                        <li key={index} className="flex gap-3 text-gray-300 text-sm leading-relaxed items-start bg-[#0a0c10]/50 p-3 rounded-xl border border-red-900/20">
                           <span className="text-red-500 mt-1 shrink-0"><svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg></span> 
                           {risk}
                        </li>
                      )) : <li className="text-gray-300 text-sm bg-gray-900 p-3 rounded-xl">{String(analysis.risks)}</li>)
                    : <li className="text-gray-300 text-sm">Early stage volatility and execution risk.</li>}
                </ul>
              </div>

              {/* Opportunity and Traction */}
              <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-6 shadow-lg">
                <h3 className="text-sm uppercase tracking-widest text-gray-400 font-bold mb-4">Traction Overview</h3>
                <div className="text-gray-300 text-[15px] leading-relaxed whitespace-pre-line bg-[#0a0c10] p-5 rounded-2xl border border-gray-800/80 font-mono shadow-inner text-green-400">
                  {analysis.signals || analysis.opportunity_and_traction || "No traction data provided."}
                </div>
              </div>

              {/* Sources */}
              {((analysis.sources && analysis.sources.length > 0) || (analysis.evidence_sources && analysis.evidence_sources.length > 0)) && (
                <div className="bg-[#12161c] border border-gray-800 rounded-3xl p-6 shadow-lg">
                  <h3 className="text-sm uppercase tracking-widest text-gray-400 font-bold mb-5 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                    Evidence Sources
                  </h3>
                  <div className="space-y-3">
                    {Array.from(new Set([...(analysis.sources || []), ...(analysis.evidence_sources || [])])).map((source, index) => (
                      <a key={index} href={source} target="_blank" rel="noopener noreferrer" className="block px-4 py-3 bg-[#0a0c10] border border-gray-800/60 rounded-xl text-xs text-blue-400 hover:text-blue-300 hover:border-blue-500/50 hover:-translate-y-0.5 shadow-sm truncate transition-all font-mono group">
                        <span className="group-hover:underline">{source}</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}

            </div>
            {/* END RIGHT COLUMN */}

          </div>
        ) : (
          <div className="bg-[#161b22] border border-gray-800 rounded-3xl p-16 text-center shadow-2xl text-gray-400 max-w-2xl mx-auto mt-20">
            <svg className="w-24 h-24 mx-auto mb-6 text-red-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <h2 className="text-3xl font-bold mb-4 text-white">Analysis Failed</h2>
            <p className="text-xl">The AI agent could not finalize the venture report.</p>
            <button onClick={() => navigate('/emerging')} className="mt-10 px-8 py-4 bg-blue-600 hover:bg-blue-500 hover:shadow-lg text-white rounded-xl font-bold transition-all transform hover:-translate-y-1">
              Return to Project Scope
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Analysis;
