from agent import Judge
from community import Community
import numpy as np
import json

from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_communities = config['num_communities']

class Network:
    def __init__(self, question: str) -> None:
        self.communities = self.create_communities(question)
        self.judge = Judge(question)

    def create_communities(self, question: str) -> list:
        com_list = []
        community_temps = np.linspace(0.5, 1.5, num_communities).tolist()
        for temp in community_temps:
            C = Community(question, temp)
            com_list.append(C)
        return com_list
    
    def get_responses(self) -> list:
        responses = []
        for community in self.communities:
            print(f"\n >> COMMUNITY {self.communities.index(community)+1} <<\n" if verbose else "", end='')
            response = community.debate()
            responses.append(response)
        return responses

    def get_answer(self) -> list:
        responses = self.get_responses()

        try:
            responses = [json.loads(response) for response in responses]
        except Exception:
            return None
        
        combined_responses = [f"Final answer: {response['Option']}\nReason: {response['Reason']}" for response in responses]
        judge_response = self.judge.ask(combined_responses)
        print(f" - Judge Verdict: {judge_response}\n" if verbose else "", end='')

        # Get all answers i.e. [com1, com2, ..., comN, judge]
        try:
            all_answers = [int(response['Option']) for response in responses]
            all_answers.append(int(judge_response))
        except Exception:
            return None
        
        return all_answers