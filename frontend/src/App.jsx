import { useState } from "react";
import { sendMessage } from "./api";

export default function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);

  async function handleSend() {
    if (!input) return;
    const reply = await sendMessage(input);
    setChat([...chat, { user: input, bot: reply.response }]);
    setInput("");
  }

  return (
    <div style={{ width: "500px", margin: "2rem auto", textAlign: "center" }}>
      <h1>🤖 Jarvis AI Assistant</h1>

      <div style={{ height: "60vh", overflowY: "auto", padding: "10px", border: "1px solid #ccc" }}>
        {chat.map((c, i) => (
          <div key={i} style={{ marginBottom: "15px", textAlign: "left" }}>
            <p><b>You:</b> {c.user}</p>
            <p><b>Jarvis:</b> {c.bot}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", marginTop: "10px" }}>
        <input
          style={{ flex: 1, padding: "10px" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Jarvis anything..."
        />
        <button style={{ padding: "10px 15px" }} onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}
