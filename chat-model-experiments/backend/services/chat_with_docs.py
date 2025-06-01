from openai import OpenAI
import os

# MCQ Model

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)

system_prompt = '''You are a helpful assistant evaluate answers to multiple-choice questions (MCQs) in a medical 
context. When the user's answer and the question number is given to you, You should provide a detailed feedback about
the user's choice. Imagine the knowledge given in the pdf is your own knowledge as an assistant. 
Limit your respinse to 50 words maximum.
'''

def talk_to_llm(input_text):
    print(f"Input text: {input_text}")
    response = client.responses.create(
    model="gpt-4.1",
    input= [
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": system_prompt
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": "file-UTGTAsAD4G9XSfAasxYqRj",
                },
                {
                    "type": "input_text",
                    "text": input_text,
                },
            ]
        }
    ],
    max_output_tokens=100)

    return response
