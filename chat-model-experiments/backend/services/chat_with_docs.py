from openai import OpenAI
import os

# MCQ Model

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)


def talk_to_llm(input_text, system_prompt, file_id=None, previous_response_id=None):
    print(f"Input text: {input_text}")
    
    # Prepare the request parameters
    request_params = {
        "model": "gpt-4.1",
        "previous_response_id": previous_response_id,
        "input": [
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
                        "file_id": file_id,
                    },
                    {
                        "type": "input_text",
                        "text": input_text,
                    },
                ]
            }
        ],
        "max_output_tokens": 1000
    }
     
    response = client.responses.create(**request_params)

    return response
