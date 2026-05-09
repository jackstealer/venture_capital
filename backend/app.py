from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Database
from data_collector import DataCollector
from ai_analyzer import AIAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from trend_analyzer import TrendAnalyzer
from scoring_engine import ScoringEngine
from recommendation_engine import RecommendationEngine
from memo_generator import MemoGenerator
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize all components
db = Database()
collector = DataCollector()  
ai_analyzer = AIAnalyzer()  
sentiment_analyzer = SentimentAnalyzer()  
trend_analyzer = TrendAnalyzer()  
scoring_engine = ScoringEngine()  
recommendation_engine = RecommendationEngine()  
memo_generator = MemoGenerator() 

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "Venture Scout API - Gen AI Powered",
        "version": "1.0.0",
        "endpoints": {
            "trending": "/api/trending",
            "analyze": "/api/analyze",
            "full_analysis": "/api/full-analysis",
            "compare": "/api/compare",
            "projects": "/api/projects"
        }
    })

@app.route('/api/trending', methods=['GET'])
def get_trending():
    try:
        limit = request.args.get('limit', 10, type=int)
        
        print(f"📡 Fetching {limit} trending repositories...")
        trending_repos = collector.fetch_trending_repos(limit)
        
        # Store in database
        for repo in trending_repos:
            db.save_project(repo)
        
        return jsonify({
            "success": True,
            "count": len(trending_repos),
            "data": trending_repos
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    try:
        data = request.json
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({
                "success": False,
                "error": "repo_url is required"
            }), 400
        
        print(f"🔍 Analyzing: {repo_url}")
        
        # Fetch repository details
        repo_data = collector.fetch_repo_details(repo_url)
        
        # AI analysis
        analysis = ai_analyzer.analyze_repository(repo_data)
        
        # Save to database
        repo_data['ai_analysis'] = analysis
        db.save_project(repo_data)
        
        return jsonify({
            "success": True,
            "data": {
                "repo": repo_data,
                "analysis": analysis
            }
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/full-analysis', methods=['POST'])
def full_analysis():
    try:
        data = request.json
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({
                "success": False,
                "error": "repo_url is required"
            }), 400
        
        print(f"\n🚀 Starting FULL AI ANALYSIS for: {repo_url}\n")
        
        print("📊 Step 1: Fetching repository data...")
        repo_data = collector.fetch_repo_details(repo_url)
     
        print("🤖 Step 2: Running AI analysis...")
        ai_analysis = ai_analyzer.analyze_repository(repo_data)
        
        print("💭 Step 3: Analyzing sentiment...")
        sentiment = sentiment_analyzer.analyze_repository(repo_data)
        
        print("📈 Step 4: Detecting trends...")
        trends = trend_analyzer.analyze_trends(repo_data)
        
        print("🎯 Step 5: Calculating scores...")
        scoring = scoring_engine.calculate_score(repo_data, ai_analysis, trends, sentiment)
        
        print("💡 Step 6: Generating recommendation...")
        recommendation = recommendation_engine.generate_recommendation(
            repo_data, ai_analysis, trends, sentiment
        )
        
        print("📝 Step 7: Creating investment memo...")
        memo = memo_generator.generate_memo(repo_data, ai_analysis, scoring)
        
        complete_analysis = {
            "repo_info": {
                "name": repo_data.get('repo_name'),
                "url": repo_data.get('repo_url'),
                "description": repo_data.get('description'),
                "stars": repo_data.get('stars'),
                "forks": repo_data.get('forks'),
                "language": repo_data.get('primary_language')
            },
            "ai_analysis": ai_analysis,
            "sentiment_analysis": sentiment,
            "trend_analysis": trends,
            "scoring": scoring,
            "recommendation": recommendation,
            "investment_memo": memo
        }
        
        # Save complete analysis
        repo_data['complete_analysis'] = complete_analysis
        db.save_project(repo_data)
        
        print("✅ Analysis complete!\n")
        
        return jsonify({
            "success": True,
            "data": complete_analysis
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def compare_projects():
    try:
        data = request.json
        repo_url1 = data.get('repo_url1')
        repo_url2 = data.get('repo_url2')
        
        if not repo_url1 or not repo_url2:
            return jsonify({
                "success": False,
                "error": "Both repo_url1 and repo_url2 are required"
            }), 400
        
        print(f"⚖️  Comparing projects...")
        
        # Fetch both repositories
        repo1 = collector.fetch_repo_details(repo_url1)
        repo2 = collector.fetch_repo_details(repo_url2)
        
        # Analyze both
        analysis1 = ai_analyzer.analyze_repository(repo1)
        analysis2 = ai_analyzer.analyze_repository(repo2)
        
        # Score both
        score1 = scoring_engine.calculate_score(repo1, analysis1)
        score2 = scoring_engine.calculate_score(repo2, analysis2)
        
        # AI comparison
        ai_comparison = ai_analyzer.compare_projects(repo1, repo2)
        
        # Recommendation comparison
        rec1 = recommendation_engine.generate_recommendation(repo1, analysis1)
        rec2 = recommendation_engine.generate_recommendation(repo2, analysis2)
        
        comparison_result = recommendation_engine.compare_projects(rec1, rec2)
        
        return jsonify({
            "success": True,
            "data": {
                "project1": {
                    "name": repo1.get('repo_name'),
                    "score": score1,
                    "recommendation": rec1
                },
                "project2": {
                    "name": repo2.get('repo_name'),
                    "score": score2,
                    "recommendation": rec2
                },
                "ai_comparison": ai_comparison,
                "final_comparison": comparison_result
            }
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all analyzed projects from database"""
    try:
        projects = db.get_all_projects()
        return jsonify({
            "success": True,
            "count": len(projects),
            "data": projects
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/project/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get specific project details"""
    try:
        project = db.get_project(project_id)
        if project:
            return jsonify({
                "success": True,
                "data": project
            })
        else:
            return jsonify({
                "success": False,
                "error": "Project not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 VENTURE SCOUT - Gen AI Investment Analysis Platform")
    print("=" * 60)
    print("📊 Server running on http://localhost:5000")
    print("📖 API Documentation: http://localhost:5000/")
    print("=" * 60)
    print("\n✨ Gen AI Features Active:")
    print("  • LLM-powered repository analysis")
    print("  • NLP sentiment analysis")
    print("  • AI trend detection")
    print("  • Smart scoring engine")
    print("  • Automated investment memos")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000)
