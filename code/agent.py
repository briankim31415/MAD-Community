from openai import OpenAI, OpenAIError
import time
import backoff

from config_loader import load_config
config = load_config()
sleep_time = config['sleep_time']
chat_models = config['chat_models']
meta_prompt = config['meta_prompt']
ask_prompt = config['ask_prompt']
judge_meta_prompt = config['judge_meta_prompt']
judge_prompt = config['judge_prompt']

class Agent:
    def __init__(self, name: str, question: str, temperature: float=1.0, model_name: str='gpt-3.5-turbo') -> None:
        self.name = name
        self.temperature = temperature
        self.model_name = model_name
        self.meta_prompt = [{"role": "system", "content": f"{meta_prompt.format(question=question)}"}]
        self.chat_hist = []
        self.client = OpenAI()

    @backoff.on_exception(backoff.expo, OpenAIError, max_tries=20, max_time=60)
    def query(self, messages: "list[dict]") -> str:
        time.sleep(sleep_time)
        assert self.model_name in chat_models, f"Model {self.model_name} not supported"
        try:
            if self.model_name in chat_models:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature
                )
                output = response.choices[0].message.content
                
                # Add output to chat history
                self.chat_hist.append({"role": "assistant", "content": f"{output}"})
                
                return output
        except OpenAIError as ai_err:
            ai_response_msg = ai_err.body["message"]
            raise OpenAIError(f"OpenAI Error: {ai_response_msg}")
    
    def add_chat(self, agent: str, message: str) -> None:
        self.chat_hist.append({"role": "user", "content": f"{agent}: {message}"})
    
    def ask(self, prompt: str=ask_prompt) -> str:
        messages = self.meta_prompt + self.chat_hist + [{"role": "user", "content": f"{self.name}: {prompt}"}]
        return self.query(messages)
    
    
class Judge(Agent):
    def __init__(self, question: str, name: str='Judge', temperature: float=1.0, model_name: str='gpt-3.5-turbo') -> None:
        super().__init__(name, question, temperature, model_name)
        self.meta_prompt = [{"role": "system", "content": f"{judge_meta_prompt.format(question=question)}"}]
    
    def ask(self, community_answers: "list[str]") -> str:
        answers = [{"role": "user", "content": f"{answer}"} for answer in community_answers]
        messages = self.meta_prompt + answers + [{"role": "user", "content": f"{self.name}: {judge_prompt}"}]
        return self.query(messages)