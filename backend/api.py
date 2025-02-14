import requests
from flask import Flask, request, jsonify
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route("/generate_map", methods=["POST"])
def generate_map():
    try:
        # Parse JSON request
        data = request.json
        indicator = data.get("indicator")
        country = data.get("country")  # Expecting ISO-3 code from chatbot
        year = data.get("year", 2022)

        if not indicator or not country:
            return jsonify({"error": "Missing required parameters"}), 400

        # **Fetch data from World Bank API**
        world_bank_url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?date={year}&format=json"
        print(f"DEBUG: Fetching data from {world_bank_url}")  # ✅ Debugging

        response = requests.get(world_bank_url)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from World Bank"}), 500

        world_bank_data = response.json()
        print(f"DEBUG: Raw API Response: {world_bank_data}")  # ✅ Print entire response

        # **Check if response contains valid data**
        if not isinstance(world_bank_data, list) or len(world_bank_data) < 2 or not world_bank_data[1]:
            return jsonify({"error": "No valid data returned from World Bank API"}), 500

        # **Extract value safely**
        records = world_bank_data[1]
        value = next((entry["value"] for entry in records if "value" in entry and entry["value"] is not None), "No Data")
        
        # **Handle "No Data" case**
        if value == "No Data":
            return jsonify({"error": f"No available data for {indicator} in {year}"}), 404

        # **Generate Choropleth Map**
        df = pd.DataFrame([{"Country": country, "Value": value}])
        fig = px.choropleth(df, locations="Country", locationmode="ISO-3",
                            color="Value", title=f"{indicator} in {year}")

        # ✅ Return both raw value & choropleth JSON
        return jsonify({
            "country": country,
            "indicator": indicator,
            "year": year,
            "value": value,
            "map": fig.to_json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)