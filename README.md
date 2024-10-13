# Git Conflict Resolver - GPT

An automatic Git conflict resolver powered by large language models (LLMs), designed to streamline the conflict resolution process in version control systems. This tool leverages both Ollama's Llama3.2 model and OpenAI's API to provide intelligent suggestions for merging conflicting code changes.

## Features

- **Multi-Model Support**: Choose between local execution using Ollama's Llama3.2 model or cloud-based resolution with OpenAI's GPT.
- **Interactive Resolution Process**: Easily iterate on conflict resolutions with user inputs.
- **JSON Output**: Results are provided in a structured JSON format for easy integration into workflows.

## Installation (macOS)

1. **Install Ollama**: Follow the instructions on the [Ollama website](https://ollama.com/download/mac) to install Ollama, which allows you to run LLMs locally on macOS.

2. **Pull the Llama3.2 Model**: Open your terminal and run the following command to download the Llama3.2 model:
   ```bash
   ollama pull llama3.2
   ```

3. **Set Up OpenAI API Key** (if using OpenAI):
   Make sure to set your OpenAI API key in your environment:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

4. **Install Requirements**: It's recommended to use a virtual environment. Install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Script**: Execute the script using the command line. You can specify which service to use (Ollama or OpenAI) and the model if necessary:
   ```bash
   python git_conflict_resolver.py --service ollama --model llama3.2
   ```

2. **Input Conflict**: The script will read the conflict text from `testfile.txt`. Ensure this file contains your Git conflict markers (e.g., `<<<<<<< HEAD`, `=======`, `>>>>>>> branch_name`).

3. **Interactive Resolution**: 
   - The tool will propose a resolution based on the provided conflict text.
   - You will be prompted to either apply the resolution, enter additional instructions to refine it, or exit the process.
   - If you choose to apply, the resolved output will replace the contents of `testfile.txt`.

## Example

```bash
$ python git_conflict_resolver.py --service openai
Using openai running None
--- Conflict Changes ---
<<<<<<< HEAD
print("Hello, World!")
=======
print("Goodbye, World!")
>>>>>>> branch_name

--- Proposed Resolution ---
print("Hello, World!")
print("Goodbye, World!")
------------------------
Do you want to apply this resolution to the file? (yes to apply, enter additional instructions to modify, or exit to quit): yes
Changes applied to testfile.txt.
```

## Contribution

Feel free to fork the repository and submit pull requests for improvements or bug fixes. Issues and suggestions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify any sections as needed!
