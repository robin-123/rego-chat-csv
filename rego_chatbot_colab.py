# Instructions for Google Colab:
# 1. Run the following commands in a Colab cell to install necessary libraries:
#    !pip install langchain-experimental langchain-groq groq pandas
# 2. Upload your 'master.csv' file to the Colab environment (e.g., by dragging it to the file explorer on the left).
# 3. Enter your GROQ_API_KEY when prompted.

import os
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_groq import ChatGroq

# Prompt for GROQ_API_KEY
groq_api_key = input("Please enter your GROQ_API_KEY: ")
os.environ["GROQ_API_KEY"] = groq_api_key

if not groq_api_key:
    print("Error: GROQ_API_KEY not provided. Please set it.")
    exit()

# Load the CSV file directly
file_path = "master.csv"

if not os.path.exists(file_path):
    print(f"Error: The file '{file_path}' was not found. Please make sure it is uploaded to the Colab environment.")
    exit()

print(f"Loading CSV file: {file_path}")

# Initialize the Groq model
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=groq_api_key)

# Create the CSV agent
agent = create_csv_agent(
    llm,
    file_path,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    allow_dangerous_code=True,
    handle_parsing_errors=True,
)

print("\nCSV Chatbot (Colab) Ready! Type 'exit' to quit.\n")

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
