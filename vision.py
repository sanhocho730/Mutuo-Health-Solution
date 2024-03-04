from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import os
import glob
from encode import local_image_to_data_url
from convert import convert_all_pdfs_in_folder
# import pickle

load_dotenv(override=True)

AZURE_OPENAI_GPT4_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT4_DEPLOYMENT')

azure_openai_client = AzureOpenAI()

pdf_folder_path = '/Users/mikewang/Desktop/Mutuo/forms/pdfs'
image_folder_path = '/Users/mikewang/Desktop/Mutuo/forms/images'
convert_all_pdfs_in_folder(pdf_folder_path, image_folder_path)

image_paths = glob.glob(os.path.join(image_folder_path, '*.jpg'))

for image_path in image_paths:
    data_url = local_image_to_data_url(image_path)
    base_filename = os.path.basename(image_path).replace('.jpg', '')
    PICKLED_RESPONSE_FILE = f'pickled_response_{base_filename}.bin'

    kwargs = {
        'model': AZURE_OPENAI_GPT4_DEPLOYMENT,
        'temperature': 0,
        'max_tokens': 2000,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Extract the all and only questions(free fields, multiple choices, check boxes, etx) as text from the picture:',
                    },
                    {
                        'type': 'image_url',
                        'image_url': {'url': data_url},
                    },
                ],
            }
        ],
    }

    # try:
    #     with open(PICKLED_RESPONSE_FILE, 'rb') as fin:
    #         response = pickle.load(fin)
    #         # print(response)
    # except FileNotFoundError:
    #     response = azure_openai_client.chat.completions.create(**kwargs)
    #     with open(PICKLED_RESPONSE_FILE, 'wb') as fout:
    #         pickle.dump(response, fout)

    # x = response.choices[0]
    # print(x.content_filter_results)

    # print(json.dumps(json.loads(response.model_dump_json()), indent=4))

    response = azure_openai_client.chat.completions.create(**kwargs)
    response_json = json.loads(response.model_dump_json())

    # print(type(response.choices[0].message.content))
    # print(response.choices[0].message.content)

    print(type(response_json['choices'][0]['message']['content']))
    print(response_json['choices'][0]['message']['content'])


# https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg
# https://www.bths.edu/ourpages/auto/2022/5/12/37181053/Medical%20Example.jpg?rnd=1652382511755
