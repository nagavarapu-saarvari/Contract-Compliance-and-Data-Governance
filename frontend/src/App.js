import React, { useEffect, useState } from "react";

import ModelSelector from "./components/ModelSelector";
import FileUpload from "./components/FileUpload";
import DocumentList from "./components/DocumentList";
import PromptPanel from "./components/PromptPanel";

import { getDocuments } from "./services/api";

function App() {

  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);

  const loadDocuments = async () => {
    const res = await getDocuments();
    setDocuments(res.data);
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="container">

      {/* LOGO SECTION */}
      <div className="top-bar">
        <img
          src="/logo.png"
          alt="Logo"
          className="logo"
        />
      </div>

      <div className="layout">

        <div className="sidebar">

          <ModelSelector />

          <FileUpload refreshDocs={loadDocuments} />

          <DocumentList
            documents={documents}
            selectedDoc={selectedDoc}
            setSelectedDoc={setSelectedDoc}
          />

        </div>

        <PromptPanel selectedDoc={selectedDoc} />

      </div>

    </div>
  );
}

export default App;