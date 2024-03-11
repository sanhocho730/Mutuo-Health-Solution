# # imports
# import mwclient  # for downloading example Wikipedia articles
# import mwparserfromhell  # for splitting Wikipedia articles into sections
# import openai  # for generating embeddings
# import os  # for environment variables
# import pandas as pd  # for DataFrames to store article sections and embeddings
# import re  # for cutting <ref> links out of Wikipedia articles
# import tiktoken  # for counting tokens

# AZURE_OPENAI_GPT_4_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_4_DEPLOYMENT')
# client = AzureOpenAI(
#     azure_endpoint=os.getenv('GPT_TEXT_ENDPOINT'),
#     api_key=os.getenv('GPT_TEXT_API_KEY'),
# )
