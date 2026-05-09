import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectCard from '../components/ProjectCard';

function EmergingTech() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (loading) {
      const timer = setInterval(() => {
        setLoadingStep(prev => (prev < 3 ? prev + 1 : prev));
      }, 800);
      return () => clearInterval(timer);
    }
  }, [loading]);

  useEffect(() => {
    fetch('/api/emerging_projects')
      .then(res => {
        if (!res.ok) {
          throw new Error(`Server returned status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        if (data && data.projects) {
          setProjects(data.projects);
        } else {
          setProjects([]);
          console.error("Format mismatch: Backend did not return a 'projects' array.");
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching projects:', err);
        setError(err.message);
        setProjects([]);
        setLoading(false);
      });
  }, []);

  const handleAnalyze = (project) => {
    navigate('/analysis', { state: { project } });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#07090b] flex flex-col items-center justify-center text-gray-300 font-mono relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-900/5 via-[#07090b] to-[#07090b]"></div>
        <div className="bg-[#0a0c10] border border-gray-800 p-8 rounded-2xl shadow-[0_0_40px_-5px_rgba(99,102,241,0.15)] w-full max-w-lg z-10 relative">
          <div className="flex items-center justify-between mb-8 border-b border-gray-800 pb-4">
            <h3 className="text-xl font-bold text-gray-100 flex items-center gap-3 tracking-widest uppercase text-sm">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
              </span>
              Venture Scout Matrix
            </h3>
            <span className="text-[10px] text-gray-600 text-right leading-tight">BOOT SEQUENCE<br/>v3.1.0</span>
          </div>
          
          <div className="space-y-5 text-[14px]">
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 1 ? <span className="text-green-500">✓</span> : <span className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin inline-block"></span>}</div>
              <span className={loadingStep === 0 ? "text-indigo-300 font-medium" : "text-gray-600"}>[Data Collectors] Activating GitHub, ProductHunt & NewsAPI nodes...</span>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 2 ? <span className="text-green-500">✓</span> : (loadingStep === 1 ? <span className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin inline-block"></span> : <span className="w-4"></span>)}</div>
              <span className={loadingStep === 1 ? "text-indigo-300 font-medium" : (loadingStep > 1 ? "text-gray-600" : "text-gray-800")}>[Signal Processing] Aggregating velocities & market demand...</span>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-0.5">{loadingStep >= 3 ? <span className="text-green-500">✓</span> : (loadingStep === 2 ? <span className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin inline-block"></span> : <span className="w-4"></span>)}</div>
              <span className={loadingStep === 2 ? "text-indigo-300 font-medium" : (loadingStep > 2 ? "text-gray-600" : "text-gray-800")}>[Quant Engine] Finalizing conviction scores and ranking...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f1115] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12 border-b border-gray-800 pb-6 flex flex-col md:flex-row justify-between items-end gap-4">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 mb-2">
              Emerging Technologies
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl">
              High-signal projects surfaced by our AI agent, ranked by proprietary conviction score.
            </p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="text-sm font-semibold text-gray-400 hover:text-white transition group flex items-center gap-1"
          >
            ← Back to Dashboard
          </button>
        </div>
        
        {error ? (
          <div className="col-span-3 flex flex-col items-center justify-center py-24 text-center">
            <div className="text-red-500 text-5xl mb-6">⚠</div>
            <h2 className="text-2xl font-bold text-white mb-2">Could not connect to backend</h2>
            <p className="text-gray-400 mb-1 max-w-md">Make sure the LLM server is running at <code className="text-blue-400">http://localhost:8000</code></p>
            <p className="text-gray-600 text-sm font-mono mt-2">{error}</p>
            <p className="text-gray-500 text-sm mt-4">Tip: Run <code className="text-green-400">python -m uvicorn app:app --reload --port 8000</code> in the <code className="text-green-400">LLM/</code> directory first. Then call <code className="text-green-400">POST /seed_data</code> to populate projects.</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="col-span-3 flex flex-col items-center justify-center py-24 text-center">
            <div className="text-gray-600 text-5xl mb-6">📭</div>
            <h2 className="text-2xl font-bold text-white mb-2">No Projects Found</h2>
            <p className="text-gray-400 max-w-md">The database has no scouted projects yet. Call <code className="text-green-400">POST /api/seed_data</code> to seed demo projects into MongoDB.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map((project, index) => (
              <ProjectCard
                key={index}
                project={project}
                onAnalyze={() => handleAnalyze(project)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default EmergingTech;
