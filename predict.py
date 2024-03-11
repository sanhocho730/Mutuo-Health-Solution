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


def list_unanswered_questions(query, response_text):
    # Split the query and response into lines for easier processing
    query_lines = query.split('\n')
    response_lines = response_text.split('\n')

    unanswered_questions = []

    for line in query_lines:
        if line.startswith('Question:') or '□' in line or '__' in line:
            question = line.strip()

            # Check if the question appears in the response with an answer other than N/A
            answered = any(
                question in response_line and 'N/A' not in response_line
                for response_line in response_lines
            )

            # If the question does not seem to be answered, add it to the list
            if not answered:
                unanswered_questions.append(question)

    return unanswered_questions

# models
EMBEDDING_MODEL = 'text-embedding-ada-002'

load_dotenv(override=True)

# AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
AZURE_OPENAI_TURBO_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_TURBO_DEPLOYMENT')
client = AzureOpenAI(
    azure_endpoint=os.getenv('GPT_TEXT_ENDPOINT'),
    api_key=os.getenv('GPT_TEXT_API_KEY'),
)

# text copied and pasted from: https://en.wikipedia.org/wiki/Curling_at_the_2022_Winter_Olympics
# I didn't bother to format or clean the text, but GPT will still understand it
# the entire article is too long for gpt-3.5-turbo, so I only included the top few sections

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

Question: <class 'str'>
Treatment
If hospitalized, name of the hospital/institution ______________ from ________ to ________
Surgery
□ Yes □ No (If yes, state surgical procedure) _______________________________________
□ Performed □ Planned Date of Surgery ______________ Anesthetic □ Local □ General
List medications currently prescribed and dosage _______________________________________
Therapy
□ Yes □ No If yes, indicate type (e.g. physiotherapy, psychotherapy, etc.) ________________
Frequency □ Daily _______ x per week □ Other ___________________________________
Location: □ Outpatient □ Therapist’s Office □ Physician’s Office □ Home
Summary of patient’s response to treatment ___________________________________________

Prognosis
Have you discussed a Return to Work Plan with your patient? □ Yes □ No
If no, why not? __________________________________________________________________
If yes, please provide details about the Return to Work Plan including recommendations for modified hours and/or modified duties: _________________________________________________________
______________________________________________________________________________
Expected date of Return to Work Full-Time __________ Next appointment __________
<class 'str'>
Employee Name:

If employee cannot return to full duties, can the employee return to work on modified duties: Yes No Date

If yes, please describe the employee's current limitations (please use the abilities section if applicable) If NO, please provide the medical contraindications to a modified return to work:

Expected length of time modifications will be required:

Is this injury or illness work related: Yes No Has a Form 8 been submitted to WSIB? Yes No

If disability is related to pregnancy, please indicate the expected date of delivery Day Month Year

I see the patient every (day, week, etc.) Date of most recent examination Day Month Year

Has patient ever had a similar condition? Yes No If yes, state when and describe:

FUNCTIONAL ABILITIES:
Walking (continuously): Up to 30 min; Up to 1 hour; No restriction; Other (e.g. uneven ground)
Standing (continuously): Up to 30 min; Up to 1 hour; No restriction; Other
Sitting (continuously): Up to 30 min; Up to 1 hour; No restriction; Other
Lifting floor to waist: Up to 20 lbs; Up to 30 lbs; Up to 40 lbs; No restriction; Other
Lifting waist to shoulder: Up to 20 lbs; Up to 30 lbs; Up to 40 lbs; No restriction; Other
Stair climbing: unable 2 – 3 steps only; down pace assisted no restriction
Able to drive: Up to 2 hours Up to 4 hours; No restriction Other
Able to operate heavy machinery: Up to 2 hours Up to 4 hours No restriction Other

Employee is: Left handed Right handed Ambidextrous
Limited ability to used left hand to: hold objects; grip; type; Write
Limited ability to used right hand to: hold objects; grip; type; Write
Completely unable to use left hand to: hold objects; grip; type; Write
Completely unable to use right hand to: hold objects; grip; type; Write
Hours per day: Full Hours Partial Hours (specify) anticipated duration no restriction

COGNITIVE ABILITIES:
Deadline Pressures: limited capacity Unable to perform No restriction; Other:
Attention limited capacity Unable to perform No restriction; Other:
Memory limited capacity Unable to perform No restriction; Other:
Reasoning limited capacity Unable to perform No restriction; Other:
Problem Solving: limited capacity Unable to perform No restriction; Other:
Other clinically assessed limitations:

If Nature of condition is Psychological/Mental Health, please advise if criteria for ICD -10- CM/ DSM 5 was evaluated: Yes No
<class 'str'>
Employee's Name
Address
Date of Birth
Language
I have access to a printer and am able to print all required medical forms
Email Address:
Check ONE
Were you hospitalized?
If YES, name of the hospital/institution
Are you claiming or receiving any other disability, wage loss and/or retirement benefits (e.g. WSIB, CPP/QPP, auto insurance, other)?
Are you working or volunteering in any capacity?
Are you receiving wages from any source?
Are you attending any educational course, program or institution?
If yes to any of the above, please provide details of these items on a separate page and include any confirming documents, claim numbers, etc.
If an accident caused your disability, indicate date WHERE and WHAT happened

Nature of the illness or injury:
Date illness or injury began:
Date of examination by Physician:
Date deemed totally disabled from work:
Is there a medical treatment plan currently in place?
Is the employee compliant with the prescribed/recommended treatment plan?
"""

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about a medical form.'},
        {'role': 'user', 'content': query},
    ],
    model=AZURE_OPENAI_TURBO_DEPLOYMENT,
    temperature=0,
)

print(response.choices[0].message.content)



# Assuming 'query' is your original query string and 'response_text' is the text received from GPT
unanswered_questions = list_unanswered_questions(
    query, response.choices[0].message.content
)


file_path = '/Users/isanho/Desktop/autoscribe_forms_main/unanswered_questions.txt'

with open(file_path, 'w', encoding='utf-8') as file:
    file.write('Follow-up Needed for Unanswered Questions:\n')
    for question in unanswered_questions:
        file.write(question + '\n')

print(f'Unanswered questions have been saved to {file_path}')

