# MAD-Community
 LLM Multi-Agent Debate with Communities

## How to Run the Code

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/MAD-Community.git
    cd MAD-Community
    ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configuration:**
    - Modify the `config.json` file to adjust the parameters as needed [#configjson-parameters].
    - To define a network, modify the `network_config.txt` file [#network-config].

4. **Run the main script in code directory:**
    ```bash
    cd code
    python MAD-Community.py
    ```


## Config.json Parameters

`verbose`: Set to `True` to print when communities and agents run
`verbose_responses`: Set to `True` to print agent responses
`verbose_message_passing`: Set to `True` to print community listeners
`test_mode`: Set to `True` to not query ChatGPT and pass sample responses
`save_stats`: Set to `True` to save statistics to .txt file
`output_path`: Path of directory to save output files
`network_preset`: Select network preset defined in `network_config_presets.txt`
`create_num_communities`: Set to `0` to use network preset, otherwise the number of communities to create
`random_order`: Set to `True` to randomly select questions
`question_start`: Question number to start from
`num_questions`: Number of questions to answer
`num_agents`: Number of agents per community
`num_rounds`: Number of multi-agent debate rounds per community
`sleep_time`: Wait time before querying ChatGPT
`chat_models`: List available ChatGPT models
`agent_model_index`: Index of selected model in `chat_models` for agents
`judge_model_index`: Index of selected model in `chat_models` for judges
`node_judge_temp`: Network judge temperature
`comm_judge_temp`: Community judge temperature



## Network Config

To define a custom network of nodes, follow the following steps:

1. **Set number of communities**
    - Modify the `create_num_communities` parameter in `config.json` with the number of desired MAD communities

2. **Clear the network config file**
    ```bash
    cd code
    python MAD-Community.py
    ```

3. **Edit the network config file**
    - In `network_config.txt`, replace each `0` with a `1` in the matrix to create your desired network
    - Rows are the `from` node and columns are the `to` node
    - The row `Qn` will mark which communities are the starting nodes
    - The column `J` will mark which communities are the final nodes before the network judge
    - `C1`, `C2`, `C3`,... corresponds to Community 1, Community 2, Community 3, etc.
    - Set the temperature of each community (default is 1.0)

4. **Comment out clear config file code**
    - In `MAD-Community.py`, comment out line 87 `# clear_network_config(create_num_communities)`

5. **Run the code**
    ```bash
    python MAD-Community.py
    ```