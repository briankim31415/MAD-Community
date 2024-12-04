from node import Community, Judge

# Load config
from config_loader import load_config, load_network_config
config = load_config()
verbose = config['verbose']
network_preset = config['network_preset']


# Network class
class Network:
    def __init__(self, question: dict):
        self.all_responses = []
        self.judge = Judge(question)
        self.communities = self.create_communities(question)
    

    # Initialize communities in the network
    def create_communities(self, question: dict) -> list:
        # Load network configuration
        starting, matrix, temp_list = load_network_config(network_preset)

        # Create communities
        com_list = []
        for i, temp in enumerate(temp_list):
            start = True if starting[i] == 1 else False
            C = Community(f"Community {i+1}", question, temp, start)
            com_list.append(C)
        
        # Temporarily add judge to the network for adding listeners
        com_list.append(self.judge)

        # Add listeners and senders
        for from_node, row in enumerate(matrix):
            for to_node, val in enumerate(row):
                # Check if from and to nodes are different
                if val == 1 and from_node != to_node:
                    com_list[from_node].add_send(com_list[to_node])
        
        # Return list of communities minus judge
        return com_list[:-1]
    
    
    # Run the network and return all responses
    def run_network(self) -> dict:
        # Run until all listeners are satisfied
        while not self.judge.check_listeners():
            for com in self.communities:
                if com.check_listeners():
                    # Save agent answers and get community final responses
                    print(f"\n======|| {com.name} ||======" if verbose else "", end='')
                    community_answers = com.run_community()
                    self.all_responses.append(community_answers)

        # Get final answer from all communities and judge
        judge_response = self.judge.run_judge()
        self.all_responses.append(judge_response)
        print(f"      Judge Verdict: {judge_response['Answer']}\n\n" if verbose else "", end='')
        return self.all_responses