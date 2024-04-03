from openai import AzureOpenAI
from dotenv import load_dotenv
import os
# from encode import local_image_to_data_url
# from convert import convert_all_pdfs_in_folder

# import pickle
# import ast  # for converting embeddings saved as strings back to arrays
# import pandas as pd  # for storing text and embeddings data

# import tiktoken  # for counting tokens
# from scipy import spatial  # for calculating vector similarities for search


def get_unanswered_questions(query, answered_text):
    """
    Uses GPT to identify unanswered questions from the initial response.
    """
    # Formulate a new prompt asking GPT to list unanswered questions.
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Given the initial query:\n\n{query}\n\nAnd the response:\n\n{answered_text}\n\nList any questions that were not answered, preserving the original format of each question."}
    ]

    # Make a new request to GPT with the updated prompt
    response = client.chat.completions.create(
        model=AZURE_OPENAI_TURBO_DEPLOYMENT,  # Ensure this variable is correctly defined
        messages=conversation,
        temperature=0
    )

    unanswered_questions_text = response.choices[0].message.content  # Adjust based on actual response structure
    return unanswered_questions_text


def generate_answers_from_conversation(conversation_path, unanswered_questions_path, answered_questions_path):
    """
    Generates answers for the unanswered questions based on the conversation provided.
    Reads the conversation and unanswered questions from their respective files, then
    generates answers using GPT and saves them to a specified file.
    
    :param conversation_path: Path to the file containing the conversation text.
    :param unanswered_questions_path: Path to the file containing the unanswered questions.
    :param answered_questions_path: Path to the file where the answered questions will be saved.
    """
    # Load the conversation text
    with open(conversation_path, 'r', encoding='utf-8') as file:
        conversation_text = file.read()
    
    # Load the unanswered questions
    with open(unanswered_questions_path, 'r', encoding='utf-8') as file:
        unanswered_questions = file.read()
    
    # Generate the prompt for GPT based on the conversation and unanswered questions
    prompt = f"{conversation_text}\n\nBased on the above conversation, please answer the following unanswered questions:\n\n{unanswered_questions}"
    
    # Use GPT to generate answers
    response = client.chat.completions.create(
        model=AZURE_OPENAI_TURBO_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of understanding detailed medical conversations and providing specific answers based on the context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5  # Adjust temperature if necessary to balance creativity and relevance
    )
    
    # Extract the GPT-generated answers
    try:
        answered_text = response.choices[0].message.content
    except AttributeError:
        answered_text = "Error: Could not generate answers based on the conversation."
    
    # Save the GPT-generated answers to a file
    with open(answered_questions_path, 'w', encoding='utf-8') as file:
        file.write(answered_text)

    print(f"Answers generated and saved to {answered_questions_path}")



# models
EMBEDDING_MODEL = 'text-embedding-ada-002'

load_dotenv(override=True)

# AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
client = AzureOpenAI(
    azure_endpoint=os.getenv('GPT_TEXT_ENDPOINT'),
    api_key=os.getenv('GPT_TEXT_API_KEY'),
)


# Read questions from response_page.txt


folder_path = '/Users/isanho/Desktop/Forms/images'

questions = ""

# Iterate through each text file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            # Read the content of the file
            content = file.read()
            # Append the content to the questions string
            questions += content + "\n\n"

# Print the extracted questions
print("Extracted questions:")
#print(questions)


curling = """

Patient Information:

Name: Jane Smith
DOB: 06/25/1982
Date: 03/04/2024

Subjective:

S1 Severe Carpal Tunnel Syndrome Management:

Patient has reported symptoms of carpal tunnel syndrome in the right wrist for approximately six months, with significant worsening in the last month. Diagnosis was confirmed via EMG and nerve conduction studies. Symptoms include numbness, tingling, pain, and difficulty with gripping objects.

S2 Treatment History:

Has been under conservative treatment, including wrist splinting, NSAIDs for pain relief, and corticosteroid injections without significant improvement. Considering surgical intervention due to the lack of response to conservative treatments.

S3 Work-related Impact:

Patient's ability to perform job-related tasks, especially typing and fine motor skills, has been significantly affected due to the condition.

S4 Past Medical History:

Patient has no significant past medical history unrelated to current condition. No known allergies to medications.

S5 Lifestyle and Occupational Information:

Patient works as a data entry specialist, which involves repetitive hand movements. Quit smoking 10 years ago, occasional alcohol consumption, no recreational drug use. Lives alone, enjoys walking as a form of exercise.

Objective:

Examination shows reduced grip strength in the right hand, positive Tinel's and Phalen's signs, and reduced sensation in the thumb, index, and middle fingers. No swelling or discoloration observed.

Assessment:

Severe carpal tunnel syndrome in the right wrist, significantly impacting patient's quality of life and ability to perform work-related tasks. Unable to perform repetitive hand movements or lift objects over 5 pounds with the right hand. Limited ability to type or write, significantly affecting the ability to perform job-related tasks.

Plan:

Surgical Intervention: Schedule carpal tunnel release surgery for 04/10/2024.
Post-Operative Care: Recommend physical therapy post-surgery to regain strength and functionality in the right wrist.
Work Modifications: Advise patient on seeking workplace modifications to reduce strain on the wrist post-recovery.
Follow-up: Arrange for a follow-up appointment 2 weeks post-surgery to monitor recovery progress.


"""

query = f"""Use the below information to answer the questions if possible.
There are 3 types of questions, free field, check box and multiple choices. The free field questions are those quesions followed by a long underline or there are no answer choices after the question. 
Answer the free field question in a new line. The check box questions are those questions followed by a check box. Answer the
check box questions with a correct mark or an x in the location of the answer check box. And the multiple choices are those 
questions followed by a list of choices or similar answers. Answer the multiple choice questions with the correct answer in a new line. 
If the answer of the question is not provided in the artcle, please answer with "N/A". Make sure to include all the original questions in the answer.
Even if there is no answer. 

Article:
\"\"\"
{curling}
\"\"\"

Question:
\"\"\"
{questions}
\"\"\"
"""

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about a medical form.'},
        {'role': 'user', 'content': query},
    ],
    model=AZURE_OPENAI_TURBO_DEPLOYMENT,
    temperature=0,
)

answered_questions_txt_path = '/Users/isanho/Desktop/autoscribe_forms_main/answered_questions.txt'
answered_text = response.choices[0].message.content
print("GPT's initial response:")
print(answered_text)

with open(answered_questions_txt_path, 'w', encoding='utf-8') as file:
        file.write(answered_text)


# Use GPT to list unanswered questions
print("\nUnanswered questions as identified by GPT:")
unanswered_questions_text = get_unanswered_questions(query, answered_text)
#print(unanswered_questions_text)


# Save the unanswered questions to a file
file_path = '/Users/isanho/Desktop/autoscribe_forms_main/unanswered_questions.txt'

with open(file_path, 'w', encoding='utf-8') as file:
    file.write('Follow-up Needed for Unanswered Questions:\n\n')
    file.write(unanswered_questions_text)

print(f'\nUnanswered questions have been saved to {file_path}')


