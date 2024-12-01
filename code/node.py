from agent import Agent
from agent import CommunityJudge

# Load config
from config_loader import load_config
config = load_config()
verbose = config['verbose']
verbose_message_passing = config['verbose_message_passing']
verbose_responses = config['verbose_responses']
num_agents = config['num_agents']
num_rounds = config['num_rounds']
node_judge_temp = config['node_judge_temp']


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
            print(f"\t{self.name} received {response['Name']}\n" if verbose_message_passing else "", end='')
            self.listen_list.remove(response['Name'])
            add_response = response.copy()
            add_response['Name'] = f"Agent {len(self.chat_hist)+1}"
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
    def __init__(self, name: str, question: dict, temperature: float, start: bool) -> None:
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
        super().__init__(name, start)
        self.agent_list = self.create_agents(question, temperature)
        self.community_judge = CommunityJudge(question, name)
        

    def create_agents(self, question: dict, temperature: float) -> list:
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
            agent = Agent(f"Agent {chr(65 + i)}", question, temperature)
            agent_list.append(agent)
        return agent_list
    

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
                print(f"{response['Name']}: Option {response['Answer']}\n" if verbose else "", end='')
                print(f"   {response['Reason']}\n\n" if verbose_responses else "", end='')


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
        print(f"\n + {self.name} Judge chose Option {final_answer['Answer']} +\n" if verbose else "", end='')
        print(f"   {final_answer['Reason']}\n" if verbose_responses else "", end='')

        # Feed response to communities
        print(f"\n-- {self.name} sending to: {', '.join(com.name for com in self.send_list)}\n" if verbose_message_passing else "", end='')
        for community in self.send_list:
            community.listener(final_answer)

        # Return entire chat history for stat tracking
        return self.chat_hist
    


class Judge(Node):
    def __init__(self, question: dict, name: str='Judge') -> None:
        """
        Initialize a judge
        Args:
            question (str): Question to ask
        """
        super().__init__(name=name)
        self.judge = CommunityJudge(question, name, node_judge_temp)
    

    def run_judge(self) -> dict:
        print("\n <<< Running Judge node >>>\n" if verbose else "", end='')
        return self.judge.ask(self.chat_hist)