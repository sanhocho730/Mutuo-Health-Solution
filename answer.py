import argparse
import os
import time

from openai import AzureOpenAI
from dotenv import load_dotenv

def read_file(file_path):
    """Utility function to read file content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    """Utility function to write content to file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def get_unanswered_questions(client, model, answered_text):
    """Uses GPT to identify unanswered questions from the initial responses."""
    prompt = f"Given the answered text, identify any questions that remain unanswered,preserving the original format of each question.:\n\n{answered_text}"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content






def update_answered_questions(client, model, original_path, new_answers_text):
    """
    Updates the original answered questions file with newly generated answers,
    effectively replacing questions that were previously unanswered.


    """

    # Example logic for updating the original content with new answers
    # This part needs to be customized based on how your questions and answers are structured
    original_content = read_file(original_path)

    prompt = (
        "Here are the existing answers to some questions:\n\n"
        f"{original_content}\n\n"
        "And here are new answers generated based on a recent conversation:\n\n"
        f"{new_answers_text}\n\n"
        "Please update the existing answers with the new information, replacing any unanswered "
        "questions with their new answers and leaving already answered questions as they are."
        "Keep the answer format as this example: \"Last name first in full>> Employee's Name (Last name first, in full): Smith, Jane\""
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of merging document contents intelligently."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    updated_content = response.choices[0].message.content
    

    return updated_content

def generate_answers_from_conversation(client, model, conversation_text, unanswered_questions):
    """
    Generates answers for the unanswered questions based on the conversation provided.
    Reads the conversation and unanswered questions from their respective files, then
    generates answers using GPT and saves them to a specified file.

    """
    # Load the conversation text

    # Generate the prompt for GPT based on the conversation and unanswered questions
    prompt = (
        f"Use the below information to fill in the form. There are three types of questions:"
        f"1. Free field questions: These should be directly answered in the text."
        f"2. Checkbox questions: For checkbox questions, answer the question by showing the correct option(s). For single checkbox question, show me 'Yes' or 'No'"
        f"3. Multiple choice questions: For these, write out the selected answers."
        f"If the information needed to answer a question is not provided, respond with \"N/A\" and ensure all original questions are included in your response."
        f"Based on the above instructions and the following conversation, please answer the unanswered questions:\n\n"
        f"Keep the answer format as this example: \"Last name first in full>> Employee's Name (Last name first, in full): Smith, Jane\""
        f"Conversation:\n{conversation_text}\n\n"
        f"Unanswered Questions:\n{unanswered_questions}"
    )
    
    # Use GPT to generate answers
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of understanding detailed medical conversations and providing specific answers based on the context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4  # Adjust temperature if necessary to balance creativity and relevance
    )
    
    # Extract the GPT-generated answers
    try:
        answered_text = response.choices[0].message.content
    except AttributeError:
        answered_text = "Error: Could not generate answers based on the conversation."
    
    # Save the GPT-generated answers to a file
    #with open(unanswered_questions_path, 'w', encoding='utf-8') as file:
    #    file.write(answered_text)

    print(f"Answers generated")

    return answered_text



def main():
    """Main function to orchestrate the processing of answers based on conversations."""
    parser = argparse.ArgumentParser(description="Generate and integrate answers based on previous responses and conversations.")
    parser.add_argument('output_txt_path', help='Path to the file containing initial responses (output.txt)')
    parser.add_argument('conversation_txt_path', help='Path to the conversation text file (conversation.txt)')
    parser.add_argument('final_output_path', help='Path to save the final integrated answers')
    args = parser.parse_args()

    EMBEDDING_MODEL = 'text-embedding-ada-002'

    load_dotenv(override=True)


    client = AzureOpenAI(
        azure_endpoint=os.getenv('GPT_TEXT_ENDPOINT'),
        api_key=os.getenv('GPT_TEXT_API_KEY'),
    )

    model = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')

    # Step 1: Extract unanswered questions from the initial responses
    start_time = time.time()
    answered_text = read_file(args.output_txt_path)
    unanswered_questions = get_unanswered_questions(client, model, answered_text)
    step1_time = time.time() - start_time
    print(f"Time taken for extracting unanswered questions: {step1_time:.2f} seconds")


    # Step 2: Generate answers using the detailed conversation
    start_time = time.time()
    conversation_text = read_file(args.conversation_txt_path)
    generated_answers = generate_answers_from_conversation(client, model,conversation_text, unanswered_questions)
    step2_time = time.time() - start_time
    print(f"Time taken for generating answers: {step2_time:.2f} seconds")

    # Step 3: Update answers and make final output
    start_time = time.time()
    new_answers = update_answered_questions(client, model, args.output_txt_path, generated_answers)
    write_file(args.final_output_path, new_answers)
    step3_time = time.time() - start_time
    print(f"Time taken for updating answers: {step3_time:.2f} seconds")


    print(f"Final answers have been saved to {args.final_output_path}")

if __name__ == '__main__':

    #example
    #python answer.py output.txt input/emr/conversation.txt final_output.txt
    main()
