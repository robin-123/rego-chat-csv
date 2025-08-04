import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage


load_dotenv() # Load environment variables from .env file

# Ollama specific configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")


master_csv_content = ""
format_txt_content = ""
llm_chain = None
chat_history_messages = []

# --- Function to read file content ---
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        messagebox.showerror("File Error", f"The file '{file_path}' was not found.")
        return None
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file '{file_path}': {e}")
        return None

# --- UI Functions ---
def upload_master_csv():
    global master_csv_content
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        content = read_file_content(file_path)
        if content is not None:
            master_csv_content = content
            master_csv_label.config(text=f"Master CSV: {os.path.basename(file_path)} (Loaded)")
            messagebox.showinfo("Success", "master.csv loaded successfully!")
            check_and_initialize_chat()

def upload_format_txt():
    global format_txt_content
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        content = read_file_content(file_path)
        if content is not None:
            format_txt_content = content
            format_txt_label.config(text=f"Format TXT: {os.path.basename(file_path)} (Loaded)")
            messagebox.showinfo("Success", "format.txt loaded successfully!")
            check_and_initialize_chat()

def check_and_initialize_chat():
    global llm_chain, chat_history_messages
    if master_csv_content and format_txt_content and llm_chain is None:
        try:
            llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL_NAME, temperature=0)

            initial_prompt_text = (
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

            # Initialize chat history with the system prompt and initial bot message
            chat_history_messages = [
                HumanMessage(content=initial_prompt_text),
                AIMessage(content="Okay, I can help you generate Rego code. What Rego code would you like to generate?")
            ]

            llm_chain = llm 

            chat_history.config(state=tk.NORMAL) # Enable editing
            chat_history.insert(tk.END, "Bot: Okay, I can help you generate Rego code. What Rego code would you like to generate?\n\n")
            chat_history.config(state=tk.DISABLED) # Disable editing
            send_button.config(state=tk.NORMAL)
            user_input_entry.config(state=tk.NORMAL)
            user_input_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Chat Initialization Error", f"Failed to initialize chat with Ollama: {e}\nEnsure Ollama is running and the model '{OLLAMA_MODEL_NAME}' is pulled.")
            llm_chain = None

def send_message():
    global llm_chain, chat_history_messages
    user_message = user_input_entry.get().strip()
    if not user_message:
        return

    chat_history.config(state=tk.NORMAL)
    chat_history.insert(tk.END, f"You: {user_message}\n")
    user_input_entry.delete(0, tk.END)
    chat_history.config(state=tk.DISABLED) 

    if llm_chain:
        try:
            # Add user message to history
            chat_history_messages.append(HumanMessage(content=user_message))

            # Invoke the LLM with the full chat history
            response = llm_chain.invoke(chat_history_messages)
            response_text = response.content 

            # Add AI message to history
            chat_history_messages.append(AIMessage(content=response_text))

            chat_history.config(state=tk.NORMAL)
            chat_history.insert(tk.END, f"Bot: {response_text}\n\n")
            chat_history.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("LLM Communication Error", f"Error communicating with Ollama: {e}\nEnsure Ollama is running and the model '{OLLAMA_MODEL_NAME}' is pulled.")
            chat_history.config(state=tk.NORMAL)
            chat_history.insert(tk.END, "Bot: An error occurred. Please try again.\n\n")
            chat_history.config(state=tk.DISABLED)
    else:
        messagebox.showwarning("Chat Not Ready", "Please upload both master.csv and format.txt to start the chat.")

# --- UI Setup ------------------------------------------------------------------------------------------------
root = tk.Tk()
root.title("Rego Chatbot UI (Ollama)")

# File Upload Frame
file_frame = tk.LabelFrame(root, text="Upload Files", padx=10, pady=10)
file_frame.pack(pady=10, padx=10, fill="x")

master_csv_button = tk.Button(file_frame, text="Upload master.csv", command=upload_master_csv)
master_csv_button.pack(side=tk.LEFT, padx=5)
master_csv_label = tk.Label(file_frame, text="Master CSV: Not Loaded")
master_csv_label.pack(side=tk.LEFT, padx=5)

format_txt_button = tk.Button(file_frame, text="Upload format.txt", command=upload_format_txt)
format_txt_button.pack(side=tk.LEFT, padx=5)
format_txt_label = tk.Label(file_frame, text="Format TXT: Not Loaded")
format_txt_label.pack(side=tk.LEFT, padx=5)

# Chat Frame
chat_frame = tk.LabelFrame(root, text="Chat", padx=10, pady=10)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

chat_history = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, width=80, height=20)
chat_history.pack(pady=5, fill="both", expand=True)

user_input_frame = tk.Frame(chat_frame)
user_input_frame.pack(pady=5, fill="x")

user_input_entry = tk.Entry(user_input_frame, width=60, state=tk.DISABLED)
user_input_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
user_input_entry.bind("<Return>", lambda event=None: send_message()) # Bind Enter key

send_button = tk.Button(user_input_frame, text="Send", command=send_message, state=tk.DISABLED)
send_button.pack(side=tk.RIGHT, padx=5)

root.mainloop()
