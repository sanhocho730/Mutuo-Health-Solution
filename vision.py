from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

AZURE_OPENAI_GPT4_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT4_DEPLOYMENT')

azure_openai_client = AzureOpenAI()

kwargs = {
    'model': AZURE_OPENAI_GPT4_DEPLOYMENT,
    'temperature': 0,
    'max_tokens': 2000,
    'messages': [
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Describe this picture:'},
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg'
                    },
                },
            ],
        }
    ],
}

response = azure_openai_client.chat.completions.create(**kwargs)

print(response)
