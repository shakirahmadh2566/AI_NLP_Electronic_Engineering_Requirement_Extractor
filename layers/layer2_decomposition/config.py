# Layer 2: Decomposition categories - YOU CAN MODIFY THIS LIST
# Add, remove, or rename categories as needed

LAYER2_CATEGORIES = {
    "sensing": {"enabled": True, "description": "Sensors and input detection"},
    "processing": {"enabled": True, "description": "Data processing and computation"},
    "control": {"enabled": True, "description": "Control algorithms and logic"},
    "communication": {"enabled": True, "description": "Data transmission protocols"},
    "power": {"enabled": True, "description": "Power supply and management"},
    "actuation": {"enabled": True, "description": "Motors, actuators, outputs"},
    "data_storage": {"enabled": True, "description": "Memory and data logging"},
    "user_interface": {"enabled": True, "description": "User interaction methods"},
    "protection": {"enabled": True, "description": "Safety and protection circuits"}
}

def get_enabled_categories():
    """Returns only enabled decomposition categories"""
    return {k: v for k, v in LAYER2_CATEGORIES.items() if v["enabled"]}