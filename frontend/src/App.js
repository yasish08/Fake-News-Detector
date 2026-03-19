import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // 🌈 BACKGROUND TRANSITION (SMOOTH GRADIENT)
  useEffect(() => {
    if (!result) {
      document.body.style.background =
        "linear-gradient(to right, #ffffff, #ffffff)";
      return;
    }

    if (result.prediction === "REAL") {
      document.body.style.background =
        "linear-gradient(to right, #ffffff, #c8f7c5)";
    } else if (result.prediction === "FAKE") {
      document.body.style.background =
        "linear-gradient(to right, #ffffff, #f7c5c5)";
    } else {
      document.body.style.background =
        "linear-gradient(to right, #ffffff, #fff3cd)";
    }
  }, [result]);

  // 🔥 CONFIDENCE LABEL
  const getConfidenceLabel = (score) => {
    if (score > 0.7) return "High Confidence";
    if (score > 0.5) return "Moderate Confidence";
    return "Low Confidence";
  };

  // 🔥 HANDLE SUBMIT
  const handleSubmit = async () => {
    if (!text && !url) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await axios.post(
        "https://fake-news-backend-i8rt.onrender.com/predict",
        { text, url }
      );

      const data = res.data;

      if (!data || data.error) {
        throw new Error("Invalid response");
      }

      setResult(data);
      setHistory((prev) => [data, ...prev.slice(0, 4)]);
    } catch (err) {
      console.error(err);
      alert("Backend error");
    }

    setLoading(false);
  };

  // 🔥 KEYWORD HIGHLIGHT
  const highlightText = (inputText, keywords) => {
    if (!keywords || keywords.length === 0) return inputText;

    let highlighted = inputText;

    keywords.forEach((word) => {
      const regex = new RegExp(`(${word})`, "gi");
      highlighted = highlighted.replace(
        regex,
        `<span style="color:red;font-weight:bold;">$1</span>`
      );
    });

    return highlighted;
  };

  // 🔥 COLORS
  const getColor = (prediction) => {
    if (prediction === "REAL") return "#00ff9d";
    if (prediction === "FAKE") return "#ff4d4d";
    return "#ffc107";
  };

  // 🔥 LABEL
  const getLabel = (prediction) => {
    if (prediction === "REAL") return "Likely Real";
    if (prediction === "FAKE") return "Likely Fake";
    return "Uncertain";
  };

  // 🔥 PIE CHART
  const chartData = result
    ? {
        labels: ["Fake", "Real"],
        datasets: [
          {
            data: [
              result.probabilities?.fake || 0,
              result.probabilities?.real || 0
            ],
            backgroundColor: ["#ff4d4d", "#00ff9d"],
            borderWidth: 0
          }
        ]
      }
    : null;

  return (
    <div className="container">
      <h1>Fake News Detector</h1>

      <div className="card">
        {/* INPUT */}
        <textarea
          placeholder="Paste news headline or article..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <input
          type="text"
          placeholder="Optional: Paste article URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {/* ⚠️ URL TIP */}
        {!url && (
          <p style={{ color: "#888", marginTop: "8px", fontSize: "12px" }}>
            Tip: Add article URL for higher accuracy
          </p>
        )}

        {/* SKELETON */}
        {loading && (
          <div className="skeleton">
            <div className="skeleton-bar"></div>
          </div>
        )}

        {/* RESULT */}
        {result && (
          <div className="result">
            <h2 style={{ color: getColor(result.prediction) }}>
              {getLabel(result.prediction)}
            </h2>

            <p>
              Final Score: {(result.confidence * 100).toFixed(1)}% <br />
              <strong>{getConfidenceLabel(result.confidence)}</strong>
            </p>

            {/* BAR */}
            <div className="bar">
              <div
                className="fill"
                style={{
                  width: `${result.confidence * 100}%`,
                  background: getColor(result.prediction)
                }}
              ></div>
            </div>

            {/* PIE */}
            {chartData && (
              <div style={{ width: "250px", margin: "20px auto" }}>
                <Pie data={chartData} />
              </div>
            )}

            {/* BREAKDOWN */}
            <div style={{ textAlign: "left", marginTop: "15px" }}>
              <h4>Credibility Breakdown</h4>
              <p>
                Model Confidence:{" "}
                {result.signals?.model_confidence?.toFixed(2)}
              </p>
              <p>
                Source Credibility: {result.credibility?.toFixed(2)}
              </p>
              <p>
                Keyword Impact:{" "}
                {result.signals?.keywords_triggered?.length}
              </p>
            </div>

            {/* 🔥 CLEAN EXPLANATION */}
            <div style={{ textAlign: "left", marginTop: "10px" }}>
              <h4>Why this result?</h4>
              <ul>
                <li>
                  Model confidence is{" "}
                  {result.signals?.model_confidence?.toFixed(2)}
                </li>
                <li>
                  Source credibility is{" "}
                  {result.credibility?.toFixed(2)}
                </li>
                <li>
                  Keywords detected:{" "}
                  {result.signals?.keywords_triggered?.length > 0
                    ? result.signals.keywords_triggered.join(", ")
                    : "None"}
                </li>
              </ul>
            </div>

            {/* HIGHLIGHT */}
            {text && (
              <div style={{ marginTop: "15px", textAlign: "left" }}>
                <h4>Highlighted Analysis</h4>
                <p
                  dangerouslySetInnerHTML={{
                    __html: highlightText(
                      text,
                      result.signals?.keywords_triggered || []
                    )
                  }}
                ></p>
              </div>
            )}

            {/* LIMITATIONS */}
            <div style={{ marginTop: "15px", fontSize: "12px", opacity: 0.8 }}>
              <h4>Limitations</h4>
              <p>
                This model does not verify factual correctness and may fail on
                new or unseen topics.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* HISTORY */}
      {history.length > 0 && (
        <div className="history">
          <h3>Recent Predictions</h3>

          {history.map((item, index) => (
            <div key={index} className="history-item">
              <span style={{ color: getColor(item.prediction) }}>
                {getLabel(item.prediction)}
              </span>{" "}
              - {(item.confidence * 100).toFixed(0)}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;