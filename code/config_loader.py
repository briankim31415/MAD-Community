import json

_config = None

def load_config():
    global _config
    if _config is None:  # Load only once and cache it
        with open('config.json', 'r') as f:
            _config = json.load(f)
    return _config