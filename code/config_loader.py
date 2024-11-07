import json

_config = None

def load_config() -> json:
    global _config
    if _config is None:
        with open('./config/config.json', 'r') as f:
            _config = json.load(f)
    return _config

def load_agent_meta_prompt() -> str:
    with open('./config/agent_start_meta_prompt.txt', 'r') as f:
        return f.read()

def load_agent_user_prompt() -> str:
    with open('./config/agent_user_prompt.txt', 'r') as f:
        return f.read()

def load_judge_meta_prompt() -> str:
    with open('./config/judge_meta_prompt.txt', 'r') as f:
        return f.read()
    
def load_judge_user_prompt() -> str:
    with open('./config/judge_user_prompt.txt', 'r') as f:
        return f.read()