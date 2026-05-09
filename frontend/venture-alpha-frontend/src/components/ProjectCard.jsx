function ProjectCard({ project, onAnalyze }) {
  // Format score to 2 decimal places if it's a number
  const score = typeof project.conviction_score === 'number' 
    ? project.conviction_score.toFixed(2) 
    : project.conviction_score;

  return (
    <div className="bg-[#161b22] border border-gray-800 rounded-2xl shadow-lg hover:shadow-cyan-900/20 hover:border-gray-600 transition-all duration-300 flex flex-col relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      
      <div className="p-6 flex-grow">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-100 leading-tight">
              {project.repo_name}
            </h3>
            <span className="inline-block mt-1 text-[10px] uppercase tracking-widest text-blue-400 font-bold bg-blue-500/10 px-2 py-0.5 rounded">
              {project.category || (project.source === 'producthunt' ? 'Product Launch' : 'Ecosystem Tool')}
            </span>
          </div>
          <div className="flex items-center gap-1 bg-gray-800/80 text-yellow-500 text-xs font-bold px-2.5 py-1 rounded-full border border-gray-700">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
            <span>{project.stars > 1000 ? (project.stars/1000).toFixed(1) + 'k' : project.stars}</span>
          </div>
        </div>
        
        <div className="mb-5 bg-gray-900/50 rounded-xl p-3 border border-gray-800">
          <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-1 block">Conviction Score</span>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600">
              {score}
            </span>
            <span className="text-xs text-gray-500 mb-1">/ 1.0</span>
          </div>
          {/* Progress bar visual for score */}
          <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-green-400 to-emerald-600 h-full rounded-full" 
              style={{ width: `${Math.min(100, (project.conviction_score || 0) * 100)}%` }}
            ></div>
          </div>
        </div>

        <p className="text-gray-400 text-sm line-clamp-3 leading-relaxed mb-5">
          {project.description}
        </p>

        <div className="space-y-2 mt-auto">
          <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold">Signals</span>
          <div className="flex flex-wrap gap-2">
            {(project.source === 'github' || project.star_velocity > 0 || project.signal_breakdown?.github_velocity) ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#161b22] border border-gray-700 text-[11px] font-medium text-gray-300">
                🧑‍💻 Developer Activity
              </span>
            ) : null}
            
            {project.trend_strength && project.trend_strength !== "" && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#161b22] border border-gray-700 text-[11px] font-medium text-gray-300">
                📈 Trends: {project.trend_strength}
              </span>
            )}

            {project.source === 'producthunt' && (
               <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#da552f]/10 border border-[#da552f]/30 text-[11px] font-medium text-[#da552f]">
                 🚀 Product Hunt {project.extra?.votes ? `(${project.extra.votes})` : 'Trending'}
               </span>
            )}

            {(project.news_mentions > 0 || project.extra?.news_mentions > 0) && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#161b22] border border-gray-700 text-[11px] font-medium text-gray-300">
                📰 {project.news_mentions || project.extra?.news_mentions} News Mentions
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="p-6 pt-4 mt-auto">
        <button
          onClick={onAnalyze}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-4 rounded-lg transition-colors duration-200 flex justify-center items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.2)]"
        >
          <svg className="w-5 h-5 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Generate Memo
        </button>
      </div>
    </div>
  );
}

export default ProjectCard;
