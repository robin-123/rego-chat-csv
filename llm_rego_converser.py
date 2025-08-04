import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv() # Load environment variables from .env file

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY not found. Please set it as an environment variable.")
    print("You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey")
    exit()

genai.configure(api_key=API_KEY)

# --- File Paths (adjust if your files are not in the same directory) ---
MASTER_CSV_PATH = "master.csv"
FORMAT_TXT_PATH = "format.txt"

# --- Function to read file content ---
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct directory.")
        exit()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        exit()

# --- Main execution ---
if __name__ == "__main__":
    # Read the content of master.csv and format.txt
    master_csv_content = read_file_content(MASTER_CSV_PATH)
    format_txt_content = read_file_content(FORMAT_TXT_PATH)

    # Initialize the Generative Model
    model = genai.GenerativeModel('gemini-1.5-flash') # You can choose other models like 'gemini-1.5-pro-latest'

    # Start a new chat session
    # The initial message provides the LLM with the context of the files
    initial_prompt = (
        "You are an expert in generating Rego code based on provided data and a format template.\n"
        "Here is the content of the 'master.csv' file:\n"
        "```csv\n"
        f"{master_csv_content}\n"
        "```\n"
        "Here is the content of the 'format.txt' file, which defines the Rego code structure:\n"
        "```\n"
        f"{format_txt_content}\n"
        "```\n"
        "Your task is to guide the user conversationally to gather necessary parameters (Vendor, MO Type, Checking Attribute, Operation, Value) from the 'master.csv' data, and then generate the Rego code using the 'format.txt' template.\n"
        "If the user provides enough information directly, generate the code. Otherwise, ask clarifying questions, suggest options (like unique MO Types or Checking Attributes if multiple matches are found), and continue the conversation until enough details are collected.\n"
        "Start by asking the user what Rego code they would like to generate."
    )

    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [initial_prompt]},
        {'role': 'model', 'parts': ["Okay, I can help you generate Rego code. What Rego code would you like to generate?"]}
    ])


    print("Rego Code Generator (LLM-powered) Ready! Type 'exit' to quit.")
    print("I will guide you through generating Rego code based on the provided master.csv and format.txt.")
    print("You can start by saying 'generate rego code'.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Exiting LLM-powered Rego Code Generator. Goodbye!")
            break

        try:
            # Send user input to the LLM and get its response
            response = chat.send_message(user_input)
            print(f"Bot: {response.text}")

        except Exception as e:
            print(f"Error communicating with the LLM: {e}")
            print("Please ensure your API key is correct and you have an active internet connection.")