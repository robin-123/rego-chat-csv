import os
import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_ollama import ChatOllama

# Instructions for Ollama:
# 1. Download and install Ollama from https://ollama.com/download
# 2. Run Ollama in your terminal.
# 3. Pull a model, e.g., for Llama 2: ollama pull llama2
# 4. Ensure the model is running when you execute this script.
# 5. Install the new Ollama integration: pip install -U langchain-ollama

# Load the CSV file directly
file_path = "master.csv"

if not os.path.exists(file_path):
    print(f"Error: The file '{file_path}' was not found. Please make sure it is in the same directory as this script.")
    exit()

print(f"Loading CSV file: {file_path}")

try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Initialize the Ollama model
# Replace 'llama2' with the name of the model you pulled (e.g., 'mistral', 'gemma')
llm = ChatOllama(model="llama2")

# Create the CSV agent
agent = create_csv_agent(
    llm,
    file_path,
    verbose=False, # Keep verbose false for cleaner output
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    allow_dangerous_code=True,
)

print("\nCSV Chatbot (Ollama CLI) Ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        print("Exiting chatbot. Goodbye!")
        break

    try:
        response = agent.run(user_input)
        print(f"Bot: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please try rephrasing your question.")
