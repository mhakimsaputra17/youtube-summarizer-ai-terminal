import os
from openai import OpenAI

token = ''
endpoint = "https://models.inference.ai.azure.com"
model_name = "o1-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    model=model_name
)

print(response.choices[0].message.content)