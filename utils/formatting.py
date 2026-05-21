import pandas as pd

def safe_dataframe(data):

    if not data:
        return pd.DataFrame([{"info": "No data available"}])

    cleaned = []

    for item in data:

        if isinstance(item, dict):
            cleaned.append(item)

        elif isinstance(item, list):
            cleaned.append({
                "value": ", ".join(map(str, item))
            })

        else:
            cleaned.append({
                "value": str(item)
            })

    return pd.DataFrame(cleaned)