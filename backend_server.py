from flask import Flask, request, jsonify
from flask_cors import CORS
from app.orchestrator import run_pipeline
import json

app = Flask(__name__)
CORS(app)  # Allow HTML file to connect

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle analysis requests from HTML frontend"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Run the pipeline
        result = run_pipeline(prompt)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    print("="*50)
    print("🚀 Backend Server Starting...")
    print("📡 Running on: http://localhost:8502")
    print("🌐 Open engineering_assistant.html in your browser")
    print("="*50)
    app.run(host='localhost', port=8502, debug=False)