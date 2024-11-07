from agent import Agent
from agent import Judge

# Load config
from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_agents = config['num_agents']
num_rounds = config['num_rounds']


class Community:
    """
    Community class to interact with agents
    Attributes:
        chat_hist (list): Chat history of the community
        answer_list (list): List of answers from agents
        agent_list (list): List of agents in the community
    Methods:
        create_agents(question: str, temperature: float) -> list: Create agents in the community
        get_answer_list() -> list: Get answer list from agents
        get_community_answer() -> json: Get final community answer
        run_debate() -> None: Debate among agents in the community
    """
    def __init__(self, question: str, temperature: float=1.0) -> None:
        """
        Initialize a community
        Args:
            question (str): Question to ask
            temperature (float, optional): Temperature for sampling. Defaults to 1.0.
        Attributes:
            chat_hist (list): Chat history of the community
            answer_list (list): List of answers from agents
            agent_list (list): List of agents in the community
        """
        self.chat_hist = []
        self.agent_list = self.create_agents(question, temperature)
        self.judge = Judge(question)
        

    def create_agents(self, question: str, temperature: float) -> list:
        """
        Create agents in the community
        Args:
            question (str): Question to ask
            temperature (float): Temperature for sampling
        Returns:
            list: List of agents in the community
        """
        agent_list = []
        for i in range(num_agents):
            agent = Agent(f"Agent {i+1}", question, temperature)
            agent_list.append(agent)
        return agent_list
    

    def get_chat_hist(self) -> list:
        """
        Get answer list from agents
        Args:
            None
        Returns:
            list: List of answers from agents
        """
        self.run_debate()
        
        # Get final judge answer for community
        final_answer = self.judge.ask(self.chat_hist[-num_agents:])
        self.chat_hist.append(final_answer)
        print(f"Community Judge chose Option {final_answer['Answer']}\n   {final_answer['Reason']}\n\n" if verbose else "", end='')
        
        return self.chat_hist


    def run_debate(self) -> None:
        """
        Debate among agents in the community
        Args:
            None
        Returns:
            None
        """
        # Iterate through agents for num_rounds
        for i in range(num_rounds):
            print(f"\n  [ Round {i+1} ]\n" if verbose else "", end='')
            for j, agent in enumerate(self.agent_list):
                # Check if it's the last round and last agent
                is_end = (i == num_rounds - 1) and (j == num_agents - 1)

                # TODO FUTURE TESTING: Keep chat_hist max length to num_agents
                # if len(self.chat_hist) >= num_agents:
                    # self.chat_hist = self.chat_hist[-num_agents:]

                # Get response from agent
                response = agent.ask(self.chat_hist, is_end)
                self.chat_hist.append(response)
                print(f"{response['Name']} chose Option {response['Answer']}\n   {response['Reason']}\n\n" if verbose else "", end='')