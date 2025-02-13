import json
import requests
import numpy as np
import base64

def decode_plotly_value(encoded_value):
    """
    Decodes a Plotly `z` value from the API response.
    """
    if isinstance(encoded_value, dict) and "bdata" in encoded_value:
        # Decode base64-encoded data
        decoded_bytes = base64.b64decode(encoded_value["bdata"])
        dtype = np.dtype(encoded_value["dtype"])
        value = np.frombuffer(decoded_bytes, dtype=dtype)[0]
        return value
    return encoded_value  # If already in readable format

def ask_map_bot(user_query):
    """
    Converts user input into structured JSON and sends API request.
    """

    # Example: Simple keyword-based parsing (To be improved with NLP)
    indicator = "GDP" if "GDP" in user_query else "Population"

    # Country detection from query
    country_map = {"India": "India", "China": "China", "USA": "USA", "Germany": "Germany"}
    country = next((c for c in country_map if c in user_query), "India")  # Default: India

    # Extract year from query (default: 2022)
    year = next((int(word) for word in user_query.split() if word.isdigit()), 2022)

    # Prepare JSON request
    request_data = {
        "indicator": indicator,
        "country": country,
        "year": year
    }

    # Send request to backend API
    api_url = "http://127.0.0.1:5000/generate_map"
    response = requests.post(api_url, json=request_data)

    if response.status_code == 200:
        data = response.json()

        # Extract country and GDP/population value from API response
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

# Run chatbot loop
while True:
    user_input = input("\nAsk me anything (type 'exit' to quit): ").strip()
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    ask_map_bot(user_input)
