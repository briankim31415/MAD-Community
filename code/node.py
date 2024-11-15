from agent import Agent
from agent import CommunityJudge

# Load config
from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_agents = config['num_agents']
num_rounds = config['num_rounds']


class Node:
    """
    Node class to interact
    """
    def __init__(self, name: str, start: bool=False) -> None:
        self.name = name
        self.listen_list = []
        self.send_list = []
        self.chat_hist = []
        self.completed = False
        self.start = start


    def listener(self, response: dict) -> None:
        if response['Name'] in self.listen_list:
            # print(f"\t{self.name} received {response['Name']}\n" if verbose else "", end='')
            self.listen_list.remove(response['Name'])
            add_response = response.copy()
            add_response['Name'] = f"[Previous Response {len(self.chat_hist)+1}]"
            self.chat_hist.append(add_response)
        else:
            print(f"\n\n\nERROR: [{self.name}] listener for {response['Name']} not in listen_list.\n")


    def check_listeners(self) -> bool:
        # Check if node is a starting node
        if self.start and not self.completed:
            self.completed = True
            return True
        
        # Check if ready to run the node
        if len(self.listen_list) == 0 and not self.completed:
            # Check if there are listening nodes or if the node is a judge
            if len(self.send_list) > 0 or self.name == 'Judge':
                self.completed = True
                return True
        
        return False
    

    def add_listener(self, community_name: str) -> None:
        self.listen_list.append(community_name)
    
    
    def add_send(self, community: 'Node') -> None:
        self.send_list.append(community)
        community.add_listener(self.name)


class Community(Node):
    def __init__(self, name: str, question: str, temperature: float=1.0, start: bool=False) -> None:
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
        super().__init__(name=name, start=start)
        self.agent_list = self.create_agents(question, temperature)
        self.community_judge = CommunityJudge(question=question, name=name)
        

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
            agent = Agent(f"Agent {i+1}", question=question, temperature=temperature, start=self.start)
            agent_list.append(agent)
        return agent_list


    def run_community(self) -> list:
        """
        Perform community functions
        Args:
            None
        Returns:
            list: List of answers from agents
        """
        # Get answers from agents
        self.debate()
        
        # Get final judge answer for community
        final_answer = self.community_judge.ask(self.chat_hist[-num_agents:])
        self.chat_hist.append(final_answer)
        # print(f"{self.name} Judge chose Option {final_answer['Answer']}\n   {final_answer['Reason']}\n\n" if verbose else "", end='')
        print(f"{self.name} Judge chose Option {final_answer['Answer']}\n\n" if verbose else "", end='')
        

        # Feed response to communities
        # print(f"\n-- {self.name} sending to: {', '.join(com.name for com in self.send_list)}\n" if verbose else "", end='')
        for community in self.send_list:
            community.listener(final_answer)

        # Return entire chat history for stat tracking
        return self.chat_hist
    

    def debate(self) -> None:
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
            for agent in self.agent_list:
                # Get response from agent
                response = agent.ask(self.chat_hist)
                self.chat_hist.append(response)
                # print(f"{response['Name']} chose Option {response['Answer']}\n   {response['Reason']}\n\n" if verbose else "", end='')
                print(f"{response['Name']} chose Option {response['Answer']}\n" if verbose else "", end='')


class Judge(Node):
    def __init__(self, question: str, name: str='Judge', temperature: float=1.0) -> None:
        """
        Initialize a judge
        Args:
            question (str): Question to ask
            temperature (float, optional): Temperature for sampling. Defaults to 1.0.
        """
        super().__init__(name=name)
        self.judge = CommunityJudge(question, name, temperature)
    

    def run_judge(self) -> dict:
        print("\n\n <<< Running Judge node >>>\n" if verbose else "", end='')
        return self.judge.ask(self.chat_hist)