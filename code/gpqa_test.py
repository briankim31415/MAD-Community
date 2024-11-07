import pandas as pd
import random
import openai
import time
from tqdm import tqdm
from pydantic import BaseModel, Field



class AgentFormat(BaseModel):
    reason: str
    answer: int


# Read the CSV file
file_path = '../data/gpqa_dataset/gpqa_main.csv'
df = pd.read_csv(file_path)

client = openai.Client()

num_questions = 2

correct_count = 0
total_count = 0

question_col_idx = df.columns.get_loc("Question") + 1
correct_col_idx = df.columns.get_loc("Correct Answer") + 1
incorrect1_col_idx = df.columns.get_loc("Incorrect Answer 1") + 1
incorrect2_col_idx = df.columns.get_loc("Incorrect Answer 2") + 1
incorrect3_col_idx = df.columns.get_loc("Incorrect Answer 3") + 1
canary_col_idx = df.columns.get_loc("Canary String") + 1


rand = df.head(num_questions)
for row in tqdm(rand.itertuples(), desc="Processing", total=len(rand), ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
    question = row[question_col_idx]
    choices = [row[correct_col_idx], row[incorrect1_col_idx], row[incorrect2_col_idx], row[incorrect3_col_idx]]
    random.shuffle(choices)
    correct_idx = choices.index(row[correct_col_idx])
    question_id = row[canary_col_idx]

    prompt = question + ("\n\n" + "\n".join([f"{i+1}. {choice}" for i, choice in enumerate(choices)]))

    tries = 0
    while True:
        if tries >= 5:
            print(f"Skipping question: {question_id}")
            break

        time.sleep(0.5)
        try:
            tries += 1
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format=AgentFormat
            )
            output = response.choices[0].message
            answer = output.parsed.answer
            if 1 <= answer <= 4:
                total_count += 1
                if answer == correct_idx + 1:
                    correct_count += 1
                break
        except Exception as e:
            print(f"Try number: {tries} >> {e}")
            continue

print(f"\n\nCorrect count: {correct_count}  ||  Total count: {total_count}")