from openai import AzureOpenAI
from dotenv import load_dotenv
import os

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
    prompt = (
        f"Use the below information to answer the questions if possible.\n"
        f"There are 3 types of questions, free field, check box, and multiple choices. "
        f"The free field questions are those questions followed by a long underline or there are no answer choices after the question. "
        f"Answer the free field question in a new line. "
        f"The check box questions are those questions followed by a check box. "
        f"Answer the check box questions with a correct mark or an x in the location of the answer check box. "
        f"And the multiple choices are those questions followed by a list of choices or similar answers. "
        f"Answer the multiple choice questions with the correct answer in a new line. "
        f"If the answer of the question is not provided in the article, please answer with \"N/A\". "
        f"Make sure to include all the original questions in the answer. Even if there is no answer. \n\n"
        f"Based on the above instructions and the following conversation, please answer the unanswered questions:\n\n"
        f"Conversation:\n{conversation_text}\n\n"
        f"Unanswered Questions:\n{unanswered_questions}"
    )
    
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


EMBEDDING_MODEL = 'text-embedding-ada-002'

load_dotenv(override=True)

# AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
client = AzureOpenAI(
    azure_endpoint=os.getenv('GPT_TEXT_ENDPOINT'),
    api_key=os.getenv('GPT_TEXT_API_KEY'),
)


conversation_txt_path = '/Users/isanho/Desktop/autoscribe_forms_main/conversation.txt'
answered_questions_txt_path = '/Users/isanho/Desktop/autoscribe_forms_main/answered_questions.txt'
file_path = '/Users/isanho/Desktop/autoscribe_forms_main/unanswered_questions.txt'

#Try to answer unanswered questions
generate_answers_from_conversation(conversation_txt_path, file_path, answered_questions_txt_path)