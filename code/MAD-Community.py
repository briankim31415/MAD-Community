import pandas as pd
from network import Network
import json
from tqdm import tqdm

# Load config
from config_loader import load_config
config = load_config()
data_path = config['data_path']
output_path = config['output_path']
verbose = config['verbose']
num_questions = config['num_questions']
num_communities = config['num_communities']


class MADCommunity:
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
        Parse data from CSV file
        Args:
            file_name (str): File name
        Returns:
            pd.DataFrame: Dataframe
        """
        data = pd.read_csv(f"../data/{data_path}")
        return data.head(num_questions)


    def get_statistics(self) -> None:
        """
        Calculates and dumps MAD-Community statistics to JSON file
        Args:
            None
        Returns:
            None
        """
        # Get correct count statistics
        with open(output_path, 'r') as f:
            data = json.load(f)

        # Init statistics to calculate
        perc_com_cor = [0 for _ in range(num_communities)]
        perc_agent_cor = [0 for _ in range(num_communities)]

        # Loop through questions and calculate statistics
        for _, question in enumerate(self.answer_list):
            correct_answer = question['correct_answer']
            community_lists = question['agent_answers']

            # perc_com_cor: percentage of communities that got the correct answer
            community_answers = [1 if com[-1] == correct_answer else 0 for com in community_lists]
            perc_com_cor = [perc_com_cor[j] + community_answers[j] for j in range(num_communities)]

            # perc_agent_cor: percentage of agents that got the correct answer per community, excluding community answer
            for j, com in enumerate(community_lists):
                agent_correct_count = [0 for _ in range(num_communities)]
                for agent_answer in com[:-1]:
                    agent_correct_count[j] += 1 if agent_answer == correct_answer else 0
                perc_agent_cor[j] += agent_correct_count[j] / len(com[:-1])
        

        # Add new statistics
        perc_com_cor = [round(perc / data['total'], 3) for perc in perc_com_cor]
        for i in range(num_communities):
            data[f'perc_com_cor_{i}'] = perc_com_cor[i]
        
        perc_agent_cor = [round(perc / data['total'], 3) for perc in perc_agent_cor]
        for i in range(num_communities):
            data[f'perc_agent_cor_{i}'] = perc_agent_cor[i]

        # Save statistics to JSON file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)


    def run_cosmosqa(self) -> None:
        """
        Run MAD-Community on CosmosQA dataset
        Args:
            None
        Returns:
            dict: Answer statistics
        """
        count_correct = 0
        count_total = 0

        # Loop through questions and print TQDM progress bar
        for question in tqdm(self.data.itertuples(), desc="Processing", total=len(self.data), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            print(f" ########## QUESTION {question[0] + 1} ##########\n" if verbose else "", end='')

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
                    print("Too many invalid response. Skipping question...")
                    break

                # Keep asking for response until valid
                try:
                    response = int(network.get_judge_answer().strip())
                    if response not in range(1, 5):
                        print("Invalid response.")
                        response = None
                except ValueError:
                    print("Invalid response.")
            
            # Skip question if response is None
            if response is None:
                continue
            
            # Store all agents answer list for statistics
            stats = {'correct_answer': answer, 'agent_answers': network.get_agent_answers()}
            self.answer_list.append(stats)

            # Check if answer is correct
            correct = (response == answer)
            print(f"{'Correct!' if correct else 'Wrong!'} The answer is...\nOption {answer}: {question[answer + 3]}\n" if verbose else "", end='')

            # Update correct/total statistics
            count_correct += 1 if correct else 0
            count_total += 1

            # Save correct count to JSON file
            with open(output_path, 'w') as f:
                json.dump({'correct': count_correct, 'total': count_total}, f, indent=4)
        

if __name__ == "__main__":
    """
    Run MAD-Community
    """
    # Run MAD-Community on CosmosQA dataset
    cosmosqa = MADCommunity()
    cosmosqa.run_cosmosqa()