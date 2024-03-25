from dotenv import load_dotenv
from openai import AzureOpenAI
from pdf2image import convert_from_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    # Initialize the PDF object and OpenAI library instance
    pdf = PDFObject(pdf_path)
    openai_lib = OpenAILibrary()

    # Convert and save all PDF pages as images in the specified directory
    pdf.save_image_repr_to_directory(output_folder)
    all_questions_and_locations = []

    # Iterate over all pages of the PDF
    for page_number in range(len(pdf._images)):
        # Get the data URL encoding for the current page
        data_url = pdf.get_dataurl_encoding(page_number)
        # Formulate the prompt for the current page
        prompt = '''Given the form content, identify and categorize all items as either free field questions, checkbox questions, or multiple-choice questions. For each item, provide the question text and specify the central pixel location of the answer field. Use the following format:
        - For free field questions: "Question text | Central pixel location: (x, y)"
        - For checkbox questions: "Question text | Checkbox options with pixel locations: ☐ Option 1 (x1, y1), ☐ Option 2 (x2, y2), ..."
        - For multiple-choice questions: "Question text | Choice options with pixel locations: Choice A (xA, yA), Choice B (xB, yB), ..."
        Ensure accuracy in identifying the pixel location of the answer field for each type of question, facilitating precise interaction with the form in a digital environment.'''

        # Generate response using OpenAI based on the current page's content
        try:
            # Check if a cached response exists
            pickled_response_file = f'pickled_response_page_{page_number+1}.bin'
            if os.path.exists(pickled_response_file):
                with open(pickled_response_file, 'rb') as fin:
                    response = pickle.load(fin)
            else:
                # If no cached response, send a new request and save it
                response = openai_lib.generate_response(prompt, data_url)
                with open(pickled_response_file, 'wb') as fout:
                    pickle.dump(response, fout)

            # Process and display the response (example below may need adjustment)
            print(f"Page {page_number+1}:")
            print(type(response.choices[0].message.content))
            print(response.choices[0].message.content)

            response_text_file = f'{output_folder}/response_page_{page_number+1}.txt'
            with open(response_text_file, 'w', encoding='utf-8') as file:
                file.write(response.choices[0].message.content)
                print(f"Response for page {page_number+1} saved to {response_text_file}")

        except Exception as e:
            print(f"Error processing page {page_number+1}: {e}")
    
    output_pdf_path = os.path.join(output_folder, "formatted_questions.pdf")


# python vison.py test.py output
if __name__ == '__main__':
    # Define the command-line arguments and parse them
    argparse = argparse.ArgumentParser()
    argparse.add_argument('pdf_path', help='The path to the PDF file.')
    argparse.add_argument('output_folder', help='The path to the output folder.')
    args = argparse.parse_args()

    load_dotenv(override=True)

    main(args.pdf_path, args.output_folder)