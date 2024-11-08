from openai import OpenAI, OpenAIError
import time
import backoff
from pydantic import BaseModel

# Load config
from config_loader import *
config = load_config()
sleep_time = config['sleep_time']
chat_models = config['chat_models']
agent_model_index = config['agent_model_index']
judge_model_index = config['judge_model_index']

class Format(BaseModel):
    answer: int
    reason: str


class Agent:
    """
    Agent class to interact with OpenAI API
    Attributes:
        name (str): Agent's name
        temperature (float): Temperature for sampling
        model_name (str): OpenAI model name
        meta_prompt (list): Meta-prompt for the agent
        user_prompt (str): User prompt for the agent
        end_prompt (str): Ending prompt for the agent
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
            user_prompt (str): User prompt for the agent
            end_prompt (str): Ending prompt for the agent
            client (OpenAI): OpenAI client
        """
        self.name = name
        self.temperature = temperature
        self.model_name = chat_models[agent_model_index]
        format_meta_prompt = load_agent_meta_prompt().format(insert_question=question)
        self.meta_prompt = [{"role": "system", "content": format_meta_prompt}]
        self.user_prompt = load_agent_user_prompt()
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
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                response_format=Format
            )

            # Extract output from response and return it
            return response.choices[0].message.parsed
        
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
    

    def ask(self, chat_hist: list, end: bool=False) -> dict:
        """
        Ask the agent a question based on the chat history
        Args:
            chat_hist (list): Community chat history
            end (bool, optional): Whether it's the last round. Defaults to False.
        Returns:
            JSON: Agent's response
        """
        # Format community chat history
        agent_chat_hist = self.format_chat_hist(chat_hist)
        messages = self.meta_prompt + agent_chat_hist + [{"role": "user", "content": self.user_prompt.format(agent_name=self.name)}]

        # Query OpenAI API and return output
        query_output = self.query(messages)
        output = {"Name": self.name, "Answer": query_output.answer, "Reason": query_output.reason}
        return output
    
    
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
            user_prompt (str): User prompt for the judge
        """
        super().__init__(name, question, temperature)
        self.model_name = chat_models[judge_model_index]
        format_meta_prompt = load_judge_meta_prompt().format(insert_question=question)
        self.meta_prompt = [{"role": "system", "content": format_meta_prompt}]
        self.user_prompt = load_judge_user_prompt()
    
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
        messages = self.meta_prompt + answers + [{"role": "user", "content": f"{self.user_prompt}"}]
        
        # Query OpenAI API and return output
        query_output = self.query(messages)
        output = {"Name": self.name, "Answer": query_output.answer, "Reason": query_output.reason}
        return output