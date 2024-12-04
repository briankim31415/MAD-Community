import json
import sys

_config = None

# Load global config file
def load_config() -> json:
    global _config
    if _config is None:
        with open('./config/_config.json', 'r') as f:
            _config = json.load(f)
    return _config

# Load agent meta prompt
def load_agent_meta_prompt() -> str:
    with open('./config/agent_meta_prompt.txt', 'r') as f:
        return f.read()

# Load agent user prompt
def load_agent_user_prompt() -> str:
    with open('./config/agent_user_prompt.txt', 'r') as f:
        return f.read()

# Load judge meta prompt
def load_judge_meta_prompt() -> str:
    with open('./config/judge_meta_prompt.txt', 'r') as f:
        return f.read()
    
# Load judge user prompt
def load_judge_user_prompt() -> str:
    with open('./config/judge_user_prompt.txt', 'r') as f:
        return f.read()
    

# Load network configuration/preset
def load_network_config(preset_config: int=0) -> list:
    lines = []
    if preset_config == 0:
        # Open network config file
        with open('./config/network_config.txt', 'r') as file:
            lines = file.read().splitlines()
    else:
        lines = set_network_config(preset_config)

    # First line is starting communities
    starting_char = (lines[1].split("Qn")[-1][1:]).split()
    starting = [int(char) for char in starting_char]

    # Remaining lines are network matrix
    matrix = []
    for line in lines[2:]:
        if line.strip() == "":
            break
        char_list = (line.split("C")[-1][1:]).split()
        int_list = [int(char) for char in char_list]
        matrix.append(int_list)
    
    # Get community temperatures
    temp_list = []
    temp_idx = lines.index("Temperatures")
    for line in lines[temp_idx + 1:]:
        if line.strip() == "":
            break
        temp = float(line.split(": ")[-1].strip())
        temp_list.append(temp)
    
    # Return 3 lists
    return [starting, matrix, temp_list]


# Clear manual network configuration file
def clear_network_config(num_communities: int) -> None:
    # Resume program if not creating new network
    if num_communities == 0:
        return

    # Column headers
    result = []
    result.append("  To \u2192    " + " ".join(f"C{i+1}" for i in range(num_communities)) + "  J")
    result.append((f"From \u2193 Qn " + " 0 " * (num_communities)).rstrip())

    # Rows
    for i in range(num_communities):
        result.append((f"       C{i+1} " + " 0 " * (num_communities+1)).rstrip())

    # Temperatures
    result.append("\n")
    result.append("Temperatures")
    result.append("\n".join(f"C{i+1}: 1.0" for i in range(num_communities)))
    
    # Write to file
    output = "\n".join(result)
    with open("./config/network_config.txt", 'w') as file:
        file.write(output)

    print(f"Network matrix of {num_communities} communities initialized.")
    
    # Exit program
    sys.exit()


# Set network configuration from preset
def set_network_config(preset_index: int) -> list:
    # Read from network_config.txt if no preset is chosen
    if preset_index == 0:
        print("\nReading from network_config.txt\n")
        return

    # Read from network_config_presets.txt
    with open("./config/network_config_presets.txt", 'r') as file:
        lines = file.read().splitlines()

    # Get preset lines
    preset_lines = []
    preset_indexes = [i for i, line in enumerate(lines) if line.startswith("[")]
    for i, idx in enumerate(preset_indexes):
        if lines[idx].startswith(f"[{preset_index}]"):
            start_idx = idx + 1
            end_idx = preset_indexes[i + 1] if i + 1 < len(preset_indexes) else len(lines)
            preset_lines = lines[start_idx:end_idx]
            break
    
    # Remove empty lines at the end
    while preset_lines and preset_lines[-1].strip() == "":
        preset_lines.pop()
    
    # Return preset lines
    return preset_lines