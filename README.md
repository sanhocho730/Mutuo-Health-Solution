# Getting Started

1. Clone the repo
2. Create a new python virtual env (python version 3.11.3) and activate it
3. Run `pip install -r requirements.txt`
4. Run `pre-commit install`
5. Run `brew install poppler`
6. Add shared .env variables to .env file
7. Run with `python vision.py`
8. Run with python vision.py -i test.pdf -e inputtest.txt -o output.pdf -v example: python vision.py -i input/form/short_term_disability.pdf -e input/emr/sample_emr.txt -o output.txt -v -d. (use --help for options). This will extract the questions from the pdf form as txt and predict some answers based on the EMR data, and the questions cannot be answered will be marked as N/A.
9. Run with python answer.py input_pdf output.txt conversation.txt final_output.txt example: python answer.py input/form/disability.pdf output.txt input/emr/conversation.txt final_output.txt. This will take in the output of vision and generate an unasnwered question list, then it uses the conversation/autoscribe data to generate the final answered question list then fill the answered into pdf form.
