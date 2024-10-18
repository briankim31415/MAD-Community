from openai import OpenAI, OpenAIError
import time
import backoff
import json

# Load config
from config_loader import load_config
config = load_config()
sleep_time = config['sleep_time']
chat_models = config['chat_models']
agent_model_index = config['agent_model_index']
meta_prompt = config['meta_prompt']
ask_prompt = config['ask_prompt']
ending_prompt = config['ending_prompt']
judge_model_index = config['judge_model_index']
judge_meta_prompt = config['judge_meta_prompt']
judge_prompt = config['judge_prompt']


class Agent:
    """
    Agent class to interact with OpenAI API
    Attributes:
        name (str): Agent's name
        temperature (float): Temperature for sampling
        model_name (str): OpenAI model name
        meta_prompt (list): Meta-prompt for the agent
        client (OpenAI): OpenAI client
    Methods:
        query(messages: list) -> str: Query OpenAI API
        format_chat_hist(chat_hist: list) -> list: Format community chat history
        ask(chat_hist: list, end: bool=False) -> json: Ask the agent a question based on the chat history
    """
    def __init__(self, name: str, question: str, temperature: float=1.0) -> None:
        """
        Initialize an agent
        Args:
            name (str): Agent's name
            question (str): Question to ask
            temperature (float, optional): Temperature for sampling. Defaults to 1.0.
        Attributes:
            model_name (str): OpenAI model name
            meta_prompt (list): Meta-prompt for the agent
        """
        self.name = name
        self.temperature = temperature
        self.model_name = chat_models[agent_model_index]
        self.meta_prompt = [{"role": "system", "content": f"{meta_prompt.format(question=question)}"}]
        self.client = OpenAI()


    @backoff.on_exception(backoff.expo, OpenAIError, max_tries=20, max_time=60)
    def query(self, messages: list) -> str:
        """
        Query OpenAI API
        Args:
            messages (list): List of messages in the chat
        Returns:
            str: OpenAI API response
        """
        # Query OpenAI API
        time.sleep(sleep_time)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature
            )

            # Extract output from response and return it
            output = response.choices[0].message.content
            return output
        
        # Raise OpenAIError if there's an error
        except OpenAIError as ai_err:
            ai_response_msg = ai_err.body["message"]
            raise OpenAIError(f"OpenAI Error: {ai_response_msg}")


    def format_chat_hist(self, chat_hist: list) -> list:
        """
        Assign community chat history to this agent or other agents
        Args:
            chat_hist (list): Community chat history
        Returns:
            list: Formatted chat history
        """
        # Parse each response in chat history
        agent_chat_hist = []
        for response in chat_hist:
            # Format response from JSON response
            message = f"Option {response['Answer']}. {response['Reason']}"

            # Check if response is from this agent
            if response['Name'] == self.name:
                agent_chat_hist.append({"role": "assistant", "content": message})
            else:
                agent_chat_hist.append({"role": "user", "content": f"{response['Name']}: {message}"})
        
        # Return formatted chat history
        return agent_chat_hist
    

    def ask(self, chat_hist: list, end: bool=False) -> json:
        """
        Ask the agent a question based on the chat history
        Args:
            chat_hist (list): Community chat history
            end (bool, optional): Whether it's the last round. Defaults to False.
        Returns:
            JSON: Agent's response
        """
        # Set prompt based on whether it's the last round
        prompt = ending_prompt if end else ask_prompt
        prompt = prompt.format(agent_name=self.name)
        
        # Format community chat history
        agent_chat_hist = self.format_chat_hist(chat_hist)
        messages = self.meta_prompt + agent_chat_hist + [{"role": "user", "content": prompt}]

        # TODO: Add retry for max number of tries, otherwise fail
        # Query OpenAI API and extract JSON output
        while True:
            output = self.query(messages)
            try:
                json_output = json.loads(output)

                # Check if JSON output contains 'Answer' and 'Reason' keys
                if all(key in json_output for key in ['Answer', 'Reason']):
                    # Add agent's name to JSON output
                    json_output['Name'] = self.name
                    break
            except json.JSONDecodeError:
                # If JSON output is invalid, retry
                print("Invalid JSON response. Retrying...")
                # Extra sleep time just in case
                time.sleep(sleep_time)
                continue
        
        # Return JSON output
        return json_output
    
    
class Judge(Agent):
    """
    Judge agent class to interact with OpenAI API
    Attributes:
        name (str): Judge's name
        temperature (float): Temperature for sampling
        model_name (str): OpenAI model name
        meta_prompt (list): Meta-prompt for the agent
        client (OpenAI): OpenAI client
    Methods:
        ask(community_answers: list) -> str: Ask the judge a question based on the community answers
    """
    def __init__(self, question: str, name: str='Judge', temperature: float=1.0) -> None:
        """
        Initialize a judge agent
        Args:
            question (str): Question to ask
            name (str, optional): Judge's name. Defaults to 'Judge'.
            temperature (float, optional): Temperature for sampling. Defaults to 1.0.
            model_name (str, optional): OpenAI model name. Defaults to 'gpt-3.5-turbo'.
        Attributes:
            model_name (str): OpenAI model name
            meta_prompt (list): Meta-prompt for the agent
        """
        super().__init__(name, question, temperature)
        self.model_name = chat_models[judge_model_index]
        self.meta_prompt = [{"role": "system", "content": f"{judge_meta_prompt.format(question=question)}"}]
    
    def ask(self, community_answers: "list[str]") -> str:
        """
        Ask the judge a question based on the community answers
        Args:
            community_answers (list): Community answers
        Returns:
            str: Judge's response
        """
        # Format community answers
        answers = [{"role": "user", "content": f"{answer}"} for answer in community_answers]
        messages = self.meta_prompt + answers + [{"role": "user", "content": f"{self.name}: {judge_prompt}"}]
        
        # Query OpenAI API and return response
        return self.query(messages)
    
        # Return integer response
        # while True:
        #     output = self.query(messages)
        #     try:
        #         response = int(output.strip())
        #         if response in range(1, 5):
        #             return response
        #     except ValueError:
        #         print("Invalid response. Retrying...")
        #         time.sleep(sleep_time)