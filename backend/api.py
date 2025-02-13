from flask import Flask, jsonify
from flask_cors import CORS  # Allows frontend to request data from backend
import plotly.express as px
import pandas as pd
import json
from flask_cors import CORS
from plotly.io import to_json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/choropleth")
def generate_choropleth():
    df = pd.DataFrame({
        "Country": ["India", "China", "USA", "Germany"],
        "GDP_per_capita": [2100, 10500, 63000, 45000]
    })

    fig = px.choropleth(df, locations="Country", locationmode="country names",
                         color="GDP_per_capita", title="Sample GDP per Capita")

    return to_json(fig)  # Use correct Plotly JSON serialization

if __name__ == "__main__":
    app.run(debug=True)