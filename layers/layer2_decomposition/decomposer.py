from models.llm_client import generate
from layers.layer2_decomposition.config import get_enabled_categories
import re

def decompose(requirements: dict, model_name: str = None):
    """Decompose into specific technical components with real examples"""
    
    enabled = get_enabled_categories()
    
    # Extract functional requirements - get the FULL context
    functional = (
        requirements.get("functional_requirements")
        or requirements.get("functional")
        or []
    )
    
    # Get all requirements for context
    all_req_text = []
    for key, value in requirements.items():
        if value and isinstance(value, (list, str)) and not key.endswith("_disabled"):
            if isinstance(value, list):
                all_req_text.extend([f"- {item}" for item in value if item])
            elif isinstance(value, str):
                all_req_text.append(f"- {value}")
    
    text = "\n".join(all_req_text[:20])  # Take up to 20 requirements
    
    if len(text) < 50:
        # If no good requirements, use the prompt directly
        text = str(requirements)
    
    # Create a VERY SPECIFIC prompt with examples
    prompt = f"""You are an embedded systems engineer designing an ESP32-based IoT system.

SYSTEM REQUIREMENTS:
{text}

TASK: Decompose this system into specific, REAL technical components.

For EACH category below, list ACTUAL components with specific names, NOT generic placeholders.

REQUIRED CATEGORIES:
- SENSING: What sensors? (e.g., "Capacitive soil moisture sensor", "DHT22 temp/humidity")
- PROCESSING: What processor? (e.g., "ESP32-S3", "ADC for analog readings")
- CONTROL: What control logic? (e.g., "Sampling every hour", "WiFi on/off scheduling")
- COMMUNICATION: What protocol? (e.g., "MQTT over WiFi", "HTTP POST to server")
- POWER: What power system? (e.g., "18650 battery + TP4056 charger", "Deep sleep mode")
- ACTUATION: What outputs? (e.g., "Water pump relay", "Status LED")
- DATA_STORAGE: What storage? (e.g., "SPIFFS for config", "SD card for data log")
- USER_INTERFACE: What UI? (e.g., "RGB status LED", "Configuration button")
- PROTECTION: What protection? (e.g., "IP65 enclosure", "Over-current fuse")

FORMAT (use bullet points - for each item):
SENSING:
- [Specific component name]
- [Another specific component]

PROCESSING:
- [Specific component name]
- [Another specific component]

(Continue for all categories)

IMPORTANT: 
- Be SPECIFIC with real component names
- Use part numbers when possible (e.g., "ESP32-S3-WROOM-1")
- DO NOT use generic phrases like "Standard components"
- Base on the requirements above

Now provide the decomposition:"""

    response = generate(prompt, model_name)
    print(f"[DEBUG] Layer 2 Response length: {len(response)} chars")
    print(f"[DEBUG] Response preview: {response[:500]}...")
    
    # Parse response
    result = {key: [] for key in enabled.keys()}
    current = None
    
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_upper = line.upper()
        
        # Map section headers to keys
        section_map = {
            'SENSING': 'sensing',
            'PROCESSING': 'processing',
            'CONTROL': 'control',
            'COMMUNICATION': 'communication',
            'POWER': 'power',
            'ACTUATION': 'actuation',
            'DATA_STORAGE': 'data_storage',
            'USER_INTERFACE': 'user_interface',
            'PROTECTION': 'protection'
        }
        
        for section, key in section_map.items():
            if section in line_upper:
                current = key
                # Extract any content after colon on same line
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content and content != '...' and not content.startswith('-'):
                        # Don't add generic phrases
                        if not any(word in content.lower() for word in ['standard', 'generic', 'typical']):
                            result[current].append(content)
                break
        
        # Extract bullet points
        if line.startswith('-') and current and current in result:
            item = line[1:].strip()
            # Filter out generic responses
            if item and len(item) > 5 and item != '...':
                generic_phrases = ['standard', 'generic', 'typical', 'basic', 'common', 'appropriate']
                if not any(phrase in item.lower() for phrase in generic_phrases):
                    result[current].append(item)
                elif len(result[current]) == 0:
                    # Only add generic if nothing else exists
                    result[current].append(item)
    
    # If any category is still empty, add specific fallbacks based on context
    soil_context = 'soil' in text.lower() or 'moisture' in text.lower()
    esp_context = 'esp32' in text.lower()
    
    for key in enabled.keys():
        if not result[key]:
            if key == 'sensing' and soil_context:
                result[key] = ['Capacitive soil moisture sensor (v2.0)', 'DHT22 temperature/humidity sensor']
            elif key == 'processing' and esp_context:
                result[key] = ['ESP32-S3-WROOM-1 module', 'ADC (Analog to Digital Converter)']
            elif key == 'communication':
                result[key] = ['WiFi 802.11 b/g/n (ESP32 built-in)', 'MQTT protocol for data transmission']
            elif key == 'power':
                result[key] = ['18650 Li-ion battery (3000mAh)', 'TP4056 charging module', 'Deep sleep power management']
            elif key == 'control':
                result[key] = ['Hourly sampling schedule', 'WiFi transmission on/off control', 'Battery voltage monitoring']
            elif key == 'actuation':
                result[key] = ['5V water pump (if irrigation needed)', 'RGB status LED']
            elif key == 'data_storage':
                result[key] = ['SPIFFS for configuration', 'MicroSD card module for data logging']
            elif key == 'user_interface':
                result[key] = ['RGB status LED', 'Push button for manual reading']
            elif key == 'protection':
                result[key] = ['IP65 waterproof enclosure', 'Polyfuse over-current protection']
            else:
                result[key] = [f"Specific {key} components based on requirements"]
    
    print(f"[DEBUG] Decomposition complete: { {k: len(v) for k, v in result.items()} }")
    return result