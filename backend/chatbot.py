import json
import requests
import spacy
import numpy as np
import base64
from fuzzywuzzy import process

def load_json(filename):
    """Loads JSON file as a dictionary."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load external JSON files
COUNTRY_ISO_MAP = load_json("countries.json")  # Country list
INDICATORS = load_json("indicators.json")  # Indicator list
ABBREVIATIONS = load_json("abbreviations.json")  # Abbreviations

def extract_query_info(user_query):
    """ Extracts country, indicator, and year from user query using NLP and fuzzy matching. """

    doc = nlp(user_query)

    # Extract year (default: 2022)
    year = next((int(token.text) for token in doc if token.text.isdigit()), 2022)

    # Extract country (match against full names & abbreviations)
    country_match = process.extractOne(user_query, list(COUNTRY_ISO_MAP.keys()), score_cutoff=60)
    country_name = country_match[0] if country_match else "Unknown"

    # Check if query contains abbreviations
    for abbr, full_name in ABBREVIATIONS.items():
        if abbr.lower() in user_query.lower():
            country_name = full_name
            break

    country_code = COUNTRY_ISO_MAP.get(country_name, "Unknown")

    # Extract indicator with fuzzy matching
    indicator_match = process.extractOne(user_query, INDICATORS.keys(), score_cutoff=60)
    indicator_code = INDICATORS.get(indicator_match[0] if indicator_match else "Unknown", "Unknown")

    return indicator_code, country_name, country_code, year

def ask_map_bot(user_query):
    """ Converts user input into structured JSON and sends API request. """

    # Extract information from query
    indicator, country_name, country_code, year = extract_query_info(user_query)

    if country_code == "Unknown" or indicator == "Unknown":
        print("\n❌ ERROR: Could not understand your query. Try rephrasing it.")
        return

    # Prepare API request
    request_data = {
        "indicator": indicator,
        "country": country_code,
        "year": year
    }

    api_url = "http://127.0.0.1:5000/generate_map"
    response = requests.post(api_url, json=request_data)

    if response.status_code == 200:
        data = response.json()

        if "value" in data and data["value"] is not None:
            value = data["value"]
            print(f"\n✅ {indicator} of {country_name} in {year}: {value}")
        else:
            print("\n❌ ERROR: No data available.")
            print(f"DEBUG: API Response: {data}")  # Print full response for debugging
    else:
        print("\n❌ ERROR: Failed to fetch map data.")
        print(f"DEBUG: API Response Code: {response.status_code}")

# Chatbot loop
while True:
    user_input = input("\nAsk me anything (type 'exit' to quit): ").strip()
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    ask_map_bot(user_input)