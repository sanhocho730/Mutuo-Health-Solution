from dotenv import load_dotenv
from openai import AzureOpenAI
from pdf2image import convert_from_path

import argparse
import base64
import io
import os
import pickle


class PDFObject:
    """Represents a PDF file."""

    def __init__(self, path):
        self._path = path  # The path to the PDF file
        self._images = convert_from_path(path)  # A list of images of the PDF file

    def get_image_encoding(self, page_number):
        """Returns the image encoding of the page number."""
        jpg_bytes = io.BytesIO()
        self._images[page_number].save(jpg_bytes, 'JPEG')
        return jpg_bytes.getvalue()

    def get_base64_encoding(self, page_number):
        """Returns the base64 encoding of the page number."""
        return base64.b64encode(self.get_image_encoding(page_number))

    def get_dataurl_encoding(self, page_number):
        """Returns the data URL encoding of the page number."""
        # Construct the data URL by determining the MIME type and encoding the image
        mime_type = 'image/jpeg'
        base64_encoded_data = self.get_base64_encoding(page_number).decode('utf-8')
        return f'data:{mime_type};base64,{base64_encoded_data}'

    def get_dataurl_encoding_whole(self):
        """Returns the data URL encoding of all the pages."""
        pass

    def save_image_repr_to_file(self, page_number, path):
        """Saves the image representation of the page number to a file."""
        self._images[page_number].save(path, 'JPEG')

    def save_image_repr_to_directory(self, directory):
        """Saves the image representation of the PDF to a directory."""
        if not os.path.exists(directory):
            os.makedirs(directory)

        for i, image in enumerate(self._images):
            filename = f'{directory}/page_{i + 1}.jpg'
            image.save(filename, 'JPEG')


class OpenAILibrary:
    """OpenAI library functions used in this project."""

    def __init__(
        self, model='AZURE_OPENAI_GPT4_DEPLOYMENT', temperature=0, max_tokens=2000
    ):
        self._azure_openai_client = AzureOpenAI()
        self._model = model
        if model in os.environ:
            self._model = os.environ[model]
        self._temperature = temperature
        self._max_tokens = max_tokens

        self._request_template = {
            'model': self._model,
            'temperature': self._temperature,
            'max_tokens': self._max_tokens,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            # 'text' attribute is needed
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                # 'url' attribute is needed
                            },
                        },
                    ],
                }
            ],
        }

    def generate_response(self, text, image_url):
        """Generates a response based on the given text and image URL."""
        request = self._request_template
        request['messages'][0]['content'][0]['text'] = text
        request['messages'][0]['content'][1]['image_url']['url'] = image_url

        response = self._azure_openai_client.chat.completions.create(**request)

        return response


def main(pdf_path, output_folder):
    pdf = PDFObject(pdf_path)
    pdf.save_image_repr_to_directory(output_folder)

    openai_lib = OpenAILibrary()

    PICKLED_RESPONSE_FILE = 'pickled_response.bin'
    try:
        with open(PICKLED_RESPONSE_FILE, 'rb') as fin:
            response = pickle.load(fin)
    except FileNotFoundError:
        response = openai_lib.generate_response(
            'Extract the all and only questions(free fields, multiple choices, check boxes, etx) as text from the picture, and generate a form with the first column as the question and the second column as the pixel location of the answer field of the question in the picture.',
            pdf.get_dataurl_encoding(0),
        )
        with open(PICKLED_RESPONSE_FILE, 'wb') as fout:
            pickle.dump(response, fout)

    print(type(response.choices[0].message.content))
    print(response.choices[0].message.content)


# python vison.py test.py output
if __name__ == '__main__':
    # Define the command-line arguments and parse them
    argparse = argparse.ArgumentParser()
    argparse.add_argument('pdf_path', help='The path to the PDF file.')
    argparse.add_argument('output_folder', help='The path to the output folder.')
    args = argparse.parse_args()

    load_dotenv(override=True)

    main(args.pdf_path, args.output_folder)