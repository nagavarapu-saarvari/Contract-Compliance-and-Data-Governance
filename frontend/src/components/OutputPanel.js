import React from "react";

function OutputPanel({ output }) {

  return (
    <div className="output">

      <h3>Output</h3>

      <pre>{output}</pre>

    </div>
  );
}

export default OutputPanel;