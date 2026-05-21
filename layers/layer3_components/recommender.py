import json
import re
import requests
from layers.layer3_components.config import get_enabled_categories, get_mapping

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "phi3:mini"

# ============================================================
# PRE-DEFINED ESP32 COMPONENT DATABASE (Guaranteed results)
# ============================================================
ESP32_COMPONENTS = {
    "sensors_inputs": [
        {
            "name": "Capacitive Soil Moisture Sensor v2.0",
            "pros": ["Corrosion resistant", "Analog output", "Low cost ($8-10)", "Long lifespan"],
            "cons": ["Requires calibration", "Not as accurate as professional sensors"],
            "evidence_source": "Adafruit/SparkFun datasheets",
            "use_case": "Long-term outdoor soil monitoring"
        },
        {
            "name": "Resistive Soil Moisture Sensor",
            "pros": ["Very cheap ($2-3)", "Simple interface", "Widely available"],
            "cons": ["Prone to corrosion", "Less accurate", "Short lifespan outdoor"],
            "evidence_source": "Common DIY sensor",
            "use_case": "Short-term or indoor monitoring"
        },
        {
            "name": "YL-69 + ADC0831",
            "pros": ["Digital output", "Adjustable threshold", "Low power"],
            "cons": ["External ADC needed", "More complex wiring"],
            "evidence_source": "ESP32 community projects",
            "use_case": "When analog pins are limited"
        },
        {
            "name": "Professional Soil Moisture (TEROS 12)",
            "pros": ["Highly accurate", "Temperature compensated", "Long lifespan"],
            "cons": ["Expensive ($150+)", "Overkill for simple monitoring"],
            "evidence_source": "METER Group datasheets",
            "use_case": "Commercial agriculture research"
        }
    ],
    "processor": [
        {
            "name": "ESP32-S3-WROOM-1",
            "pros": ["Built-in WiFi/BT", "Low deep sleep (5uA)", "USB native", "$5-7"],
            "cons": ["Limited RAM (512KB)", "No built-in SD card"],
            "evidence_source": "Espressif datasheet",
            "use_case": "Battery-powered WiFi IoT"
        },
        {
            "name": "ESP32-C3-DevKitM-1",
            "pros": ["RISC-V architecture", "Ultra-low power (3uA sleep)", "Small form factor", "$4-5"],
            "cons": ["Less GPIO pins", "No Bluetooth classic"],
            "evidence_source": "Espressif documentation",
            "use_case": "Minimalist battery applications"
        },
        {
            "name": "ESP32-WROVER-E",
            "pros": ["8MB PSRAM", "More memory for data logging", "Dual-core"],
            "cons": ["Higher sleep current (15uA)", "More expensive ($8-10)"],
            "evidence_source": "Espressif comparison",
            "use_case": "Data-intensive applications"
        }
    ],
    "controller": [
        {
            "name": "ESP32-S3 Built-in Control",
            "pros": ["Integrated into main processor", "No extra cost", "Low power"],
            "cons": ["Uses main CPU cycles", "Limited to ESP32 capabilities"],
            "evidence_source": "Espressif architecture",
            "use_case": "Simple control logic (sampling, thresholds)"
        },
        {
            "name": "PID Control Library (ESP32)",
            "pros": ["Software implementation", "Tunable parameters", "No hardware cost"],
            "cons": ["CPU overhead", "Requires tuning"],
            "evidence_source": "Arduino PID library",
            "use_case": "Precise control loops"
        },
        {
            "name": "External Microcontroller (ATtiny85)",
            "pros": ["Dedicated control", "Ultra-low power", "Offloads main CPU"],
            "cons": ["Extra cost ($2-3)", "More complex programming", "Additional PCB space"],
            "evidence_source": "ATtiny datasheet",
            "use_case": "Critical timing or safety systems"
        }
    ],
    "communication_modules": [
        {
            "name": "ESP32 Built-in WiFi with MQTT",
            "pros": ["No extra hardware", "Standard protocol", "Reliable"],
            "cons": ["Higher power consumption", "Needs WiFi network"],
            "evidence_source": "ESP32 WiFi documentation",
            "use_case": "Greenhouse with WiFi access"
        },
        {
            "name": "ESP-NOW Protocol",
            "pros": ["Very low power", "No router needed", "Fast pairing"],
            "cons": ["Short range (200m)", "Limited to ESP devices"],
            "evidence_source": "Espressif ESP-NOW guide",
            "use_case": "Multi-node sensor network"
        },
        {
            "name": "LoRa Module (SX1276)",
            "pros": ["Long range (2-5km)", "Low power", "Penetrates walls"],
            "cons": ["Extra cost ($15-20)", "Lower data rate", "Needs external module"],
            "evidence_source": "Semtech datasheet",
            "use_case": "Remote areas without WiFi"
        }
    ],
    "power_system": [
        {
            "name": "18650 Li-ion (3000mAh) + TP4056",
            "pros": ["High capacity", "Rechargeable", "Cheap ($8 total)"],
            "cons": ["Needs protection circuit", "Heavy"],
            "evidence_source": "Battery University",
            "use_case": "1-2 month battery life"
        },
        {
            "name": "2x AA Alkaline + Boost Converter",
            "pros": ["Readily available", "No charging circuit", "Safe"],
            "cons": ["Non-rechargeable", "Lower capacity", "Less voltage stable"],
            "evidence_source": "Battery comparison",
            "use_case": "Short-term deployment (2-3 weeks)"
        },
        {
            "name": "Solar + 18650 + TP4056 + BQ25504",
            "pros": ["Infinite runtime", "Green energy", "Set and forget"],
            "cons": ["Complex", "Higher cost ($25-30)", "Needs sunlight"],
            "evidence_source": "Solar harvesting designs",
            "use_case": "Outdoor no grid power"
        }
    ],
    "actuators": [
        {
            "name": "5V Mini Water Pump (2-3W)",
            "pros": ["Cheap ($3-5)", "Simple on/off control", "Good flow rate"],
            "cons": ["Noisy", "Not precise", "Vibrates"],
            "evidence_source": "DIY irrigation projects",
            "use_case": "Simple on/off watering"
        },
        {
            "name": "Servo Motor + Ball Valve",
            "pros": ["Precise control", "Low power once open", "Professional"],
            "cons": ["More complex plumbing", "Slower operation"],
            "evidence_source": "Irrigation system design",
            "use_case": "Drip irrigation control"
        },
        {
            "name": "MOSFET Switch + Solenoid Valve",
            "pros": ["Fast switching", "Low power holding", "Industrial grade"],
            "cons": ["Requires flyback diode", "Can be noisy"],
            "evidence_source": "Power electronics design",
            "use_case": "High-flow irrigation systems"
        }
    ],
    "data_storage": [
        {
            "name": "SPIFFS (ESP32 Flash)",
            "pros": ["No extra hardware", "1-2MB available", "Simple API"],
            "cons": ["Limited space", "Wear leveling limited"],
            "evidence_source": "ESP32 SPIFFS docs",
            "use_case": "Configuration plus last 100 readings"
        },
        {
            "name": "MicroSD Card Module",
            "pros": ["Large storage (GB)", "Easy data transfer", "CSV logging"],
            "cons": ["Extra power", "Uses SPI pins", "Slower"],
            "evidence_source": "SD card tutorials",
            "use_case": "Long-term data logging"
        },
        {
            "name": "External EEPROM (AT24C256)",
            "pros": ["Low power", "Simple I2C interface", "32KB storage"],
            "cons": ["Limited capacity", "Slower write cycles"],
            "evidence_source": "Microchip datasheet",
            "use_case": "Critical configuration data"
        }
    ],
    "user_interface": [
        {
            "name": "RGB LED with Button",
            "pros": ["Cheap ($1)", "Low power", "Simple feedback"],
            "cons": ["No data display", "Limited information"],
            "evidence_source": "Status indicator designs",
            "use_case": "Basic status alerts"
        },
        {
            "name": "0.96 Inch OLED (SSD1306)",
            "pros": ["Shows actual readings", "I2C interface", "Low power", "$3-4"],
            "cons": ["Small screen", "Limited resolution"],
            "evidence_source": "OLED with ESP32 tutorials",
            "use_case": "On-site data viewing"
        },
        {
            "name": "2.4 Inch TFT Display (ILI9341)",
            "pros": ["Color display", "Touch option", "Good resolution"],
            "cons": ["Higher power", "More complex wiring", "$10-15"],
            "evidence_source": "Display driver documentation",
            "use_case": "Rich user interface with graphs"
        }
    ],
    "protection_safety_circuits": [
        {
            "name": "IP65 or IP67 Enclosure",
            "pros": ["Weatherproof", "Affordable ($10-15)", "Easy to modify"],
            "cons": ["Can trap heat", "Bulky"],
            "evidence_source": "NEMA ratings guide",
            "use_case": "Outdoor greenhouse installation"
        },
        {
            "name": "Polyfuse (PTC) plus TVS Diode",
            "pros": ["Resettable overcurrent", "ESD protection", "Cheap ($1)"],
            "cons": ["Slow trip time", "Adds complexity"],
            "evidence_source": "Circuit protection guide",
            "use_case": "Pump and battery protection"
        },
        {
            "name": "Reverse Polarity Protection (MOSFET)",
            "pros": ["Low voltage drop", "Efficient", "Auto-reset"],
            "cons": ["Requires correct MOSFET selection", "Adds cost ($0.50-1)"],
            "evidence_source": "Power protection circuits",
            "use_case": "Battery-powered devices"
        }
    ]
}

def web_search(query, max_results=3):
    """Search the web for component information using DuckDuckGo"""
    results = []
    try:
        # Try new package first
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", "")[:300],
                        "link": r.get("href", "")
                    })
                    print(f"[WEB] Found: {r.get('title', '')[:50]}...")
        except ImportError:
            # Fallback to old package
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=max_results):
                        results.append({
                            "title": r.get("title", ""),
                            "snippet": r.get("body", "")[:300],
                            "link": r.get("href", "")
                        })
                        print(f"[WEB] Found: {r.get('title', '')[:50]}...")
            except ImportError:
                print("[WEB] DuckDuckGo package not installed. Install: pip install ddgs")
    except Exception as e:
        print(f"[WEB] Search error: {e}")
    
    return results

def generate_ollama(prompt, model_name=None):
    """Direct HTTP call to Ollama with model selection"""
    model = model_name or DEFAULT_MODEL
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2048,
                    "num_ctx": 2048
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"[ERROR: {response.status_code}]"
    except Exception as e:
        return f"[ERROR: {str(e)}]"

def search_and_generate_components(category, requirements_text, model_name=None):
    """Search web and generate component recommendations with sources"""
    
    print(f"[INFO] Searching web for: {category} components...")
    
    # Perform web search
    search_queries = [
        f"best {category} for ESP32 IoT 2025",
        f"{category} comparison pros cons",
        f"ESP32 {category} recommendation"
    ]
    
    all_web_results = []
    for query in search_queries[:2]:  # Limit to 2 searches
        results = web_search(query, max_results=2)
        all_web_results.extend(results)
    
    # Build prompt with web search results
    web_context = ""
    if all_web_results:
        web_context = "\n\nWeb Search Results (use as reference):\n"
        for i, result in enumerate(all_web_results[:5], 1):
            web_context += f"{i}. {result['title']}\n   {result['snippet']}\n   Source: {result['link']}\n\n"
        print(f"[INFO] Found {len(all_web_results)} web results for {category}")
    else:
        print(f"[INFO] No web results for {category}, using LLM knowledge only")
    
    prompt = f"""You are an embedded systems hardware engineer. Recommend specific components for: {category}

Requirements: {requirements_text}

{web_context}

Generate 3-4 specific component options with REAL part numbers when possible.

Return ONLY valid JSON array. NO other text.

Format:
[
  {{
    "name": "Component name with model number",
    "pros": ["advantage1", "advantage2", "advantage3"],
    "cons": ["disadvantage1", "disadvantage2"],
    "evidence_source": "Source: [web result title] or [LLM knowledge]",
    "use_case": "Specific application scenario"
  }}
]

Now generate recommendations for {category}:"""

    response_text = generate_ollama(prompt, model_name)
    
    try:
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            components = json.loads(json_match.group())
            print(f"[INFO] Generated {len(components)} components for {category}")
            return components
        else:
            print(f"[WARNING] No JSON found for {category}")
            return []
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON for {category}: {e}")
        return []

def recommend_components(layer2: dict, model_name: str = None):
    """Recommend components using web search + pre-defined database + LLM"""
    
    category_mapping = get_mapping()
    final_result = {}
    
    print(f"\n[INFO] Starting component recommendations")
    print(f"[INFO] Model: {model_name or DEFAULT_MODEL}")
    print(f"[INFO] Web search: ENABLED")
    print(f"[INFO] Pre-defined database: LOADED ({len(ESP32_COMPONENTS)} categories)\n")
    
    for l2_category, l3_category in category_mapping.items():
        print(f"\n{'='*50}")
        print(f"Processing: {l3_category}")
        print(f"{'='*50}")
        
        # Get requirements for this category
        requirements_list = layer2.get(l2_category, [])
        if requirements_list:
            requirements_text = "\n".join(requirements_list[:3])
        else:
            requirements_text = f"Standard {l3_category} for ESP32 IoT system"
        
        # Try web search + LLM generation first
        web_components = search_and_generate_components(l3_category, requirements_text, model_name)
        
        if web_components and len(web_components) >= 2:
            # Use web search results
            final_result[l3_category] = web_components
            print(f"[INFO] Using web search results for {l3_category}")
        elif l3_category in ESP32_COMPONENTS:
            # Fallback to pre-defined database
            final_result[l3_category] = ESP32_COMPONENTS[l3_category]
            print(f"[INFO] Using pre-defined database for {l3_category}")
        else:
            # Ultimate fallback
            final_result[l3_category] = [{
                "name": f"Standard {l3_category.replace('_', ' ')} for ESP32",
                "pros": ["Compatible with ESP32 ecosystem", "Available from multiple vendors", "Good community support"],
                "cons": ["Verify specific requirements", "Check power compatibility"],
                "evidence_source": "ESP32 community knowledge base",
                "use_case": requirements_text[:100]
            }]
            print(f"[WARNING] Using generic fallback for {l3_category}")
    
    print(f"\n[INFO] Component recommendations complete for {len(final_result)} categories")
    return final_result