import os
import pandas as pd
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.tools import Tool
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
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

try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Initialize the Groq model
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=groq_api_key)

# --- Custom Rego Generation Tool ---
def generate_rego_policy_tool_func(query_mo_type: str) -> str:
    """
    Generates Rego policy code based on the MO Type found in the master.csv.
    The query_mo_type should be a string representing the 'MO Type' column value.
    """
    matching_rows = df[df['MO Type'].str.lower() == query_mo_type.lower()]

    if matching_rows.empty:
        return f"No matching data found for MO Type: {query_mo_type} in master.csv to generate Rego code."

    row_data = matching_rows.iloc[0]

    vendor = row_data.get("Vendor", "unknown")
    mo_type = row_data.get("MO Type", "unknown")
    checking_attribute = row_data.get("Checking Attribute", "unknown")
    operation = row_data.get("Operation", "EQUALS")
    value = row_data.get("Value", "null")

    rego_operator = "=="
    if operation.upper() == "EQUALS":
        rego_operator = "=="
    elif operation.upper() == "NOT_EQUALS":
        rego_operator = "!="
    # Add more operations if your CSV has other types (e.g., GREATER_THAN, LESS_THAN)

    formatted_value = value
    if isinstance(value, str):
        if value.lower() == "null":
            formatted_value = "null"
        else:
            formatted_value = f'"{value}"'
    elif pd.isna(value):
        formatted_value = "null"

    # Construct the Rego policy string based on example.txt
    rego_code = f"""package {vendor.lower()}.{mo_type.lower()}

default allow = false

allow {{
   input.vendor == "{vendor}"
   input.MO_Type == "{mo_type}"
   input.Checking_Attribute {rego_operator} {formatted_value}
   input.parameters.gctiAnrUuBoostFactor != null
}}
"""
    return rego_code

rego_generation_tool = Tool(
    name="RegoGenerator",
    func=generate_rego_policy_tool_func,
    description="Useful for generating Rego policy code. Input should be the 'MO Type' (e.g., 'LNBTS') for which to generate the Rego code. This tool will look up the MO Type in the master.csv and construct the Rego policy based on the corresponding row data."
)

# --- CSV Querying Tool ---
# Create a pandas dataframe agent to handle general CSV queries
csv_agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=False,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    allow_dangerous_code=True,
    handle_parsing_errors=True,
)

# Wrap the pandas agent's run method as a Tool
csv_query_tool = Tool(
    name="CSVQueryTool",
    func=csv_agent_executor.run,
    description="Useful for answering questions about the data in master.csv. Input should be a natural language question about the CSV data."
)

# --- Main Agent Initialization ---
tools = [
    rego_generation_tool,
    csv_query_tool
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False, # Keep verbose false for cleaner output
    handle_parsing_errors=True,
    agent_kwargs={
        "prefix": "You are an AI assistant that can answer questions about a CSV file and generate Rego policy code. "
                  "When asked to generate Rego code, use the RegoGenerator tool with the appropriate MO Type. "
                  "For other questions about the CSV data, use the CSVQueryTool."
    }
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
