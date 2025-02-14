import json
import requests
import spacy
import numpy as np
import base64
from fuzzywuzzy import process

def decode_plotly_value(encoded_value):
    """ Decodes base64-encoded numerical values from Plotly API response. """
    if isinstance(encoded_value, dict) and "bdata" in encoded_value:
        return np.frombuffer(base64.b64decode(encoded_value["bdata"]), dtype=encoded_value["dtype"])[0]
    return encoded_value  # Return as-is if it's not encoded

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# **Country List with ISO-3 Codes**
COUNTRY_ISO_MAP = {  
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Andorra": "AND", "Angola": "AGO",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
    "Bahamas": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD", "Barbados": "BRB", "Belarus": "BLR",
    "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN", "Bhutan": "BTN", "Bolivia": "BOL",
    "Bosnia and Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA", "Brunei": "BRN", "Bulgaria": "BGR",
    "Burkina Faso": "BFA", "Burundi": "BDI", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Chile": "CHL", "China": "CHN", "Colombia": "COL", "Costa Rica": "CRI", "Cuba": "CUB", 
    "Czech Republic": "CZE", "Denmark": "DNK", "Dominican Republic": "DOM", "Ecuador": "ECU", "Egypt": "EGY",
    "France": "FRA", "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC", "Guatemala": "GTM",
    "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Japan": "JPN", "Kenya": "KEN", "Malaysia": "MYS",
    "Mexico": "MEX", "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL", "Nigeria": "NGA",
    "Norway": "NOR", "Pakistan": "PAK", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
    "Qatar": "QAT", "Russia": "RUS", "Saudi Arabia": "SAU", "Singapore": "SGP", "South Africa": "ZAF",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sweden": "SWE", "Switzerland": "CHE", "Thailand": "THA",
    "Turkey": "TUR", "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA", "Vietnam": "VNM", "Zambia": "ZMB", "Zimbabwe": "ZWE"
}

INDICATORS = {
    "GDP per capita": "NY.GDP.PCAP.CD",
    "Total GDP": "NY.GDP.MKTP.CD",
    "Population": "SP.POP.TOTL",
    "Inflation": "FP.CPI.TOTL.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS",
    "Life Expectancy": "SP.DYN.LE00.IN",
    "CO2 Emissions": "EN.ATM.CO2E.PC",
    "Poverty Rate": "SI.POV.DDAY",
    "Exports": "NE.EXP.GNFS.CD",
    "Imports": "NE.IMP.GNFS.CD",
    "Government Debt": "GC.DOD.TOTL.GD.ZS",
    "Education Expenditure": "SE.XPD.TOTL.GD.ZS",
    "Health Expenditure": "SH.XPD.CHEX.GD.ZS"
}

def extract_query_info(user_query):
    """ Extracts country, indicator, and year from user query using NLP and fuzzy matching. """

    doc = nlp(user_query)

    # Extract year (default: 2022)
    year = next((int(token.text) for token in doc if token.text.isdigit()), 2022)

    # Common country abbreviations (expanding recognition)
    ABBREVIATIONS = {
        "UK": "United Kingdom",
        "USA": "United States",
        "UAE": "United Arab Emirates",
        "South Korea": "Korea, Rep.",
        "North Korea": "Korea, Dem. People’s Rep."
    }

    # Extract country with fuzzy matching
    country_match = process.extractOne(user_query, list(COUNTRY_ISO_MAP.keys()), score_cutoff=60)

    if country_match:
        country_name = country_match[0]
    else:
        for abbr, full_name in ABBREVIATIONS.items():
            if abbr.lower() in user_query.lower():
                country_name = full_name
                break
        else:
            country_name = "Unknown"

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
        print(f"DEBUG: API URL: {api_url}")

# Chatbot loop
while True:
    user_input = input("\nAsk me anything (type 'exit' to quit): ").strip()
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    ask_map_bot(user_input)