import React, { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import ModelSelector from "./components/ModelSelector";
import FileUpload from "./components/FileUpload";
import DocumentList from "./components/DocumentList";
import PromptPanel from "./components/PromptPanel";

import { getDocuments } from "./services/api";

function App() {

  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState([]);

  const loadDocuments = async () => {
    const res = await getDocuments();
    setDocuments(res.data);
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="h-screen overflow-hidden bg-slate-50">

      {/* NAVBAR */}
      <Navbar />

      <div className="flex h-screen pt-16">

        {/* SIDEBAR */}
        <div className="w-80 border-r border-primary-100 bg-primary-100 overflow-y-auto p-6 space-y-6">

          <ModelSelector />

          <FileUpload refreshDocs={loadDocuments} />

          <DocumentList
            documents={documents}
            selectedDoc={selectedDoc}
            setSelectedDoc={setSelectedDoc}
          />

        </div>

        {/* MAIN CONTENT */}
        <div className="flex-1 overflow-hidden bg-primary-700">
          <PromptPanel selectedDoc={selectedDoc} documents={documents} />
        </div>

      </div>

    </div>
  );
}

export default App;