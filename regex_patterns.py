import re
# Precompile regex patterns
NON_ASCII_PATTERN = re.compile(r'[^\x00-\x7F]')
PARENTHESES_PATTERN = re.compile(r'[()]')
AMOUNT_PATTERN = re.compile(r'\bN?\d{1,3}(?:,\d{3})*(?:\.\d+)?\b')
PHONE_PATTERN = re.compile(r'\b0\d{10}\b')
ACCOUNT_PATTERN = re.compile(r'\b\d{10}\b')