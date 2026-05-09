import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4 text-center">
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center opacity-20"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-6">
        <h1 className="text-6xl md:text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600 mb-6 drop-shadow-sm">
          Venture Alpha
        </h1>
        
        <p className="text-xl md:text-3xl text-gray-300 mb-10 font-light">
          Your Intelligent AI Venture Scout Agent
        </p>
        
        <p className="text-md md:text-lg text-gray-400 mb-12 max-w-2xl mx-auto">
          Uncover the next generation of emerging technologies and open-source projects powered by advanced AI analysis. Stay ahead of the curve.
        </p>

        <button
          onClick={() => navigate('/emerging')}
          className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white bg-gradient-to-r from-blue-600 to-purple-700 rounded-full overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
        >
          <span className="absolute w-0 h-0 transition-all duration-500 ease-out bg-white rounded-full group-hover:w-56 group-hover:h-56 opacity-10"></span>
          <span className="relative flex items-center gap-2">
            Discover Emerging Technologies
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
          </span>
        </button>
      </div>

      <div className="relative z-10 mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">
        {[
          { title: 'AI-Powered Analysis', desc: 'Deep dive into repositories using state-of-the-art LLMs.' },
          { title: 'Real-time Metrics', desc: 'Track stars, forks, and community momentum instantly.' },
          { title: 'Conviction Scoring', desc: 'Proprietary algorithms to rank project potential.' }
        ].map((feature, idx) => (
          <div key={idx} className="bg-white/5 backdrop-blur-lg border border-white/10 p-6 rounded-2xl text-left hover:bg-white/10 transition">
            <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
            <p className="text-gray-400">{feature.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
