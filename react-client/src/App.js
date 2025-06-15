import React, { useState } from "react";
import "./index.css";

function App() {
  const [name, setName] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = "http://132.196.215.105";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setOutput("");

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP error: ${response.status} - ${text}`);
      }

      const data = await response.json();
      setOutput(`
        ${data.professional.join("\n- ")}

        Casual:
        - ${data.casual.join("\n- ")}
      `);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Conversation Starter</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter a person's name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </form>

      {error && <p className="error">❌ {error}</p>}
      {output && (
        <div className="output">
          <h3>Generated Starters:</h3>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
