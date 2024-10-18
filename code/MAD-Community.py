import pandas as pd
from network import Network
import json
from tqdm import tqdm

from config_loader import load_config
config = load_config()
verbose = config['verbose']
num_questions = config['num_questions']
num_communities = config['num_communities']

def parse_data(file_name: str) -> pd.DataFrame:
    data = pd.read_csv(f"../data/{file_name}")
    return data

def cosmosqa() -> list:
    cosmosqa = parse_data('train.csv')
    
    community_answers = {'correct': 0, 'total': 0}
    for i in range(1, num_communities + 1):
        community_answers[f'community_{i}'] = 0

    cosmosqa = cosmosqa.head(num_questions)
    
    for question in tqdm(cosmosqa.itertuples(), desc="Processing", total=len(cosmosqa), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
        print(f" ########## QUESTION {question[0] + 1} ##########\n" if verbose else "", end='')
        format_question = f"Context paragraph: {question[2]}\n\nQuestion: {question[3]}\n\nOption 1: {question[4]}\nOption 2: {question[5]}\nOption 3: {question[6]}\nOption 4: {question[7]}"
        answer = question[8] + 1

        network = Network(question=format_question)
        response = network.get_answer()
        if response is None:
            print("Error: Unable to get answer\n")
            continue

        correct = response[-1] == (answer)
        print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {answer}: {question[answer + 3]}\n" if verbose else "", end='')

        community_answers['correct'] += 1 if correct else 0
        community_answers['total'] += 1

        for i in range(1, num_communities + 1):
            community_answers[f'community_{i}'] += 1 if response[i - 1] == (answer) else 0
        
        # Save answer count to JSON file
        with open('answers.json', 'w') as f:
            json.dump(community_answers, f, indent=4)
    
    return community_answers


if __name__ == "__main__":
    out = cosmosqa()
    print(f"{out['correct']} out of {out['total']} correct\nDone")