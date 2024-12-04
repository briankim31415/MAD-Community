import pandas as pd
from network import Network
import json
from tqdm import tqdm
import random
from stats import get_statistics

# Load config
from config_loader import load_config, clear_network_config
config = load_config()
test_mode = config['test_mode']
output_path = config['output_path']
random_order = config['random_order']
verbose = config['verbose']
num_questions = config['num_questions']
question_start = config['question_start']
create_num_communities = config['create_num_communities']


# MAD-Community class
class MADCommunity:
    # Parse data from given CSV file
    def parse_data(self, data_path: str) -> pd.DataFrame:
        data = pd.read_csv(f"../data/{data_path}")
        if random_order:
            return data.sample(n=num_questions)
        else:
            return data[question_start:question_start+num_questions]
        
    
    # Run MAD-Community on GPQA dataset
    def run_gpqa(self) -> list:
        # Get data
        data = self.parse_data("gpqa_dataset/gpqa_main.csv")

        # Init counters and responses for statistics
        count_correct = 0
        count_total = 0
        response_stats = []
        
        # GPQA Column indices
        question_col_idx = data.columns.get_loc("Question") + 1
        correct_col_idx = data.columns.get_loc("Correct Answer") + 1
        incorrect1_col_idx = data.columns.get_loc("Incorrect Answer 1") + 1
        incorrect2_col_idx = data.columns.get_loc("Incorrect Answer 2") + 1
        incorrect3_col_idx = data.columns.get_loc("Incorrect Answer 3") + 1
        canary_col_idx = data.columns.get_loc("Canary String") + 1

        # Loop through questions and print TQDM progress bar
        for row in tqdm(data.itertuples(), desc="Processing", total=len(data), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            question_id = row[canary_col_idx]
            print(f"\n\n ########## QUESTION {count_total+1} {{{question_id}}} ##########" if verbose else "", end='')

            # Format question and answer
            question = row[question_col_idx]
            choices = [row[correct_col_idx], row[incorrect1_col_idx], row[incorrect2_col_idx], row[incorrect3_col_idx]]
            random.shuffle(choices)
            correct_idx = choices.index(row[correct_col_idx])
            question = {'question': question, 'choices': choices}

            # Get answer from network
            network = Network(question)
            all_responses = network.run_network()
            ans_choice = all_responses[-1]['Answer']
            response_stats.append({'correct_answer': correct_idx + 1, 'all_responses': all_responses})

            # Check if answer is correct
            correct = (correct_idx + 1 == ans_choice)
            print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {correct_idx + 1}: {choices[correct_idx]}\n\n" if verbose else "", end='')

            # Update correct/total statistics
            count_correct += 1 if correct else 0
            count_total += 1

            # Save correct count to JSON file
            if not test_mode:
                with open(f"{output_path}gpqa_main_output.json", 'w') as f:
                    json.dump({'correct': count_correct, 'total': count_total}, f, indent=4)
        
        # Return response statistics
        return response_stats


# Call MADCommunity class
if __name__ == "__main__":
    # Initialize MADCommunity and run GPQA
    clear_network_config(create_num_communities)
    gpqa = MADCommunity()
    response_stats = gpqa.run_gpqa()
    
    # Log statistics
    get_statistics(response_stats)