# Layer 1: Requirements categories configuration
# You can ADD, REMOVE, or MODIFY categories here

LAYER1_CATEGORIES = {
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
}

def get_enabled_categories():
    """Returns only enabled categories"""
    return {k: v for k, v in LAYER1_CATEGORIES.items() if v["enabled"]}