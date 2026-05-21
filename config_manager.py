import json
import os
import subprocess
import sys

CONFIG_FILE = "dynamic_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "layer1": {
        "functional_requirements": {
            "enabled": True,
            "description": "What the system must do",
            "prompt_hint": "List functional requirements"
        },
        "constraints": {
            "enabled": True,
            "description": "Budget, timeline, technical limits",
            "prompt_hint": "List constraints"
        },
        "performance_targets": {
            "enabled": True,
            "description": "Speed, accuracy, efficiency metrics",
            "prompt_hint": "List performance targets"
        },
        "environmental_conditions": {
            "enabled": True,
            "description": "Temperature, humidity, outdoor/indoor",
            "prompt_hint": "List environmental conditions"
        },
        "protections_safety": {
            "enabled": True,
            "description": "Safety requirements, protection circuits",
            "prompt_hint": "List protection and safety requirements"
        },
        "success_goal": {
            "enabled": True,
            "description": "Main objective and success criteria",
            "prompt_hint": "Define success goal"
        }
    },
    "layer2": {
        "sensing": {
            "enabled": True,
            "description": "Sensors and input detection",
            "example": "Soil moisture sensor, temperature sensor"
        },
        "processing": {
            "enabled": True,
            "description": "Data processing and computation",
            "example": "ESP32 MCU, ADC conversion"
        },
        "control": {
            "enabled": True,
            "description": "Control algorithms and logic",
            "example": "Sampling schedule, threshold detection"
        },
        "communication": {
            "enabled": True,
            "description": "Data transmission protocols",
            "example": "WiFi, MQTT, HTTP"
        },
        "power": {
            "enabled": True,
            "description": "Power supply and management",
            "example": "Battery, charger, regulator"
        },
        "actuation": {
            "enabled": True,
            "description": "Motors, actuators, outputs",
            "example": "Water pump, LED, buzzer"
        },
        "data_storage": {
            "enabled": True,
            "description": "Memory and data logging",
            "example": "SPIFFS, SD card, EEPROM"
        },
        "user_interface": {
            "enabled": True,
            "description": "User interaction methods",
            "example": "OLED display, buttons, LEDs"
        },
        "protection": {
            "enabled": True,
            "description": "Safety and protection circuits",
            "example": "Enclosure, fuses, TVS diode"
        }
    },
    "layer3_mapping": {
        "sensing": "sensors_inputs",
        "processing": "processor",
        "control": "controller",
        "communication": "communication_modules",
        "power": "power_system",
        "actuation": "actuators",
        "data_storage": "data_storage",
        "user_interface": "user_interface",
        "protection": "protection_safety_circuits"
    },
    "layer3": {
        "sensors_inputs": {
            "enabled": True,
            "description": "Temperature, humidity, motion, soil moisture sensors"
        },
        "processor": {
            "enabled": True,
            "description": "MCU, CPU, FPGA - ESP32 series"
        },
        "controller": {
            "enabled": True,
            "description": "PID, logic controllers, control algorithms"
        },
        "communication_modules": {
            "enabled": True,
            "description": "WiFi, Bluetooth, LoRa, Zigbee modules"
        },
        "power_system": {
            "enabled": True,
            "description": "Batteries, regulators, chargers, solar"
        },
        "actuators": {
            "enabled": True,
            "description": "Motors, servos, relays, pumps"
        },
        "data_storage": {
            "enabled": True,
            "description": "SD card, EEPROM, Flash, cloud"
        },
        "user_interface": {
            "enabled": True,
            "description": "Display, buttons, LEDs, touch"
        },
        "protection_safety_circuits": {
            "enabled": True,
            "description": "Fuses, surge protection, isolation, enclosures"
        }
    }
}

def load_config():
    """Load dynamic configuration with error handling"""
    
    # If config file doesn't exist, create default
    if not os.path.exists(CONFIG_FILE):
        print(f"[INFO] Config file not found. Creating default: {CONFIG_FILE}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    # Try to read existing file
    try:
        with open(CONFIG_FILE, 'r') as f:
            content = f.read().strip()
            
            # Check if file is empty
            if not content:
                print("[WARNING] Config file is empty. Using default configuration.")
                save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG
            
            # Try to parse JSON
            config = json.loads(content)
            print("[INFO] Config loaded successfully")
            return config
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {e}")
        print(f"[ERROR] Corrupted config file. Backing up and creating new one.")
        
        # Backup corrupted file
        if os.path.exists(CONFIG_FILE):
            backup_file = f"{CONFIG_FILE}.backup"
            os.rename(CONFIG_FILE, backup_file)
            print(f"[INFO] Backed up corrupted config to: {backup_file}")
        
        # Create fresh config
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """Save dynamic configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"[INFO] Config saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")

def add_layer1_category(name, description, prompt_hint):
    """Add a new Layer 1 category dynamically"""
    config = load_config()
    config["layer1"][name] = {
        "enabled": True,
        "description": description,
        "prompt_hint": prompt_hint
    }
    save_config(config)
    regenerate_config_files()
    return True

def add_layer2_category(name, description, example):
    """Add a new Layer 2 category dynamically (auto-creates Layer 3 mapping)"""
    config = load_config()
    config["layer2"][name] = {
        "enabled": True,
        "description": description,
        "example": example
    }
    # Also add to layer3 mapping
    layer3_name = name.replace("_", "_components")
    config["layer3_mapping"][name] = layer3_name
    config["layer3"][layer3_name] = {
        "enabled": True,
        "description": f"{description} components"
    }
    save_config(config)
    regenerate_config_files()
    return True

def add_layer3_category(name, description):
    """Add a new standalone Layer 3 category dynamically (not linked to Layer 2)"""
    config = load_config()
    config["layer3"][name] = {
        "enabled": True,
        "description": description
    }
    save_config(config)
    regenerate_config_files()
    return True

def remove_category(layer, category_name):
    """Remove (disable) a category dynamically"""
    config = load_config()
    if layer == "layer1" and category_name in config["layer1"]:
        config["layer1"][category_name]["enabled"] = False
    elif layer == "layer2" and category_name in config["layer2"]:
        config["layer2"][category_name]["enabled"] = False
    elif layer == "layer3" and category_name in config["layer3"]:
        config["layer3"][category_name]["enabled"] = False
    save_config(config)
    regenerate_config_files()
    return True

def enable_category(layer, category_name, enabled=True):
    """Enable or disable a category"""
    config = load_config()
    if layer == "layer1" and category_name in config["layer1"]:
        config["layer1"][category_name]["enabled"] = enabled
    elif layer == "layer2" and category_name in config["layer2"]:
        config["layer2"][category_name]["enabled"] = enabled
    elif layer == "layer3" and category_name in config["layer3"]:
        config["layer3"][category_name]["enabled"] = enabled
    save_config(config)
    regenerate_config_files()
    return True

def regenerate_config_files():
    """Regenerate all config files from dynamic config"""
    config = load_config()
    
    # Create directories if they don't exist
    os.makedirs("layers/layer1_requirements", exist_ok=True)
    os.makedirs("layers/layer2_decomposition", exist_ok=True)
    os.makedirs("layers/layer3_components", exist_ok=True)
    
    # Regenerate layer1 config
    with open("layers/layer1_requirements/config.py", "w") as f:
        f.write("""# AUTO-GENERATED - DO NOT EDIT MANUALLY
# Use config_manager_app.py to modify categories

LAYER1_CATEGORIES = {\n""")
        for key, value in config["layer1"].items():
            f.write(f'    "{key}": {{\n')
            f.write(f'        "enabled": {value["enabled"]},\n')
            f.write(f'        "description": "{value["description"]}",\n')
            f.write(f'        "prompt_hint": "{value.get("prompt_hint", "")}"\n')
            f.write(f'    }},\n')
        f.write("}\n\n")
        f.write("def get_enabled_categories():\n")
        f.write('    """Returns only enabled categories"""\n')
        f.write("    return {k: v for k, v in LAYER1_CATEGORIES.items() if v['enabled']}\n")
    
    # Regenerate layer2 config
    with open("layers/layer2_decomposition/config.py", "w") as f:
        f.write("""# AUTO-GENERATED - DO NOT EDIT MANUALLY
# Use config_manager_app.py to modify categories

LAYER2_CATEGORIES = {\n""")
        for key, value in config["layer2"].items():
            f.write(f'    "{key}": {{\n')
            f.write(f'        "enabled": {value["enabled"]},\n')
            f.write(f'        "description": "{value["description"]}",\n')
            f.write(f'        "example": "{value.get("example", "")}"\n')
            f.write(f'    }},\n')
        f.write("}\n\n")
        f.write("def get_enabled_categories():\n")
        f.write('    """Returns only enabled categories"""\n')
        f.write("    return {k: v for k, v in LAYER2_CATEGORIES.items() if v['enabled']}\n")
    
    # Regenerate layer3 config
    with open("layers/layer3_components/config.py", "w") as f:
        f.write("""# AUTO-GENERATED - DO NOT EDIT MANUALLY
# Use config_manager_app.py to modify categories

LAYER2_TO_LAYER3_MAPPING = {\n""")
        for k, v in config["layer3_mapping"].items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n\n")
        f.write("LAYER3_CATEGORIES = {\n")
        for key, value in config["layer3"].items():
            f.write(f'    "{key}": {{\n')
            f.write(f'        "enabled": {value["enabled"]},\n')
            f.write(f'        "description": "{value["description"]}"\n')
            f.write(f'    }},\n')
        f.write("}\n\n")
        f.write("def get_enabled_categories():\n")
        f.write('    """Returns enabled Layer3 categories"""\n')
        f.write("    return {k: v for k, v in LAYER3_CATEGORIES.items() if v['enabled']}\n\n")
        f.write("def get_mapping():\n")
        f.write('    """Returns mapping from Layer2 to Layer3 for enabled categories"""\n')
        f.write("    mapping = {}\n")
        f.write("    for l2, l3 in LAYER2_TO_LAYER3_MAPPING.items():\n")
        f.write("        if l3 in get_enabled_categories():\n")
        f.write("            mapping[l2] = l3\n")
        f.write("    return mapping\n")
    
    print("✅ All config files regenerated!")

def get_config_summary():
    """Get summary of current configuration"""
    config = load_config()
    summary = {
        "layer1": {
            "total": len(config["layer1"]),
            "enabled": sum(1 for v in config["layer1"].values() if v["enabled"]),
            "disabled": sum(1 for v in config["layer1"].values() if not v["enabled"])
        },
        "layer2": {
            "total": len(config["layer2"]),
            "enabled": sum(1 for v in config["layer2"].values() if v["enabled"]),
            "disabled": sum(1 for v in config["layer2"].values() if not v["enabled"])
        },
        "layer3": {
            "total": len(config["layer3"]),
            "enabled": sum(1 for v in config["layer3"].values() if v["enabled"]),
            "disabled": sum(1 for v in config["layer3"].values() if not v["enabled"])
        }
    }
    return summary

# Initialize on import
if __name__ == "__main__":
    # Delete corrupted file if it exists and is empty
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    os.remove(CONFIG_FILE)
                    print(f"[INFO] Removed empty config file: {CONFIG_FILE}")
        except:
            pass
    
    # Load or create config
    config = load_config()
    regenerate_config_files()
    
    # Print summary
    summary = get_config_summary()
    print("\n" + "="*50)
    print("✅ Config Manager Initialized!")
    print("="*50)
    print(f"Layer 1: {summary['layer1']['enabled']}/{summary['layer1']['total']} categories enabled")
    print(f"Layer 2: {summary['layer2']['enabled']}/{summary['layer2']['total']} categories enabled")
    print(f"Layer 3: {summary['layer3']['enabled']}/{summary['layer3']['total']} categories enabled")
    print("="*50)