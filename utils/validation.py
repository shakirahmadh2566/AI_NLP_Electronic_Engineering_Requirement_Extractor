import json
import re

def safe_json(text: str):

    if not text:
        return None

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None

    raw = match.group()

    try:
        return json.loads(raw)

    except json.JSONDecodeError:

        # repair attempts
        raw = raw.replace("'", '"')
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)

        try:
            return json.loads(raw)
        except:
            return None