from config_loader import load_config, load_network_config
from datetime import datetime
config = load_config()
test_mode = config['test_mode']
save_stats = config['save_stats']
output_path = config['output_path']
network_preset = config['network_preset']
num_questions = config['num_questions']
num_agents = config['num_agents']
num_rounds = config['num_rounds']


# Calculate and dump MAD-Community statistics to JSON file
def get_statistics(response_stats: list) -> None:
    # Check if test mode is enabled
    if test_mode and not save_stats:
        return
    
    # Get network parameters
    _, matrix, temp_list = load_network_config(network_preset)
    num_communities = len(matrix)
    total_agent_responses = num_questions * num_communities * num_agents * num_rounds
    stats = {
                'Judge_Score': 0,
                'Community_Score': [0] * num_communities,
                'Agents_Score': 0
            }

    # Iterate through each question and calculate scores
    for question in response_stats:
        # Calculate judge score
        correct_answer = question['correct_answer']
        judge_answer = all_responses.pop()['Answer']
        stats['Judge_Score'] += 1 if judge_answer == correct_answer else 0

        # Calculate community and agent scores
        all_responses = question['all_responses']
        for i, com_chat_hist in enumerate(all_responses):
            # Calculate community score
            com_answer = com_chat_hist.pop()['Answer']
            stats['Community_Score'][i] += 1 if com_answer == correct_answer else 0

            # Calculate agent score
            for agent in com_chat_hist:
                if 'Previous Response' not in agent['Name']:
                    stats['Agents_Score'] += 1 if agent['Answer'] == correct_answer else 0

    # Calculate percentages
    stats['Judge_Percent'] = round(100 * round(stats['Judge_Score'] / num_questions, 3), 1)
    stats['Community_Percent'] = [round(100 * round(score / num_questions, 3), 1) for score in stats['Community_Score']]
    stats['Agents_Percent'] = round(100 * round(stats['Agents_Score'] / total_agent_responses, 2), 1)

    # Set file name based on test mode and timestamp
    current_time = datetime.now().strftime("%m-%d,%H%M")
    if test_mode:
        file_name = f"test_stats/{current_time}.txt"
    elif save_stats:
        file_name = f"stats_save/stats_{current_time}.txt"
    else:
        file_name = "stats.txt"

    # Save statistics to JSON file
    with open(f"{output_path}{file_name}", 'w') as f:
        f.write("MAD-Community Statistics\n")
        f.write(f"Timestamp: {current_time}\n" if save_stats else "")
        f.write("=========================\n\n")

        if network_preset > 0:
            f.write(f"Network Preset: {network_preset}\n")

        f.write(f"Number of questions: {num_questions}\n")
        f.write(f"Number of communities: {num_communities}\n")
        f.write(f"Number of agents: {num_agents}\n")
        f.write(f"Number of rounds: {num_rounds}\n\n")

        f.write("Community {Temp} Scores\n")
        for i, percent in enumerate(stats['Community_Percent']):
            f.write(f"\tCommunity {i+1} {{{temp_list[i]}}}: {percent}% correct ({stats['Community_Score'][i]}/{num_questions})\n")
        f.write(f"Agents Score: {stats['Agents_Percent']}% correct\n")
        f.write(f"\n[Final Result]\nJudge Score: {stats['Judge_Percent']}% correct ({stats['Judge_Score']}/{num_questions})\n\n")

    return