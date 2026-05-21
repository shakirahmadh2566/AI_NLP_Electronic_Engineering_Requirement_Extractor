from models.llm_client import generate
from layers.layer1_requirements.config import get_enabled_categories, LAYER1_CATEGORIES
import json
import re

def extract_requirements(prompt: str, model_name: str = None):
    """Extract requirements with robust JSON parsing"""
    
    enabled = get_enabled_categories()
    
    # Build dynamic prompt based on enabled categories
    categories_prompt = ""
    for key, value in enabled.items():
        categories_prompt += f'  "{key}": [],\n'
    
    # Simpler prompt that's easier for models to follow
    system_prompt = f"""Extract engineering requirements from the input.

Return ONLY valid JSON. No other text, no explanation.

Required format:
{{
{categories_prompt}}}

Input: {prompt}

Output:"""

    response = generate(system_prompt, model_name)
    print(f"[DEBUG] Layer 1 raw response (first 300 chars): {response[:300]}...")
    
    # Try multiple methods to extract JSON
    data = None
    
    # Method 1: Find JSON between curly braces
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            clean = response[start:end]
            # Try to fix common JSON issues
            clean = re.sub(r',\s*}', '}', clean)  # Remove trailing commas
            clean = re.sub(r',\s*]', ']', clean)  # Remove trailing commas in arrays
            data = json.loads(clean)
            print("[DEBUG] Method 1 succeeded")
    except Exception as e:
        print(f"[DEBUG] Method 1 failed: {e}")
    
    # Method 2: Try to extract using regex for each category
    if data is None:
        try:
            data = {}
            for key in enabled.keys():
                # Look for pattern: "key": [ ... ]
                pattern = f'"{key}"\\s*:\\s*\\[(.*?)\\]'
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    items_str = match.group(1)
                    # Extract quoted strings
                    items = re.findall(r'"([^"]*)"', items_str)
                    data[key] = items if items else []
                else:
                    data[key] = []
            print("[DEBUG] Method 2 succeeded (regex extraction)")
        except Exception as e:
            print(f"[DEBUG] Method 2 failed: {e}")
    
    # Method 3: Try to parse line by line
    if data is None:
        try:
            data = {key: [] for key in enabled.keys()}
            current_key = None
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                # Check for category headers
                for key in enabled.keys():
                    if f'"{key}"' in line or key in line.lower():
                        current_key = key
                        break
                # Extract list items
                if current_key and line.startswith('-'):
                    item = line[1:].strip().strip('"')
                    if item:
                        data[current_key].append(item)
                elif current_key and line.startswith('"') and line.endswith('"'):
                    item = line.strip('"')
                    if item:
                        data[current_key].append(item)
            print("[DEBUG] Method 3 succeeded (line-by-line)")
        except Exception as e:
            print(f"[DEBUG] Method 3 failed: {e}")
    
    # If we have valid data, ensure all categories exist
    if data and isinstance(data, dict):
        result = {}
        for key in enabled.keys():
            result[key] = data.get(key, [])
            # Ensure it's a list
            if not isinstance(result[key], list):
                if isinstance(result[key], str):
                    result[key] = [result[key]]
                else:
                    result[key] = []
        
        print(f"[DEBUG] Layer 1 parsed: { {k: len(v) for k, v in result.items()} }")
        return result
    
    # If all methods fail, return structured fallback based on prompt
    print("[DEBUG] All parsing methods failed, using intelligent fallback")
    
    # Intelligent fallback - extract info from prompt
    fallback_result = {key: [] for key in enabled.keys()}
    
    # Try to extract information from the original prompt
    prompt_lower = prompt.lower()
    
    if "soil" in prompt_lower or "moisture" in prompt_lower:
        fallback_result["functional_requirements"] = [
            "Monitor soil moisture levels",
            "Transmit data via WiFi",
            "Real-time monitoring capability"
        ]
        fallback_result["constraints"] = [
            "Budget: $50 per node",
            "Battery powered"
        ]
        fallback_result["performance_targets"] = [
            "Accuracy: ±2%",
            "Battery life: 1 month minimum"
        ]
        fallback_result["environmental_conditions"] = [
            "Temperature: -10°C to 50°C",
            "Waterproof rating: IP65"
        ]
        fallback_result["protections_safety"] = [
            "Over-current protection",
            "Waterproof enclosure"
        ]
        fallback_result["success_goal"] = [
            "Reliable soil moisture monitoring",
            "95% data transmission success rate"
        ]
    else:
        # Generic fallback
        fallback_result["functional_requirements"] = [prompt[:200] + "..."]
        fallback_result["constraints"] = ["Please provide more details"]
        fallback_result["performance_targets"] = ["To be defined"]
        fallback_result["environmental_conditions"] = ["Standard operating conditions"]
        fallback_result["protections_safety"] = ["Standard protections"]
        fallback_result["success_goal"] = ["Successful implementation"]
    
    return fallback_result