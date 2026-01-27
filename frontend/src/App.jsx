import React, { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const App = () => {
  const [lat, setLat] = useState("28.6139");
  const [lon, setLon] = useState("77.2090");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [aqi, setAqi] = useState(null);
  const [weather, setWeather] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [aqiRes, weatherRes] = await Promise.all([
        axios.get(`${API_BASE}/aqi`, { params: { lat, lon } }),
        axios.get(`${API_BASE}/weather`, { params: { lat, lon } }),
      ]);
      setAqi(aqiRes.data);
      setWeather(weatherRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header>
        <h1>Weather & AQI Dashboard</h1>
        <p>Enter coordinates to fetch real-time readings.</p>
      </header>

      <section className="controls">
        <label>
          Latitude
          <input value={lat} onChange={(e) => setLat(e.target.value)} />
        </label>
        <label>
          Longitude
          <input value={lon} onChange={(e) => setLon(e.target.value)} />
        </label>
        <button onClick={fetchData} disabled={loading}>
          {loading ? "Loading..." : "Fetch"}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="cards">
        <div className="card">
          <h2>AQI</h2>
          {aqi ? (
            <>
              <p className="big">{aqi.aqi ?? "-"}</p>
              <pre>{JSON.stringify(aqi.components, null, 2)}</pre>
            </>
          ) : (
            <p>No data yet.</p>
          )}
        </div>
        <div className="card">
          <h2>Weather</h2>
          {weather ? (
            <>
              <p className="big">{weather.temperature ?? "-"}°C</p>
              <p>{weather.condition}</p>
              <p>Humidity: {weather.humidity ?? "-"}%</p>
            </>
          ) : (
            <p>No data yet.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default App;
