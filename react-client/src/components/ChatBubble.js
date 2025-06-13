import React from "react";

const ChatBubble = ({ message }) => {
  const isUser = message.type === "user";
  const isAssistant = message.type === "assistant";
  const isError = message.type === "error";

  return (
    <div className={`chat-bubble ${isUser ? "user" : "assistant"}`}>
      {message.role && <div className="role-label">{message.role}</div>}
      {Array.isArray(message.content) ? (
        <ul>
          {message.content.map((line, idx) => (
            <li key={idx}>{line}</li>
          ))}
        </ul>
      ) : (
        <p className={isError ? "error" : ""}>{message.content}</p>
      )}
    </div>
  );
};

export default ChatBubble;
