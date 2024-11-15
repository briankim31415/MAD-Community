from node import Community, Judge

# Load config
from config_loader import load_config, load_network_config
config = load_config()
verbose = config['verbose']
network_path = config['network_path']
network_preset = config['network_preset']


class Network:
    """
    Network class to interact with communities
    Attributes:
        agent_answers (list): List of answers from all agents
        judge (Judge): Judge agent
        communities (list): List of communities in the network
    Methods:
        create_communities(question: str) -> list: Create communities in the network
        get_agent_answers() -> list: Get answers from all agents
        get_community_responses() -> list: Get responses from all communities
        get_judge_answer() -> str: Get final answer from all communities
    """
    def __init__(self, question: str) -> None:
        """
        Initialize a network
        Args:
            question (str): Question to ask
        Attributes:
            agent_answers (list): List of answers from all agents
            judge (Judge): Judge agent
            communities (list): List of communities in the network
        """
        self.all_responses = []
        self.judge = Judge(question)
        self.communities = self.create_communities(question)
    

    def create_communities(self, question: str) -> list:
        """
        Create communities in the network
        Args:
            question (str): Question to ask
        Returns:
            list: List of communities in the network
        """
        starting, matrix, temp_list = load_network_config(network_preset)

        com_list = []
        for i, temp in enumerate(temp_list):
            start = True if starting[i] == 1 else False
            C = Community(f"Community {i+1}", question, temp, start)
            com_list.append(C)
        
        com_list.append(self.judge)

        # Add listeners and senders
        for from_node, row in enumerate(matrix):
            for to_node, val in enumerate(row):
                # Check if from and to nodes are different
                if val == 1 and from_node != to_node:
                    com_list[from_node].add_send(com_list[to_node])
        
        # Return list of communities minus judge
        return com_list[:-1]
    
    
    def run_network(self) -> dict:
        """
        Run the network to get final answer
        Args:
            None
        Returns:
            dict: Final answer from the network
        """
        # com_responses = []

        while not self.judge.check_listeners():
            # Get responses from all communities
            for com in self.communities:
                if com.check_listeners():
                    # Save agent answers and get community final responses
                    print(f"\n\n\n\t======|| {com.name} ||======\n" if verbose else "", end='')
                    community_answers = com.run_community()
                    self.all_responses.append(community_answers)

        # Get final answer from all communities
        judge_response = self.judge.run_judge()
        self.all_responses.append(judge_response)
        print(f"      Judge Verdict: {judge_response['Answer']}\n\n" if verbose else "", end='')
        return self.all_responses