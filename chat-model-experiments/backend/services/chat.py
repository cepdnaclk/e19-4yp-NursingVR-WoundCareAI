from openai import OpenAI
import os

API_KEY = os.environ.get("OPENAI_API_KEY")    

client = OpenAI(
    api_key=API_KEY,
)

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": "file-EBvboLPZgLs2EE3i1agkj6",
                },
                {
                    "type": "input_text",
                    "text": "What is the first dragon in the book?",
                },
            ]
        }
    ]
)

print(response.output_text)