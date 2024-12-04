from openai import OpenAI, OpenAIError
import time
import backoff
from pydantic import BaseModel

# Load config
from config_loader import *
config = load_config()
test_mode = config['test_mode']
sleep_time = config['sleep_time']
chat_models = config['chat_models']
agent_model_index = config['agent_model_index']
judge_model_index = config['judge_model_index']
comm_judge_temp = config['comm_judge_temp']

# Agent response format
class Format(BaseModel):
    answer: int
    reason: str


# Agent class
class Agent:
    def __init__(self, name: str, question: dict, temperature: float=0.7):
        self.name = name
        self.temperature = temperature
        self.client = OpenAI()
        self.question = question

        # Agent specific initialization
        self.model_name = chat_models[agent_model_index]
        self.meta_prompt = load_agent_meta_prompt()
        self.user_prompt = load_agent_user_prompt()

    
    # Format user prompt
    def format_user_prompt(self, chat_hist: list) -> str:
        # Add question and choices to user prompt
        question = self.question['question']
        choices = self.question['choices']

        # Add other agents' responses to user prompt
        if not chat_hist:
            other_responses = "No other agents have responded yet."
        else:
            other_responses = "\n".join([f'{res["Name"]}: Chose {res["Answer"]} because "{res["Reason"]}"' for res in chat_hist])

        # Set agent or judge name
        if isinstance(self, CommunityJudge):
            agent_name = "Judge"
        else:
            agent_name = self.name
        
        # Replace placeholders in user prompt
        replace_dict = {
            "question": question,
            "choice_1": choices[0],
            "choice_2": choices[1],
            "choice_3": choices[2],
            "choice_4": choices[3],
            "other_responses": other_responses,
            "agent_name": agent_name
        }
        return self.user_prompt.format(**replace_dict)
    

    # Query OpenAI API
    @backoff.on_exception(backoff.expo, OpenAIError, max_tries=20, max_time=60)
    def query(self, messages: list) -> str:
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
        

    # Ask agent a question
    def ask(self, chat_hist: list) -> dict:
        # Check if test mode is enabled
        if test_mode:
            return {"Name": self.name, "Answer": 1, "Reason": "Test reason"}

        # Format community chat history
        self.format_user_prompt(chat_hist)
        messages = [{"role": "system", "content": self.meta_prompt},
                    {"role": "user", "content": self.format_user_prompt(chat_hist)}]

        # Query OpenAI API and return output
        tries = 0
        fail = False
        while True:
            try:
                tries += 1
                query_output = self.query(messages)
                output = {"Name": self.name, "Answer": query_output.answer, "Reason": query_output.reason}
                print("\nSuccess after fail\n" if fail else "", end='')
                if 1 <= query_output.answer <= 4:
                    break
            except Exception as e:
                # Retry if there's an error
                print(f"\nTry number {tries} >> {e}")
                fail = True
                continue
            
        return output
    

# Agent subclass for community judge
class CommunityJudge(Agent):
    def __init__(self, question: str, name: str='Judge', temperature: float=comm_judge_temp):
        super().__init__(name, question, temperature)

        # Judge specific initialization
        self.model_name = chat_models[judge_model_index]
        self.meta_prompt = load_judge_meta_prompt()
        self.user_prompt = load_judge_user_prompt()