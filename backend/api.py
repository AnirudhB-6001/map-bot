from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import plotly.express as px
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Map Bot API is running with real-time data!"})

@app.route("/generate_map", methods=["POST"])
def generate_map():
    """
    Receives a JSON request with 'indicator', 'country', and 'year'.
    Fetches real-time data from the World Bank API and generates a choropleth map.
    """

    try:
        # Parse JSON request
        data = request.json
        indicator = data.get("indicator", "NY.GDP.PCAP.CD")  # Default: GDP per capita
        country = data.get("country", "IND")  # Default: India (ISO Alpha-3 code)
        year = data.get("year", 2022)

        # Convert country names to World Bank ISO-3 codes (for now, assume input is ISO-3)
        country_codes = {
            "India": "IND", "China": "CHN", "USA": "USA", "Germany": "DEU",
            "Pakistan": "PAK", "United Kingdom": "GBR"
        }
        country_code = country_codes.get(country, "IND")  # Default: India

        # **Fetch data from World Bank API**
        world_bank_url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?date={year}&format=json"

        response = requests.get(world_bank_url)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from World Bank"}), 500

        world_bank_data = response.json()

        # Extract relevant data
        if len(world_bank_data) < 2 or "value" not in world_bank_data[1][0]:
            return jsonify({"error": "No data available for this query"}), 404

        value = world_bank_data[1][0]["value"]

        # Create DataFrame for visualization
        df = pd.DataFrame({
            "Country": [country],
            "Indicator": [indicator],
            "Value": [value],
            "Year": [year]
        })

        # Generate Choropleth Map
        fig = px.choropleth(df, locations="Country", locationmode="country names",
                            color="Value", title=f"{indicator} in {year}")

        return fig.to_json()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
