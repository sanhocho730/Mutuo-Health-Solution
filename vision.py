from dotenv import load_dotenv
from openai import AzureOpenAI
from pdf2image import convert_from_path

import argparse
import base64
import io
import logging
import os
import pickle

import PyPDF2


class PDFEncoder:
    """
    A class to encode a PDF file into different formats.
    Note that the page number is 0-indexed.
    """

    def __init__(self, path):
        self._path = path  # The path to the PDF file
        self._images = convert_from_path(path)  # A list of images of the PDF file

    def get_page_count(self):
        """Returns the number of pages in the PDF file."""
        return len(self._images)

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


class OpenAIRequestLibrary:
    """A library for generating request objects for OpenAI API."""

    _azure_openai_client = None  # The Azure OpenAI client

    def __init__(
        self, model='AZURE_OPENAI_GPT4_DEPLOYMENT', temperature=0, max_tokens=2000
    ):
        if self._azure_openai_client is None:
            self._init_openai_client()

        assert model in os.environ
        self._model = os.environ[model]
        self._temperature = temperature
        self._max_tokens = max_tokens

        self._request_body = {  # The request body to be sent to the OpenAI API
            'model': self._model,
            'temperature': self._temperature,
            'max_tokens': self._max_tokens,
        }

    def add_plain_message(self, role, content):
        """Adds a plain message to the request body."""
        if 'messages' not in self._request_body:
            self._request_body['messages'] = []  # Initialize the messages list
        self._request_body['messages'].append({'role': role, 'content': content})

    def add_image_message(self, text, image_url):
        """Adds an image message to the request body."""
        if 'messages' not in self._request_body:
            self._request_body['messages'] = []  # Initialize the messages list
        self._request_body['messages'].append(
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': text,
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': image_url,
                        },
                    },
                ],
            }
        )

    def send(self):
        """Sends the request to the OpenAI API."""
        response = self._azure_openai_client.chat.completions.create(
            **self._request_body
        )
        return response

    def __str__(self) -> str:
        return str(self._request_body)

    @classmethod
    def _init_openai_client(cls):
        cls._azure_openai_client = AzureOpenAI()


def parse_arguments():
    """
    Returns an argparse Namespace object that contains the parsing result of
    the command-line arguments.
    """

    # Define the command-line arguments and parse them
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input-form',
        required=True,
        help='The path to the PDF file to be filled out.',
    )
    parser.add_argument(
        '-e',
        '--emr-database',
        required=True,
        help='The path to the electrical medical record (EMR) file.',
    )
    parser.add_argument(
        '-o', '--output', required=True, help='The path to the output PDF file.'
    )
    # TODO: Set up logger to print debugging information.
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Prints debugging output.'
    )
    parser.add_argument(
        '-d',
        '--debug-dump',
        action='store_true',
        help='Dumps intermediate files for debugging.',
    )
    args = parser.parse_args()

    return args


def parse_pdf(file_path):
    """Parse the PDF file and extract the questions."""

    pdf = PDFEncoder(file_path)

    question_names = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        fields = reader.get_fields()
        for field_name, _ in fields.items():
            question_names.append(field_name)
    keys_string = '|'.join(question_names)

    # Iterate over all pages of the PDF
    parse_result = []  # List of parsed results for each page
    for page_number in range(pdf.get_page_count()):
        # Get the data URL encoding for the current page
        data_url = pdf.get_dataurl_encoding(page_number)
        # Formulate the prompt for the current page
        # TODO: Alternative prompt: 'Extract the all and only questions(free fields, multiple choices, check boxes, etx) as text from the picture, and generate a form with the first column as the question and the second column as the pixel location of the answer field of the question in the picture.'
        prompt = f"""Given the form content and the Question Names "{keys_string}": (seperated by "|"), 
        Extract all and only questions from the form content (free fields, multiple choices, checkboxes, etc.) as text from the picture. 
        For each item, provide the question text and match the most relevant question name. If there's no question name could be matched, use "NONAME"
        If there Place the  Use the following format:
        - For free field questions: "Question Names>> Question text "
        - For checkbox questions: "Question Names>> Question text | Checkbox options : ☐ Option 1 , ☐ Option 2 , ..."
        - For multiple-choice questions: "Question Names>> Question text | Choice options : Choice A , Choice B , ...
        Ensure accuracy and facilitating precise interaction with the form in a digital environment."
        """

        # Generate response using OpenAI based on the current page's content
        # Check if a cached response exists
        pickled_response_file = f'pickled_response_page_{page_number+1}.bin'
        if os.path.exists(pickled_response_file):
            with open(pickled_response_file, 'rb') as fin:
                response = pickle.load(fin)
        else:
            # If no cached response, send a new request and save it
            request = OpenAIRequestLibrary(temperature=0.3)
            request.add_image_message(prompt, data_url)
            response = request.send()
            with open(pickled_response_file, 'wb') as fout:
                pickle.dump(response, fout)

        # Process and display the response (example below may need adjustment)
        parse_result.append(response.choices[0].message.content)

    return keys_string, parse_result


def predict_answers(question_list, emr_database):
    """
    Predict the answers to the questions in the PDF file based on the EMR database.
    """

    questions = '\n'.join(question_list)

    query = f"""Use the below information to fill in the form. 
    The first line should be the question (leave the questions as original) and the second line shouble be the answers.
    There are three types of questions:
    1. Free field questions: These should be directly answered in the text.
    2. Checkbox questions: For checkbox questions(multiple), answer the question by checking the correct option(s). For single checkbox question, show me 'Yes' or 'No'
    3. Multiple choice questions: For these, write out the selected answers.
    If the information needed to answer a question is not provided, respond with "N/A" and ensure all original questions are included in your response.
    Given these instructions, fill in the answers based on the available information. Ensure to keep the original format of each question, particularly for checkbox options.
    Keep the answer format as this example: "Last name first in full>> Employee's Name (Last name first, in full): Smith, Jane"

    Article:
    \"\"\"
    {emr_database}
    \"\"\"

    Question:
    \"\"\"
    {questions}
    \"\"\"
    """
    request = OpenAIRequestLibrary(temperature=0.4)
    request.add_plain_message('system', 'You answer questions about a medical form.')
    request.add_plain_message('user', query)
    response = request.send()
    predict_result = response.choices[0].message.content

    return predict_result


def init():
    """
    Initialize the environment variables and configuration.
    """

    # Intialize the environment variables - Azure OpenAI credentials
    load_dotenv(override=True)


def main():
    """
    The entry point of the script.
    """

    # Parse the command-line arguments
    args = parse_arguments()

    # Set up the logger to print debugging information
    if args.verbose:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO
    logging.basicConfig(
        format='[%(filename)s:%(lineno)d:%(funcName)s()] %(message)s', level=log_lvl
    )

    logging.debug(f'Parsed arguments: {args}')

    # Initialize the environment variables and configuration
    init()

    # Parse the PDF file and extract the questions
    keys_string, parse_result = parse_pdf(args.input_form)

    # Read the EMR database
    with open(args.emr_database, 'r') as file:
        emr_database = file.read()

    # Predict the answers to the questions in the PDF file basd on the EMR database
    predict_result = predict_answers(parse_result, emr_database)

    # Save the predicted answers to a text file
    with open(args.output, 'w') as file:
        file.write(predict_result)


if __name__ == '__main__':
    #   Example usage:
    #       python vision.py -i test.pdf -e inputtest.txt -o output.pdf -v
    #       python vision.py -i input/form/short_term_disability.pdf -e input/emr/sample_emr.txt -o output.txt -v -d
    main()