from num2words import num2words
from words_replacement import  STATIC_REPLACEMENTS
from regex_patterns import *
import logging

# =========================
# Logging Setup
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("")


def convert_amount(match):
    amount_str = match.group()
    if amount_str.startswith('N') or amount_str.startswith('#') :
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
    if kobo > 0:
        kobo_words = num2words(kobo, lang='en').replace('-', ' ')
        return f"{naira_words} naira and {kobo_words} kobo"
    return f"{naira_words}"

def format_number(match):
    return ' '.join(match.group())

def process_string(input_string):
    try:
        # print(f"Input string : {input_string}")
        logger.info(f"Input string : {input_string}")
        # Apply static replacements
        for old, new in STATIC_REPLACEMENTS.items():
            input_string = input_string.replace(old, new)    
        # Remove non-ASCII characters
        input_string = NON_ASCII_PATTERN.sub('', input_string)
        # Remove parentheses
        input_string = PARENTHESES_PATTERN.sub('', input_string)
        # Convert amounts to words
        input_string = AMOUNT_PATTERN.sub(convert_amount, input_string)
        # Format phone and account numbers
        input_string = PHONE_PATTERN.sub(format_number, input_string)
        input_string = ACCOUNT_PATTERN.sub(format_number, input_string)
        input_string = input_string.replace("#", "")
        # print(f"Processed string : {input_string}")
        logger.info(f"Processed string : {input_string}")
        logger.info("Sucessfully processed text for audio synthesis")
        # return input_string.lower()
        return input_string
    except Exception as e:
        logger.error(f"Error while processing text : {e}")
