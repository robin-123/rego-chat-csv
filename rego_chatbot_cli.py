import os
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("Error: GROQ_API_KEY not found in .env file. Please set it.")
    exit()

# Load the CSV file directly
file_path = "master.csv"

if not os.path.exists(file_path):
    print(f"Error: The file '{file_path}' was not found. Please make sure it is in the same directory as this script.")
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

print("\nCSV Chatbot (CLI) Ready! Type 'exit' to quit.\n")

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
