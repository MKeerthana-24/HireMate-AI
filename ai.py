import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200,     
        temperature=0.7
    )


    return response.choices[0].message.content

def generate_questions(topic, count=10):
    prompt = f"""
You are a senior technical interviewer.

Generate exactly {count} UNIQUE interview questions.

Topic: {topic}

Candidate:
Final Year Computer Science Student

Rules:
1. Return ONLY the questions.
2. Number them from 1 to {count}.
3. Do not provide answers.
4. Questions should gradually increase in difficulty.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=600,
        temperature=0.8
    )

    return response.choices[0].message.content
def evaluate_answer(question, answer):

    prompt = f"""
You are an experienced technical interviewer.

Interview Question:
{question}

Student Answer:
{answer}

Evaluate the student's answer.

Respond EXACTLY in this format:

Score: X/10

Strengths:
- Point 1
- Point 2

Weaknesses:
- Point 1
- Point 2

Suggestion:
One short paragraph explaining how the student can improve.

Do not ask another question.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300,
        temperature=0.5
    )

    return response.choices[0].message.content
def evaluate_interview(questions_answers):

    prompt = f"""
You are a professional technical interviewer.

Below is the complete interview.

{questions_answers}

Evaluate the candidate.

Return exactly in this format:

Overall Score: X/10

Strengths:
- Point 1
- Point 2

Weaknesses:
- Point 1
- Point 2

Suggestions:
One short paragraph explaining how the candidate can improve.
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=500,
        temperature=0.5
    )

    return response.choices[0].message.content