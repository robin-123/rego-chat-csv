# app.py
from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import re
import os
import secrets # For generating a strong secret key

app = Flask(__name__)

# --- Configuration ---
# Generate a strong, random secret key for session management.
# In a production environment, this should be loaded from an environment variable
# or a secure configuration file, NOT hardcoded.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))

# --- Data Loading ---
# Load the CSV data. Ensure 'master.csv' is in the same directory as app.py
try:
    df = pd.read_csv('master.csv')
    # Convert relevant columns to string type to avoid errors with .str.contains()
    # if they contain non-string data (e.g., numbers, NaN).
    df['MO Type'] = df['MO Type'].astype(str)
    df['Checking Attribute'] = df['Checking Attribute'].astype(str)
    print("master.csv loaded successfully.")
except FileNotFoundError:
    df = pd.DataFrame(columns=['MO Type', 'Checking Attribute']) # Create a DataFrame with expected columns
    print("master.csv not found. Starting with an empty DataFrame.")
except Exception as e:
    df = pd.DataFrame(columns=['MO Type', 'Checking Attribute'])
    print(f"Error loading master.csv: {e}. Starting with an empty DataFrame.")

def process_user_query(query):
    intent = None
    entities = {}

    # Intent: Generate Rego Policy
    rego_keywords = ['rego', 'policy', 'generate', 'create', 'make']
    if any(keyword in query.lower() for keyword in rego_keywords):
        intent = 'generate_rego_policy'

    # Entity Extraction: MO Type, Checking Attribute
    if 'mo type' in query.lower():
        entities['mo_type'] = True
    if 'checking attribute' in query.lower():
        entities['checking_attribute'] = True

    # Try to extract specific values for MO Type or Checking Attribute
    for col_name in df.columns:
        if col_name.lower() == 'mo type':
            for unique_val in df[col_name].dropna().unique():
                if re.search(r'\b' + re.escape(unique_val.lower()) + r'\b', query.lower()):
                    entities['mo_type_value'] = unique_val
                    break
        elif col_name.lower() == 'checking attribute':
            for unique_val in df[col_name].dropna().unique():
                if re.search(r'\b' + re.escape(unique_val.lower()) + r'\b', query.lower()):
                    entities['checking_attribute_value'] = unique_val
                    break

    return intent, entities

@app.route('/')
def index():
    """Renders the main chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages and directs the conversation flow."""
    user_message = request.json.get('message', '').strip()
    response = ""

    if not user_message:
        return jsonify({'response': "Please type a message."})

    intent, entities = process_user_query(user_message)

    # State 1: Awaiting filter value after clarification
    if session.get('awaiting_filter_value'):
        filter_value = user_message
        filter_by = session['filter_by']
        session.pop('awaiting_filter_value')
        session.pop('filter_by') # Clear filter_by after use

        if filter_by == 'mo type':
            filtered_df = df[df['MO Type'].str.contains(filter_value, case=False, na=False)]
        elif filter_by == 'checking attribute':
            filtered_df = df[df['Checking Attribute'].str.contains(filter_value, case=False, na=False)]
        elif filter_by == 'both':
            filtered_df = df[
                df['MO Type'].str.contains(filter_value, case=False, na=False) |
                df['Checking Attribute'].str.contains(filter_value, case=False, na=False)
            ]
        else:
            return jsonify({'response': 'No filter criteria specified.'})

        if not filtered_df.empty:
            session['filtered_data'] = filtered_df.to_dict(orient='records')
            return jsonify({'response': 'Filtered data found. Now I can generate the Rego policy. Would you like to generate it?'})
        else:
            return jsonify({'response': 'No data found matching your criteria. Please try again.'})

    # State 2: Initial intent recognition or follow-up to initial query
    if intent == 'generate_rego_policy':
        if 'mo_type_value' in entities and 'checking_attribute_value' in entities:
            # Both values provided in initial query
            session['filter_by'] = 'both'
            session['awaiting_filter_value'] = True # Set to true to trigger the filter logic above
            # Simulate the user providing the combined value for filtering
            # For 'both', we'll just use the MO Type value for the initial filter, and the filter logic will handle the OR condition
            return jsonify({'response': f'Found MO Type: {entities['mo_type_value']} and Checking Attribute: {entities['checking_attribute_value']}. Proceeding to filter.', 'message': entities['mo_type_value']})
        elif 'mo_type_value' in entities:
            session['filter_by'] = 'mo type'
            session['awaiting_filter_value'] = True
            return jsonify({'response': f'Found MO Type: {entities['mo_type_value']}. Proceeding to filter.', 'message': entities['mo_type_value']})
        elif 'checking_attribute_value' in entities:
            session['filter_by'] = 'checking attribute'
            session['awaiting_filter_value'] = True
            return jsonify({'response': f'Found Checking Attribute: {entities['checking_attribute_value']}. Proceeding to filter.', 'message': entities['checking_attribute_value']})
        else:
            # Ask for clarification if no specific values are found
            session['clarification_needed'] = True
            return jsonify({'response': 'To generate the Rego policy, I need to filter the data. What kind of parameter are you looking for? (MO Type, Checking Attribute, or Both)', 'type': 'clarification'})
    
    # State 3: User clarifies parameter type
    elif user_message.lower() in ['mo type', 'checking attribute', 'both'] and session.get('clarification_needed'):
        session['clarification_needed'] = False
        session['filter_by'] = user_message.lower()
        session['awaiting_filter_value'] = True

        suggestions = []
        if user_message.lower() == 'mo type':
            suggestions = df['MO Type'].dropna().unique().tolist()
        elif user_message.lower() == 'checking attribute':
            suggestions = df['Checking Attribute'].dropna().unique().tolist()
        elif user_message.lower() == 'both':
            mo_type_suggestions = df['MO Type'].dropna().unique().tolist()
            checking_attribute_suggestions = df['Checking Attribute'].dropna().unique().tolist()
            suggestions = list(set(mo_type_suggestions + checking_attribute_suggestions))

        response_message = f'You selected to filter by {user_message}. Please provide the value for {user_message}.'
        if suggestions:
            response_message += f' Some suggestions: {", ".join(suggestions[:5])}...' # Limit suggestions to 5

        return jsonify({'response': response_message})
    
    # State 4: User confirms Rego generation
    elif user_message.lower() == 'yes' and session.get('filtered_data'):
        # Directly call generate_rego logic here instead of redirecting
        if 'filtered_data' in session and session['filtered_data']:
            rego_policy = "# Rego Policy Generated\n\n"
            for row in session['filtered_data']:
                mo_type = row.get('MO Type', 'N/A')
                checking_attribute = row.get('Checking Attribute', 'N/A')
                rego_policy += f"package ericsson.consistency.{mo_type.lower().replace(' ', '_')}\n\n"
                rego_policy += f"default allow = false\n\n"
                rego_policy += f"allow {{\n"
                rego_policy += f"    input.mo_type == \"{mo_type}\"\n"
                rego_policy += f"    input.checking_attribute == \"{checking_attribute}\"\n"
                rego_policy += f"}}\n\n"
            session.pop('filtered_data', None) # Clear filtered data after generation
            return jsonify({'response': 'Here is your Rego policy:', 'rego_policy': rego_policy})
        else:
            return jsonify({'response': 'No filtered data available to generate Rego policy.'})

    # Default response if no intent or state matches
    else:
        return jsonify({'response': "I'm sorry, I can only generate Rego policies for parameter consistency checking for Ericsson data models at the moment."})

if __name__ == '__main__':
    app.run(debug=True)