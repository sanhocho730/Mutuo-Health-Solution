from pdf2image import convert_from_path
import os


def convert_pdf_to_jpg(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_filename = os.path.basename(pdf_path).replace('.pdf', '')

    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        filename = f'{output_folder}/{base_filename}_page_{i + 1}.jpg'
        image.save(filename, 'JPEG')


def convert_all_pdfs_in_folder(folder_path, output_folder):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            convert_pdf_to_jpg(pdf_path, output_folder)
