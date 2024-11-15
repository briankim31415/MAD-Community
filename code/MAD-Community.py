import pandas as pd
from network import Network
import json
from tqdm import tqdm
from openai import OpenAI
import time
import random

# Load config
from config_loader import load_config, clear_network_config
config = load_config()
data_path = config['data_path']
output_path = config['output_path']
random_order = config['random_order']
verbose = config['verbose']
num_questions = config['num_questions']
create_num_communities = config['create_num_communities']


class MADCommunity:
    """
    MAD-Community class to run the network
    Attributes:
        answer_list (list): List of answers from agents
        data (pd.DataFrame): Dataframe
    Methods:
        __init__() -> None: Initialize MAD-Community
        parse_data() -> pd.DataFrame: Parse data from CSV file
        get_statistics() -> None: Calculates and dumps MAD-Community statistics to JSON file
        run_cosmosqa() -> None: Run MAD-Community on CosmosQA dataset
    """
    def __init__(self) -> None:
        """
        Initialize MAD-Community
        Args:
            None
        Attributes:
            answer_list (list): List of answers from agents
            data (pd.DataFrame): Dataframe
        """
        self.answer_list = []
        self.data = self.parse_data()


    def parse_data(self) -> pd.DataFrame:
        """
        Parse data from CSV file and return ordered or random questions
        Args:
            None
        Returns:
            pd.DataFrame: Dataframe
        """
        data = pd.read_csv(f"../data/{data_path}")
        if random_order:
            return data.sample(n=num_questions)
        else:
            return data.head(num_questions)


    def run_baseline(self) -> None:
        count_correct = 0
        count_total = 0
        for question in tqdm(self.data.itertuples(), desc="Processing", total=len(self.data), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            print(f"\n\n ########## QUESTION {question[0] + 1} ##########" if verbose else "", end='')

            format_question = f"Context paragraph: {question[2]}\n\nQuestion: {question[3]}\n\nOption 1: {question[4]}\nOption 2: {question[5]}\nOption 3: {question[6]}\nOption 4: {question[7]}\n\nChoose the correct option (1-4) and strictly output **a single integer**."
            answer = question[8] + 1

            client = OpenAI()
            messages = [{"role": "user", "content": format_question}]
            done = False
            count = 0
            while not done:
                count += 1
                if count >= 20:
                    print("\n\nToo many invalid response. Skipping question...\n\n")
                    break
                time.sleep(0.5)
                try:
                    response = client.chat.completions.create(
                        model='gpt-4o-mini',
                        messages=messages
                    )

                    # Extract output from response and return it
                    output = int(response.choices[0].message.content)
                    done = True
            
                # Raise OpenAIError if there's an error
                except Exception as e:
                    print(e)
            

            correct = (output == answer)
            print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {answer}: {question[answer + 3]}\n\n" if verbose else "", end='')

            count_correct += 1 if correct else 0
            count_total += 1

            with open(output_path, 'w') as f:
                json.dump({'correct': count_correct, 'total': count_total}, f, indent=4)


    def run_cosmosqa(self) -> None:
        """
        Run MAD-Community on CosmosQA dataset
        Args:
            None
        Returns:
            None
        """
        # Init counters
        count_correct = 0
        count_total = 0

        # Loop through questions and print TQDM progress bar
        for question in tqdm(self.data.itertuples(), desc="Processing", total=len(self.data), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            print(f"\n\n ########## QUESTION {question[0] + 1} ##########\n" if verbose else "", end='')

            # Format question and answer
            format_question = f"Context paragraph: {question[2]}\n\nQuestion: {question[3]}\n\nOption 1: {question[4]}\nOption 2: {question[5]}\nOption 3: {question[6]}\nOption 4: {question[7]}"
            answer = question[8] + 1

            # Get answer from network
            network = Network(question=format_question)
            response = None
            count = 0
            while response is None:
                # If too many invalid responses, skip question
                count += 1
                if count >= 20:
                    print("\n\nToo many invalid response. Skipping question...\n\n")
                    break

                # Keep asking for response until valid
                try:
                    response = int(network.get_judge_answer().strip())
                    if response not in range(1, 5):
                        print("\n\nInvalid response\n\n.")
                        response = None
                except ValueError:
                    print("\n\nInvalid response.\n\n")
            
            # Skip question if response is None
            if response is None:
                continue
            
            # Store all agents answer list for statistics
            stats = {'correct_answer': answer, 'agent_answers': network.get_agent_answers()}
            self.answer_list.append(stats)

            # Check if answer is correct
            correct = (response == answer)
            print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {answer}: {question[answer + 3]}\n\n" if verbose else "", end='')

            # Update correct/total statistics
            count_correct += 1 if correct else 0
            count_total += 1

            # Save correct count to JSON file
            with open(output_path, 'w') as f:
                json.dump({'correct': count_correct, 'total': count_total}, f, indent=4)
        
        
    def run_gpqa(self) -> None:
        """
        Run MAD-Community on GPQA dataset
        Args:
            None
        Returns:
            None
        """
        # Init counters
        count_correct = 0
        count_total = 0
        
        # GPQA Column indices
        question_col_idx = self.data.columns.get_loc("Question") + 1
        correct_col_idx = self.data.columns.get_loc("Correct Answer") + 1
        incorrect1_col_idx = self.data.columns.get_loc("Incorrect Answer 1") + 1
        incorrect2_col_idx = self.data.columns.get_loc("Incorrect Answer 2") + 1
        incorrect3_col_idx = self.data.columns.get_loc("Incorrect Answer 3") + 1
        canary_col_idx = self.data.columns.get_loc("Canary String") + 1

        # Loop through questions and print TQDM progress bar
        for row in tqdm(self.data.itertuples(), desc="Processing", total=len(self.data), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            question_id = row[canary_col_idx]
            print(f"\n\n ########## QUESTION {count_total+1} {{{question_id}}} ##########\n" if verbose else "", end='')

            # Format question and answer
            question = row[question_col_idx]
            choices = [row[correct_col_idx], row[incorrect1_col_idx], row[incorrect2_col_idx], row[incorrect3_col_idx]]
            random.shuffle(choices)
            correct_idx = choices.index(row[correct_col_idx])
            prompt = question + ("\n\n" + "\n".join([f"{i+1}. {choice}" for i, choice in enumerate(choices)]))

            # Get answer from network
            network = Network(question=prompt)
            response = network.run_network()
            ans_choice = response['Answer']
            
            # Store all agents answer list for statistics
            # stats = {'correct_answer': correct_idx + 1, 'agent_answers': network.get_agent_answers()}
            # self.answer_list.append(stats)

            # Check if answer is correct
            print(f"\nCorrect_idx: {correct_idx}, Response: {ans_choice}\n")
            correct = (correct_idx + 1 == ans_choice)
            print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {correct_idx + 1}: {choices[correct_idx]}\n\n" if verbose else "", end='')

            # Update correct/total statistics
            count_correct += 1 if correct else 0
            count_total += 1

            # Save correct count to JSON file
            with open(output_path, 'w') as f:
                json.dump({'correct': count_correct, 'total': count_total}, f, indent=4)


if __name__ == "__main__":
    clear_network_config(create_num_communities)
    # gpqa = MADCommunity()
    # gpqa.run_gpqa()