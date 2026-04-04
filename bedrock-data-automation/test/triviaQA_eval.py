''' 
To evaluate the performance of an LLM, we will use a 
technique called normalized match. This involves comparing 
the model's response to the correct answer by normalizing 
both texts. 
'''
import csv
import re
from openai import OpenAI

with open("triviaqa.csv") as f:
    qa_pairs = list(csv.DictReader(f))

# Initialize the OpenAI client
client = OpenAI()

# removes all non-alphanumeric characters and converts the text to lowercase. 
# This ensures that the comparison between the model's response and the correct 
# answer is fair and consistent.
def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

correct = 0
for q in qa_pairs:
    prompt = f"Answer the following question with a short and direct fact:\n\n{q['question']}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content.strip()

    if normalize(q['answer']) == normalize(response):
        correct += 1