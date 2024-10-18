from agent import Agent

from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_agents = config['num_agents']
num_rounds = config['num_rounds']
ending_prompt = config['ending_prompt']

class Community:
    def __init__(self, question: str, temperature: float=1.0) -> None:
        self.temperature = temperature
        self.agents = []
        self.create_agents(question)

    def create_agents(self, question: str) -> None:
        for i in range(num_agents):
            agent = Agent(f"Agent {i+1}", question, self.temperature)
            self.agents.append(agent)
    
    def debate(self) -> str:
        response = ""
        for i in range(num_rounds):
            print(f"Round {i+1}...\n" if verbose else "", end='')
            for j, agent in enumerate(self.agents):
                if i == num_rounds - 1 and j == num_agents - 1:    # Last round and last agent
                    response = agent.ask(ending_prompt)
                else:
                    response = agent.ask()
                    for k in range(num_agents):
                        if j != k:
                            self.agents[k].add_chat(agent.name, response)
                
                # Print resposne
                print(f"Round {i+1}, {agent.name}: {response}\n" if verbose else "", end='')
        
        return response