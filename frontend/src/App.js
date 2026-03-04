import React, { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-primary-50">
      {/* NAVBAR */}
      <Navbar />

      <div className="flex h-[calc(100vh-64px)]">
        {/* SIDEBAR */}
        <div className="w-80 border-r border-slate-200 bg-white overflow-y-auto p-6 space-y-6 shadow-sm">

          <ModelSelector />

          <FileUpload refreshDocs={loadDocuments} />

          <DocumentList
            documents={documents}
            selectedDoc={selectedDoc}
            setSelectedDoc={setSelectedDoc}
          />

        </div>

        {/* MAIN CONTENT */}
        <div className="flex-1 overflow-hidden bg-white">
          <PromptPanel selectedDoc={selectedDoc} />
        </div>

      </div>

    </div>
  );
}

export default App;