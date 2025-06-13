import React, { useState } from "react";
import ChatBubble from "./components/ChatBubble";
import InputBar from "./components/InputBar";
import "./index.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (name) => {
    setLoading(true);
    setMessages((prev) => [...prev, { type: "user", content: name }]);

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await response.json();

      const starters = [
        { type: "assistant", role: "Professional", content: data.professional },
        { type: "assistant", role: "Casual", content: data.casual },
      ];

      setMessages((prev) => [...prev, ...starters]);
    } catch (err) {
      setMessages((prev) => [...prev, { type: "error", content: "Failed to fetch response." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>AI Conversation Starter</h1>
      <div className="chat-box">
        {messages.map((msg, idx) => (
          <ChatBubble key={idx} message={msg} />
        ))}
        {loading && <ChatBubble message={{ type: "assistant", content: "Generating..." }} />}
      </div>
      <InputBar onSubmit={handleSubmit} disabled={loading} />
    </div>
  );
}

export default App;
