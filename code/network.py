from agent import Judge
from community import Community
import numpy as np

# Load config
from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_communities = config['num_communities']


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
        self.agent_answers = []
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
        com_list = []
        community_temps = np.linspace(0.5, 1.5, num_communities).tolist()
        for temp in community_temps:
            C = Community(question, temp)
            com_list.append(C)
        return com_list
    

    def get_agent_answers(self) -> list:
        """
        Get answers from all agents
        Args:
            None
        Returns:
            list: List of answers from all agents
        """
        return self.agent_answers
    

    def get_community_responses(self) -> list:
        """
        Get responses from all communities
        Args:
            None
        Returns:
            list: List of responses from all communities
        """
        com_responses = []
        for i, community in enumerate(self.communities):
            # Get community final responses
            print(f"\n >> COMMUNITY {i+1} <<\n" if verbose else "", end='')
            response = community.get_community_answer()
            com_responses.append(response)

            # Get agent answers
            self.agent_answers.append(community.get_answer_list())
        return com_responses


    def get_judge_answer(self) -> str:
        """
        Get final answer from all communities
        Args:
            None
        Returns:
            str: Judge's final answer
        """
        # Get responses from all communities
        responses = self.get_community_responses()
        combined_responses = [f"Final answer: {response['Answer']}\n\nReason: {response['Reason']}" for response in responses]

        # Get and return judge's answer
        judge_response = self.judge.ask(combined_responses)
        print(f"\n\n - Judge Verdict: {judge_response}\n\n" if verbose else "", end='')
        return judge_response