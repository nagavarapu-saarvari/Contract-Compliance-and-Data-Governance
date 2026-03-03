import React, { useState } from "react";

function PromptPanel({ selectedDoc }) {

  const [prompt, setPrompt] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [rules, setRules] = useState([]);
  const [showGuided, setShowGuided] = useState(false);

  const guidedPrompts = [
    "Generate governance rules from the selected contract",
    "Extract enforceable business policies from the contract",
    "Identify data sharing restrictions in the agreement",
    "List all compliance obligations present in the document"
  ];

  const selectGuidedPrompt = (text) => {
    setPrompt(text);
    setShowGuided(false);
  };

  const handleSubmit = async () => {

    if (!selectedDoc) {
      alert("Please select a document first");
      return;
    }

    setPrompt("")
    setRules([]);
    setStatusMessage("Parsing PDF...");

    const response = await fetch(
      `http://localhost:8001/generate_rules/${selectedDoc}`,
      { method: "POST" }
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {

      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      lines.forEach(line => {

  if (!line.trim()) return;

  if (line.startsWith("{")) {

    const parsed = JSON.parse(line);

    if (parsed.type === "rules") {

      setRules(parsed.rules);
      setStatusMessage("");

    }

  } else {

    setStatusMessage(line);

  }

  });

    }

  };

  return (
    <div className="chat-container">

      {/* STATUS OR TABLE */}

      <div className="chat-output">

        {rules.length === 0 && statusMessage && (
          <div className="status-message">
            {statusMessage}
          </div>
        )}

        {rules.length > 0 && (

          <table className="rules-table">

            <thead>
              <tr>
                <th>Rule ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Category</th>
                <th>Effect</th>
              </tr>
            </thead>

            <tbody>

              {rules.map((rule, index) => (

                <tr key={index}>
                  <td>{rule.rule_id}</td>
                  <td>{rule.title}</td>
                  <td>{rule.description}</td>
                  <td>{rule.action_category}</td>
                  <td>{rule.effect}</td>
                </tr>

              ))}

            </tbody>

          </table>

        )}

      </div>

      {/* GUIDED PROMPTS */}

      {showGuided && (

        <div className="guided-panel">

          {guidedPrompts.map((text, index) => (

            <div
              key={index}
              className="guided-item"
              onClick={() => selectGuidedPrompt(text)}
            >
              {text}
            </div>

          ))}

        </div>

      )}

      {/* INPUT */}

      <div className="prompt-container">

        <div className="input-wrapper">

          <input
            type="text"
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          <button
            className="guided-button"
            onClick={() => setShowGuided(!showGuided)}
          >
            ✨
          </button>

        </div>

        <button
          className="send-button"
          onClick={handleSubmit}
          disabled={!prompt.trim()}
        >
          Submit
        </button>

      </div>

    </div>
  );
}

export default PromptPanel;