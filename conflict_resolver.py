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

# Function to display changes and resolution
def display_changes(conflict_text, resolved_text):
    print("\n--- Conflict Changes ---")
    print(conflict_text)
    print("\n--- Proposed Resolution ---")
    print(resolved_text)
    print("\n------------------------\n")

# Resolve the conflict using Ollama's LLM
def resolve_with_ollama(conflict_text, model=DEFAULT_OLLAMA_MODEL, additional_instructions=None):
    # Craft a prompt for the LLM to merge the conflicts
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
    
    # Use the ollama library to call the model
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    
    # Access the content from the response
    resolved_text = response.get("message", {}).get("content", "No content found in response.")

    # Extract the JSON part from the raw response
    try:
        # Look for the starting point of the JSON
        json_start = resolved_text.index('{')
        json_content = resolved_text[json_start:]  # Extract JSON content

        # Strip out any unwanted text before the JSON
        json_content = json_content.split('```')[0].strip()  # Remove any code block markers and trailing text

        # Attempt to load the JSON content
        resolved_text_json = json.loads(json_content)
        return resolved_text_json.get("output", "No output found in JSON response.")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw content: {resolved_text}")
        return None  # Return None to indicate failure

# Resolve the conflict using OpenAI's API
def resolve_with_openai(conflict_text, model=DEFAULT_OPENAI_MODEL, additional_instructions=None):
    # Craft a prompt for the LLM to merge the conflicts
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

    # Use OpenAI's API to call the model (new API style)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Access the content from the response
    resolved_text = response['choices'][0]['message']['content']

    # Extract the JSON part from the raw response
    try:
        # Look for the starting point of the JSON
        json_start = resolved_text.index('{')
        json_content = resolved_text[json_start:]  # Extract JSON content

        # Strip out any unwanted text before the JSON
        json_content = json_content.split('```')[0].strip()  # Remove any code block markers and trailing text

        # Attempt to load the JSON content
        resolved_text_json = json.loads(json_content)
        return resolved_text_json.get("output", "No output found in JSON response.")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw content: {resolved_text}")
        return None  # Return None to indicate failure


# Choose which service to use for resolving conflicts
def resolve_conflict(conflict_text, service="ollama", model=None, additional_instructions=None):
    if service == "ollama":
        model = model or DEFAULT_OLLAMA_MODEL
        resolved_text = resolve_with_ollama(conflict_text, model, additional_instructions)
        if resolved_text:
            display_changes(conflict_text, resolved_text)  # Display the changes and resolution
        return resolved_text
    elif service == "openai":
        model = model or DEFAULT_OPENAI_MODEL
        resolved_text = resolve_with_openai(conflict_text, model, additional_instructions)
        if resolved_text:
            display_changes(conflict_text, resolved_text)  # Display the changes and resolution
        return resolved_text
    else:
        raise ValueError(f"Unknown service: {service}")

def main(service="openai", model=None):
    print("Using ", service , " running ", model)
    # Load the conflict text from the file
    with open('testfile.txt', 'r') as file:
        conflict_text = file.read()

    resolved_text = None
    additional_instructions = None
    while resolved_text is None:
        # Resolve the conflict
        resolved_text = resolve_conflict(conflict_text, service, model, additional_instructions)

        # Prompt user for additional instructions or confirmation to apply changes
        user_input = input("Do you want to apply this resolution to the file? (yes to apply, enter additional instructions to modify, or exit to quit): ").strip()

        if user_input.lower() == 'yes':
            with open('testfile.txt', 'w') as file:
                file.write(resolved_text)
            print("Changes applied to testfile.txt.")
            break  # Exit the loop if changes are applied
        elif user_input.lower() == 'exit':
            break;
        else:
            # Use the user's input as additional instructions
            resolved_text = None  # Reset resolved_text to trigger another resolution attempt
            additional_instructions = user_input

    else:
        print("Could not resolve the conflict.")

if __name__ == "__main__":
    import argparse

    # Command-line arguments
    parser = argparse.ArgumentParser(description="Resolve git conflicts using LLMs.")
    parser.add_argument("--service", choices=["ollama", "openai"], default="openai", help="Select the service to use (ollama or openai)")
    parser.add_argument("--model", help="Specify the model to use for conflict resolution")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(service=args.service, model=args.model)
