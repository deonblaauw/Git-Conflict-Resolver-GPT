import re
import json

def fix_json(json_str):
    # Escape backslashes that are not already escaped
    json_str = re.sub(r'(?<!\\)\\(?![\\"])', r"\\\\", json_str)  # Only escape lone backslashes
    
    # Remove trailing commas in JSON arrays and objects
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    return json_str

def fix_json_content(content):
    # Fix improperly formatted strings, handling cases where single quotes should be preserved
    content = re.sub(r'(\w)"(\w)', r'\1\'\2', content)  # Fix "word"s" to "word's"
    
    # Replace stray single quotes with double quotes in keys/values
    content = re.sub(r'(?<=[:,\s])\'(?=\w+\'?\s*[:,\]])', '"', content)  # Replace single quotes in keys/values
    
    return content

def fix_quotes(content):
    # Ensure all quotes are correctly formatted around JSON keys/values
    content = re.sub(r'(?<=[:,\s])\'(?=\w+\'?\s*[:,\]])', '"', content)
    return content