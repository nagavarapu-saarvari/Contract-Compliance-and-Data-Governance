import React, { useState, useRef } from "react";
import { uploadFile, checkCompliance } from "../services/api";

function FileUpload({ refreshDocs }) {

  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const clearFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleUpload = async () => {

    if (!file) return;

    const fileName = file.name.toLowerCase();

    try {

      if (fileName.endsWith(".pdf")) {

        await uploadFile(file);
        alert("PDF uploaded successfully");
        refreshDocs();
        clearFile();

      }

      else if (fileName.endsWith(".py")) {

        await checkCompliance(file);
        clearFile();

      }

      else {

        alert("Unsupported file type. Please upload a PDF or .py file.");
        clearFile();

      }

    } catch (error) {

      console.error(error);
      alert("Error processing file");
      clearFile();

    }

  };

  return (
    <div className="card">

      <h3>Upload File</h3>

      <p className="file-info">
        Supported files: <strong>.pdf</strong> and <strong>.py</strong>
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.py"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        disabled={!file}
      >
        Upload
      </button>

    </div>
  );
}

export default FileUpload;