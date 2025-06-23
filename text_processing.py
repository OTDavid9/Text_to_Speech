import re
from num2words import num2words
from dotenv import load_dotenv
import os
from openai import OpenAI
from system_prompt import system_prompt
import logging

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")


def process_string(input_string):
    # Step 1: Replace 'ALAT' with 'Alat'
    processed_string = input_string.replace('ALAT', 'Alat')

    processed_string = processed_string.replace('NGN', '')   

    processed_string = processed_string.replace('*', '')   

    processed_string = processed_string.replace('PIN', 'pin')   
    processed_string = processed_string.replace('MTN', 'M T n') 


    # processed_string = processed_string.replace('N', '') 


    # Remove all non-ASCII characters (emojis and foreign symbols)
    processed_string = ''.join(char for char in processed_string if ord(char) < 128)

    # Step 2: Remove all parentheses
    processed_string = processed_string.replace('(', '').replace(')', '')

    # Step 3: Convert amounts (with or without 'N') to words
    def convert_amount(match):
        amount_str = match.group()
        if amount_str.startswith('N'):
            amount_str = amount_str[1:]
        amount_str = amount_str.replace(',', '')

        if '.' in amount_str:
            naira, kobo = amount_str.split('.')
            naira = int(naira)
            kobo = int(kobo)
        else:
            naira = int(amount_str)
            kobo = 0

        naira_words = num2words(naira, lang='en').replace('-', ' ')
        # naira_words += ' naira'


        if kobo > 0:
            kobo_words = num2words(kobo, lang='en').replace('-', ' ')
            return f"{naira_words} and {kobo_words} kobo"
        else:
            return f"{naira_words}"

    # Match amounts: N25000.50, 25,000.50, N25000, 25000
    processed_string = re.sub(r'\bN?\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', lambda m: convert_amount(m), processed_string)

    # Step 4: Format phone numbers (11 digits starting with 0)
    def format_number(match):
        num = match.group()
        return ' '.join(num)

    # Hyphenate phone numbers
    processed_string = re.sub(r'\b0\d{10}\b', format_number, processed_string)

    # Hyphenate account numbers (10 digits)
    processed_string = re.sub(r'\b\d{10}\b', format_number, processed_string)
    processed_string  = processed_string.lower()

    logging.info(f"kkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
    

    return processed_string


# client = OpenAI(
#     base_url= OLLAMA_BASE_URL,
#     api_key= OPENAI_API_KEY,  # Still required, even if ignored by backend
# )


# def llm_text_preprocessor(prompt:str = "Hi ALAT, ALAT. Send N11,000.50 to 0176543793 or call 07069779200")-> str:

#     # prompt = 'Hello'

#     Conversation = [

#     {"role": "system", "content": system_prompt},
#     {"role": "user", "content": prompt} ]

    

#     response = client.chat.completions.create(
#             messages=Conversation,
#             model=MODEL_NAME,
#             temperature=0.9
#         )
    
#     message = response.choices[0].message
#     response_content = message.content.strip() if message.content else ""
#     clean_response = response_content.replace("<think>\n\n</think>", "").strip()
#     print(clean_response)

#     return clean_response

# llm_text_preprocessor()
