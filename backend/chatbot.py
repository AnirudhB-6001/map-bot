import json
import requests
import spacy
import numpy as np
import base64
from fuzzywuzzy import process

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Country and indicator mapping for World Bank API
COUNTRY_LIST = ["India", "China", "USA", "United States", "Germany", "Pakistan", "United Kingdom"]
INDICATORS = {
    "GDP": "NY.GDP.PCAP.CD",
    "Population": "SP.POP.TOTL",
    "Inflation": "FP.CPI.TOTL.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS"
}

def decode_plotly_value(encoded_value):
    """ Decodes a Plotly `z` value from the API response. """
    if isinstance(encoded_value, dict) and "bdata" in encoded_value:
        # Decode base64-encoded data
        decoded_bytes = base64.b64decode(encoded_value["bdata"])
        dtype = np.dtype(encoded_value["dtype"])
        value = np.frombuffer(decoded_bytes, dtype=dtype)[0]
        return round(value, 2)  # Return rounded numerical value
    return encoded_value  # If already in readable format

def extract_query_info(user_query):
    """ Extracts country, indicator, and year from user query using NLP and fuzzy matching. """

    doc = nlp(user_query)

    # Extract year (default: 2022)
    year = next((int(token.text) for token in doc if token.text.isdigit()), 2022)

    # Extract country
    country, confidence = process.extractOne(user_query, COUNTRY_LIST) if COUNTRY_LIST else ("India", 100)

    # Extract indicator
    indicator_key, confidence = process.extractOne(user_query, INDICATORS.keys()) if INDICATORS else ("GDP", 100)
    indicator_code = INDICATORS.get(indicator_key, "NY.GDP.PCAP.CD")  # Default to GDP

    return indicator_code, country, year

def ask_map_bot(user_query):
    """ Converts user input into structured JSON and sends API request. """

    indicator, country, year = extract_query_info(user_query)

    # Prepare API request
    request_data = {
        "indicator": indicator,
        "country": country,
        "year": year
    }

    api_url = "http://127.0.0.1:5000/generate_map"
    response = requests.post(api_url, json=request_data)

    if response.status_code == 200:
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            country_data = data["data"][0]
            country_name = country_data.get("locations", ["Unknown"])[0]
            value = decode_plotly_value(country_data.get("z", "Unknown"))  # Decode value

            # Print formatted response
            print(f"\n{indicator} of {country_name} in {year}: {value}")
        else:
            print("\nNo data available for the given query.")
    else:
        print("\nError: Failed to fetch map data")

# Chatbot loop
while True:
    user_input = input("\nAsk me anything (type 'exit' to quit): ").strip()
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    ask_map_bot(user_input)