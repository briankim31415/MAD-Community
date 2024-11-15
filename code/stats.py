def get_statistics(response_stats: list, output_path: str) -> None:
    """
    Calculates and dumps MAD-Community statistics to JSON file
    Args:
        None
    Returns:
        None
    """
    num_communities = len(response_stats[0]['all_responses']) - 1
    stats = {   
                'Judge_Score': 0,
                'Community_Score': [0] * num_communities,
                'Agents_Score': 0.0
            }

    for question in response_stats:
        correct_answer = question['correct_answer']
        all_responses = question['all_responses']
        judge_answer = all_responses.pop()['Answer']
        stats['Judge_Score'] += 1 if judge_answer == correct_answer else 0

        agent_question_score = 0
        for i, com_chat_hist in enumerate(all_responses):
            com_answer = com_chat_hist.pop()['Answer']
            stats['Community_Score'][i] += 1 if com_answer == correct_answer else 0

            agent_correct = [1 if agent['Answer'] == correct_answer else 0 for agent in com_chat_hist]
            agent_question_score += float(sum(agent_correct) / len(com_chat_hist))
        
        stats['Agents_Score'] += agent_question_score / num_communities
    
    stats['Judge_Score'] = round(stats['Judge_Score'] / len(response_stats), 3)
    stats['Community_Score'] = [round(score / len(response_stats), 3) for score in stats['Community_Score']]
    stats['Agents_Score'] = round(stats['Agents_Score'] / len(response_stats), 3)

    # Save statistics to JSON file
    with open(f"{output_path}stats.txt", 'w') as f:
        f.write("MAD-Community Statistics\n")
        f.write("=========================\n\n")

        f.write(f"Number of communities: {num_communities}\n")
        f.write(f"Number of questions: {len(response_stats)}\n\n")

        f.write(f"Agents Score: {stats['Agents_Score']}% correct\n")
        f.write("Community Scores\n")
        for i, score in stats['Community_Score']:
            f.write(f"\tCommunity {i+1}: {score}% correct\n")
        f.write(f"\n[Final Result] Judge Score: {stats['Judge_Score']}% correct\n\n")

    return