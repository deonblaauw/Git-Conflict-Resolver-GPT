import subprocess
import os
import requests
import openai
import ollama  # Import the ollama package
import json
from utility.utils import fix_json_content, fix_json

# Default models for each service
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OPENAI_MODEL = "gpt-4o"

# Common file types to scan for merge conflicts
COMMON_FILE_TYPES = ['.py', '.js', '.java', '.cpp', '.html', '.css', '.php', '.rb', '.go', '.sh', '.txt']

# Function to display changes and resolution
def display_changes(conflict_text, resolved_text):
    print("\n--- Conflict Changes ---")
    print(conflict_text)
    print("\n--- Proposed Resolution ---")
    print(resolved_text)
    print("\n------------------------\n")

# Resolve the conflict using Ollama's LLM
def resolve_with_ollama(conflict_text, model=DEFAULT_OLLAMA_MODEL, additional_instructions=None):
    prompt = (
        "You are a code reviewer and need to resolve a Git merge conflict. "
        "Here are the conflicting changes with markers:\n\n"
        f"{conflict_text}\n\n"
        "Please merge the changes appropriately and provide a final version of the text that includes parts from both sides, "
        "removing the conflict markers and making it coherent.\n\n"
    )

    if additional_instructions:
        prompt += f"Additionally, here are the instructions to consider: {additional_instructions}\n\n"

    prompt += (
        "Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'output'.\n\n"
        "# Output\n"
        f'{{"output": "Here is the output of the merged files ..."}}'
    )

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    resolved_text = response.get("message", {}).get("content", "No content found in response.")

    try:
        json_start = resolved_text.index('{')
        json_content = resolved_text[json_start:]
        json_content = json_content.split('```')[0].strip()

        resolved_text_json = json.loads(json_content)
        return resolved_text_json.get("output", "No output found in JSON response.")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw content: {resolved_text}")
        return None

# Resolve the conflict using OpenAI's API
def resolve_with_openai(conflict_text, model=DEFAULT_OPENAI_MODEL, additional_instructions=None):
    prompt = (
        "You are a code reviewer and need to resolve a Git merge conflict. "
        "Here are the conflicting changes with markers:\n\n"
        f"{conflict_text}\n\n"
        "Please merge the changes appropriately and provide a final version of the text that includes parts from both sides, "
        "removing the conflict markers and making it coherent.\n\n"
    )

    if additional_instructions:
        prompt += f"Additionally, here are the instructions to consider: {additional_instructions}\n\n"

    prompt += (
        "Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'output'.\n\n"
        "# Output\n"
        f'{{"output": "Here is the output of the merged files ..."}}'
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    resolved_text = response['choices'][0]['message']['content']

    try:
        json_start = resolved_text.index('{')
        json_content = resolved_text[json_start:]
        json_content = json_content.split('```')[0].strip()

        resolved_text_json = json.loads(json_content)
        return resolved_text_json.get("output", "No output found in JSON response.")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw content: {resolved_text}")
        return None

# Choose which service to use for resolving conflicts
def resolve_conflict(conflict_text, service="ollama", model=None, additional_instructions=None):
    if service == "ollama":
        model = model or DEFAULT_OLLAMA_MODEL
        resolved_text = resolve_with_ollama(conflict_text, model, additional_instructions)
        if resolved_text:
            display_changes(conflict_text, resolved_text)
        return resolved_text
    elif service == "openai":
        model = model or DEFAULT_OPENAI_MODEL
        resolved_text = resolve_with_openai(conflict_text, model, additional_instructions)
        if resolved_text:
            display_changes(conflict_text, resolved_text)
        return resolved_text
    else:
        raise ValueError(f"Unknown service: {service}")

# Scan directory and subdirectories for files with merge conflicts, excluding the current script
def scan_for_merge_conflicts(directory, service, model):
    current_script = os.path.abspath(__file__)  # Get the full path of the current script

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Exclude the current script from being scanned
            if file_path == current_script:
                continue

            if any(file.endswith(ext) for ext in COMMON_FILE_TYPES):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    if '<<<<<<<' in content and '=======' in content and '>>>>>>>' in content:
                        print(f"\nFound merge conflict in: {file_path}")
                        resolved_text = resolve_conflict(content, service, model)
                        if resolved_text:
                            while True:
                                user_input = input("Do you want to apply this resolution? (yes to apply, enter additional instructions to modify, or exit to skip): ").strip().lower()
                                if user_input == 'yes':
                                    with open(file_path, 'w') as f:
                                        f.write(resolved_text)
                                    print(f"Resolved and applied merge conflict in: {file_path}")
                                    break
                                elif user_input == 'exit':
                                    print(f"Skipped merge conflict in: {file_path}")
                                    break
                                else:
                                    resolved_text = resolve_conflict(content, service, model, user_input)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

def main(service="openai", model=None):
    print("Using", service, "with model", model)
    scan_for_merge_conflicts(os.getcwd(), service, model)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resolve git conflicts using LLMs.")
    parser.add_argument("--service", choices=["ollama", "openai"], default="openai", help="Select the service to use (ollama or openai)")
    parser.add_argument("--model", help="Specify the model to use for conflict resolution")
    args = parser.parse_args()

    main(service=args.service, model=args.model)
