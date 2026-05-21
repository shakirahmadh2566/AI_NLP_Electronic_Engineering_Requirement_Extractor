# Keep as is or modify for custom prompts
from layers.layer1_requirements.config import get_enabled_categories

def get_dynamic_prompt():
    """Generate prompt based on enabled categories"""
    enabled = get_enabled_categories()
    categories_list = "\n".join([f"- {k.replace('_', ' ').title()}" for k in enabled.keys()])
    return f"""
Extract the following categories from engineering requirements:
{categories_list}

Return as JSON with these exact keys.
"""