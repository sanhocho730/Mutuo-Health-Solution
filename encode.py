import base64
from mimetypes import guess_type


# Function to encode a local image into data URL
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, 'rb') as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f'data:{mime_type};base64,{base64_encoded_data}'


# Example usage
image_path = '/Users/mikewang/Desktop/Screenshot 2024-02-15 at 10.19.32 PM.png'
data_url = local_image_to_data_url(image_path)
# print("Data URL:", data_url)
