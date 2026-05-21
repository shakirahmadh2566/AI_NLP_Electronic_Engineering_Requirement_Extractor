import requests
import json
import subprocess
import time

OLLAMA_URL = "http://localhost:11434"

# Available models from your system
AVAILABLE_MODELS = {
    "phi3:mini": {
        "name": "phi3:mini",
        "size": "2.2 GB",
        "description": "Good balance of speed and accuracy",
        "best_for": "Complex reasoning, component recommendations"
    },
    "deepseek-coder:1.3b": {
        "name": "deepseek-coder:1.3b",
        "size": "776 MB", 
        "description": "Fast, good for code and engineering",
        "best_for": "Technical decomposition, requirements"
    },
    "lfm2.5-thinking:latest": {
        "name": "lfm2.5-thinking:latest",
        "size": "731 MB",
        "description": "Lightweight, good for reasoning",
        "best_for": "Requirements extraction, quick tasks"
    },
    "qwen2.5:0.5b": {
        "name": "qwen2.5:0.5b",
        "size": "397 MB",
        "description": "Very fast, minimal memory usage",
        "best_for": "Fast processing, simple tasks"
    },
    "ALIENTELLIGENCE/electricalengineerv2:latest": {
        "name": "ALIENTELLIGENCE/electricalengineerv2:latest",
        "size": "4.7 GB",
        "description": "Specialized for electrical engineering",
        "best_for": "Hardware design, component selection"
    }
}

# Track current loaded model
_current_model = None

def unload_model(model_name):
    """Unload specific model from memory"""
    try:
        result = subprocess.run(['ollama', 'stop', model_name], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[INFO] ✓ Unloaded: {model_name}")
            return True
    except Exception as e:
        print(f"[DEBUG] Unload attempt: {e}")
    return False

def generate(prompt: str, model_name: str):
    """Generate using specific model with smart loading/unloading"""
    global _current_model
    
    # Check if we need to switch models
    if _current_model != model_name:
        # Different model - unload current if exists
        if _current_model is not None:
            print(f"[INFO] Switching models: {_current_model} → {model_name}")
            print(f"[INFO] Unloading {_current_model}...")
            unload_model(_current_model)
        else:
            print(f"[INFO] Loading model: {model_name}")
        
        _current_model = model_name
    else:
        # Same model - keep loaded
        print(f"[INFO] Reusing already loaded model: {model_name}")
    
    # Generate response
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 512,
                    "num_ctx": 1024
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure 'ollama serve' is running."
    except Exception as e:
        return f"Error: {str(e)}"

def get_available_models():
    """Get list of available models"""
    return AVAILABLE_MODELS

def get_current_model():
    """Get currently loaded model"""
    return _current_model

def reset_model():
    """Force reset/clear current model"""
    global _current_model
    if _current_model:
        unload_model(_current_model)
        _current_model = None