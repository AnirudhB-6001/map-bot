import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

const App = () => {
  const [plotData, setPlotData] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/choropleth")
      .then((response) => response.json())
      .then((data) => setPlotData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <div>
      <h1>Choropleth Map</h1>
      {plotData ? (
        <Plot data={plotData.data} layout={plotData.layout} />
      ) : (
        <p>Loading map...</p>
      )}
    </div>
  );
};

export default App;