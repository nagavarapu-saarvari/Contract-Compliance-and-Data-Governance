import React, { useState, useRef } from "react";
import { uploadFile } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Upload, AlertCircle } from "lucide-react";

function FileUpload({ refreshDocs }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  const clearFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const uploadSelectedFile = async (selectedFile) => {
    try {
      const fileName = selectedFile.name.toLowerCase();

      if (!fileName.endsWith(".pdf") && !fileName.endsWith(".py")) {
        alert("Unsupported file type. Please upload a PDF or .py file.");
        return;
      }

      await uploadFile(selectedFile);

      alert("File uploaded successfully");

      clearFile();
    } catch (error) {
      if (error.response && error.response.data) {
        alert(error.response.data.detail);
      } else {
        alert("File upload failed");
      }
    }
    finally { clearFile(); }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      await uploadFile(file);

      alert("File uploaded successfully");

      refreshDocs();
    } catch (error) {
      if (error.response && error.response.data) {
        alert(error.response.data.detail);
      } else {
        alert("File upload failed");
      }
    }
    finally { clearFile(); }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);

    const droppedFile = e.dataTransfer.files[0];

    if (!droppedFile) return;

    const fileName = droppedFile.name.toLowerCase();

    if (!fileName.endsWith(".pdf") && !fileName.endsWith(".py")) {
      alert("Unsupported file type. Please upload a PDF or .py file.");
      return;
    }

    setFile(droppedFile);
  };

  return (
    <Card className="border-l-4 border-l-primary-400">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-primary-400" />
          <CardTitle className="text-base">Upload File</CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">

        {/* Supported file types */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg px-3 py-2 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-primary-700 font-medium">
            Supported: <strong>.pdf</strong> and <strong>.py</strong> files
          </p>
        </div>

        {/* File Picker / Drag Drop */}
        <div className="relative">

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.py"
            onChange={(e) => {
              const selected = e.target.files[0];

              if (selected) {
                setFile(selected);
                uploadSelectedFile(selected); // auto upload
              }
            }}
            className="hidden"
            id="file-input"
          />

          <label
            htmlFor="file-input"
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`flex items-center justify-center w-full px-4 py-6 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-200
              ${
                dragging
                  ? "border-primary-400 bg-primary-50"
                  : "border-primary-300 hover:bg-primary-50"
              }`}
          >
            <div className="text-center">
              <Upload className="h-6 w-6 text-primary-400 mx-auto mb-2" />

              <p className="text-sm font-medium text-slate-700">
                {file ? file.name : "Click to select file"}
              </p>

              <p className="text-xs text-slate-500 mt-1">
                or drag and drop
              </p>
            </div>
          </label>
        </div>

        {/* Upload Button (for drag-drop files) */}
        <Button
          onClick={handleUpload}
          disabled={!file}
          className="w-full bg-primary-400 hover:bg-primary-500 text-white"
        >
          Upload File
        </Button>

      </CardContent>
    </Card>
  );
}

export default FileUpload;