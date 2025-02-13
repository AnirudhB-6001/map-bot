from flask import Flask, request, jsonify
from flask_cors import CORS  # Enables frontend & chatbot to access API
import plotly.express as px
import pandas as pd

app = Flask(__name__)
CORS(app)  # Allows requests from frontend/chatbot

@app.route("/")
def home():
    return jsonify({"message": "Map Bot API is running!"})

@app.route("/generate_map", methods=["POST"])
def generate_map():
    """
    Receives a JSON request with 'indicator', 'country', and 'year'.
    Generates and returns a choropleth map based on the request.
    """

    try:
        # Parse JSON request
        data = request.json
        indicator = data.get("indicator", "GDP")
        country = data.get("country", "India")
        year = data.get("year", 2022)

        # Sample dataset (Later, we'll replace this with real data)
        df = pd.DataFrame({
            "Country": ["India", "China", "USA", "Germany"],
            "Year": [2022, 2022, 2022, 2022],
            "GDP": [3200, 10500, 65000, 48000],  # GDP per capita in USD
            "Population": [1400000000, 1440000000, 331000000, 83000000]
        })

        # Filter dataset based on user request
        df_filtered = df[(df["Country"] == country) & (df["Year"] == year)]

        if df_filtered.empty:
            return jsonify({"error": "No data available for this query"}), 404

        # Generate Choropleth Map
        fig = px.choropleth(df_filtered, locations="Country", locationmode="country names",
                            color=indicator, title=f"{indicator} in {year}")

        return fig.to_json()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
