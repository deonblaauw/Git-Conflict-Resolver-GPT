import subprocess
import os
import requests
import openai

# Default models for each service
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OPENAI_MODEL = "gpt-4o"

# Detect Git conflicts
def get_conflict_files():
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True)
    conflict_files = result.stdout.splitlines()
    return conflict_files

# Parse conflict markers in a file
def extract_conflicts(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    if '<<<<<<<' in content and '>>>>>>>' in content:
        return content
    return None

# Resolve the conflict using Ollama's LLM
def resolve_with_ollama(conflict_text, model=DEFAULT_OLLAMA_MODEL):
    url = f"http://localhost:11434/models/{model}/resolve"
    payload = {"prompt": conflict_text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()['text']
    else:
        raise Exception(f"Error resolving with Ollama: {response.status_code} {response.text}")

# Resolve the conflict using OpenAI's LLM
def resolve_with_openai(conflict_text, model=DEFAULT_OPENAI_MODEL):
    response = openai.Completion.create(
        engine=model,
        prompt=conflict_text,
        max_tokens=1500
    )
    return response.choices[0].text.strip()

# Choose which service to use for resolving conflicts
def resolve_conflict(conflict_text, service="ollama", model="llama3.2"):
    if service == "ollama":
        model = model or DEFAULT_OLLAMA_MODEL
        return resolve_with_ollama(conflict_text, model)
    elif service == "openai":
        model = model or DEFAULT_OPENAI_MODEL
        return resolve_with_openai(conflict_text, model)
    else:
        raise ValueError(f"Unknown service: {service}")

# Replace the conflicts in the file with the LLM's resolution
def apply_resolution(file_path, resolved_text):
    with open(file_path, 'w') as file:
        file.write(resolved_text)
    print(f"Resolved conflict in {file_path}")

def main(service="ollama", model="llama3.2"):
    conflict_files = get_conflict_files()
    if not conflict_files:
        print("No conflicts detected.")
        return

    for conflict_file in conflict_files:
        conflict_text = extract_conflicts(conflict_file)
        if conflict_text:
            print(f"Resolving conflict in {conflict_file} using {service} with model {model or 'default'}")
            resolved_text = resolve_conflict(conflict_text, service, model)
            apply_resolution(conflict_file, resolved_text)
        else:
            print(f"No conflicts found in {conflict_file}")

if __name__ == "__main__":
    import argparse

    # Command-line arguments
    parser = argparse.ArgumentParser(description="Resolve git conflicts using LLMs.")
    parser.add_argument("--service", choices=["ollama", "openai"], default="ollama", help="Select the service to use (ollama or openai)")
    parser.add_argument("--model", help="Specify the model to use for conflict resolution")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(service=args.service, model=args.model)
