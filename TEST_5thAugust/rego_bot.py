import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI client with the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# The core system prompt for the LLM. This is crucial for guiding the model
# to generate correct and well-formatted Rego policies.
SYSTEM_PROMPT = """
You are an expert in the Open Policy Agent (OPA) and the Rego policy language.
Your task is to generate complete, valid, and well-structured Rego policies based on the user's request.
The generated policy must be a complete, runnable file.
Always include a `package` declaration at the top of the policy.
If the user's request implies a default behavior, use `default allow = false` or `default allow = true` as appropriate.
Include a `deny` rule with a clear, descriptive message for any conditions that should be forbidden.
Comment the code to explain the logic clearly.
Do not include any placeholders like `<...>` in the final code.
The generated code should be enclosed in a single markdown code block with the language specifier 'rego'.
If the request is ambiguous or lacks necessary details (e.g., specific values or field names), ask for clarification.
Ensure the policy is logically sound and adheres to Rego syntax.
"""

def generate_rego_policy(user_prompt: str):
    """
    Generates a Rego policy using the LLM.
    """
    if not user_prompt:
        return {"error": "Please provide a prompt."}

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Combine the system prompt and user prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {user_prompt}"
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        # Extract the generated code from the LLM's response
        llm_response = response.text
        
        # Use simple string manipulation to get the Rego code block
        rego_code_start = llm_response.find("```rego") + len("```rego")
        rego_code_end = llm_response.rfind("```")
        rego_code = llm_response[rego_code_start:rego_code_end].strip()
        
        response = {
            "rego_code": rego_code
        }
        
        return response

    except Exception as e:
        # General error handling
        return {"error": str(e)}

def main():
    """
    Main function to run the Rego policy generator.
    It can run in interactive mode or take a command-line argument.
    """
    if len(sys.argv) > 1:
        # Command-line argument mode
        user_prompt = " ".join(sys.argv[1:])
        print("Generating policy...")
        result = generate_rego_policy(user_prompt)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n--- Generated Rego Policy ---")
            print(result["rego_code"])
            print("\n")
    else:
        # Interactive mode
        print("Rego Policy Generator")
        print("Enter your request to generate a Rego policy. Type 'exit' to quit.")

        while True:
            try:
                user_prompt = input("> ")
                if user_prompt.lower() == 'exit':
                    break

                print("Generating policy...")
                result = generate_rego_policy(user_prompt)

                if "error" in result:
                    print(f"Error: {result['error']}")
                else:
                    print("\n--- Generated Rego Policy ---")
                    print(result["rego_code"])
                    print("\n")
            except EOFError:
                print("\n\nThis environment does not support interactive input. Please run the script with a command-line argument:")
                print("python rego_bot.py \"<your policy request>\"")
                break

if __name__ == "__main__":
    main()