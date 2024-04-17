import PyPDF2
from fillpdf import fillpdfs
import argparse


def get_field_options(reader, field_info):
    options = []
    kids = field_info.get('/Kids')
    if kids:
        for kid in kids:
            kid_object = reader.get_object(kid)
            if kid_object:
                ap = kid_object.get('/AP')
                if ap:
                    if isinstance(ap, PyPDF2.generic.IndirectObject):
                        ap = reader.get_object(ap)
                    if '/N' in ap:
                        key=[k for k in list(ap['/N'].keys()) if k!='/Off']
                        options.extend(key)
                
    return options if options else None

def main(input_pdf_path):
    output_pdf_path = 'answered.pdf'
    answered_questions_txt_path = "answered_questions.txt"
    data_dict = {}
    temp_dict = {}

    # Open the file in read mode
    with open(answered_questions_txt_path, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            part_name = line.strip().split('>>')[0]
            #get the question field name.
            part_answer = line.strip().split(':')[-1]
            #get the question answer
            temp_dict[part_name] = part_answer


    with open(input_pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        fields = reader.get_fields()

        for field_name, field_info in fields.items():
            field_type = field_info.get('/FT')
            if field_name in temp_dict:
                if field_type == '/Tx':  # Text field
                    data_dict[field_name] = temp_dict[field_name]
                elif field_type == '/Btn':  # Checkbox or radio button field
                    options = get_field_options(reader, field_info)
                    if options is not None and temp_dict[field_name] in options:
                        data_dict[field_name] = temp_dict[field_name]

    fillpdfs.write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict)


# python vison.py short_term_disability.pdf
if __name__ == '__main__':
    # Define the command-line arguments and parse them
    argparse = argparse.ArgumentParser()
    argparse.add_argument('input_pdf_path', help='The path to the PDF file.')
    args = argparse.parse_args()
    main(args.input_pdf_path)


#pip install pycryptodome for pdfs?
# for the PDF which encrypted using the AES algorithm?