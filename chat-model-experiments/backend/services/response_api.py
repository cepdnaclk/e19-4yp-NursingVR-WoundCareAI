from openai import OpenAI
import os

#  history taking model

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)

def talk_to_llm(previous_response_id=None, input_text="" , system_prompt=""):

    response = client.responses.create(
        model="gpt-4.1",
        previous_response_id=previous_response_id,
        input=[{"role":"system", "content": system_prompt},{"role": "user", "content": input_text}],
        max_output_tokens=100
    )

    return response

