# Layer 3: Component categories - FULLY CUSTOMIZABLE
# Map Layer2 categories to Layer3 component categories

LAYER2_TO_LAYER3_MAPPING = {
    "sensing": "sensors_inputs",
    "processing": "processor",
    "control": "controller",
    "communication": "communication_modules",
    "power": "power_system",
    "actuation": "actuators",
    "data_storage": "data_storage",
    "user_interface": "user_interface",
    "protection": "protection_safety_circuits"
}

# Layer 3 component categories with descriptions
LAYER3_CATEGORIES = {
    "sensors_inputs": {
        "enabled": True,
        "description": "Temperature, humidity, motion, etc."
    },
    "processor": {
        "enabled": True,
        "description": "MCU, CPU, FPGA"
    },
    "controller": {
        "enabled": True,
        "description": "PID, logic controllers"
    },
    "communication_modules": {
        "enabled": True,
        "description": "WiFi, Bluetooth, LoRa, Zigbee"
    },
    "power_system": {
        "enabled": True,
        "description": "Batteries, regulators, chargers"
    },
    "actuators": {
        "enabled": True,
        "description": "Motors, servos, relays"
    },
    "data_storage": {
        "enabled": True,
        "description": "SD card, EEPROM, Flash"
    },
    "user_interface": {
        "enabled": True,
        "description": "Display, buttons, LEDs"
    },
    "protection_safety_circuits": {
        "enabled": True,
        "description": "Fuses, surge protection, isolation"
    }
}

def get_enabled_categories():
    """Returns enabled Layer3 categories"""
    return {k: v for k, v in LAYER3_CATEGORIES.items() if v["enabled"]}

def get_mapping():
    """Returns mapping from Layer2 to Layer3 for enabled categories"""
    mapping = {}
    for l2, l3 in LAYER2_TO_LAYER3_MAPPING.items():
        if l3 in get_enabled_categories():
            mapping[l2] = l3
    return mapping