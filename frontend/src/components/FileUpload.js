import React, { useState, useRef } from "react";
import { uploadFile, checkCompliance } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Upload, AlertCircle } from "lucide-react";

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
    <Card className="border-l-4 border-l-primary-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-primary-600" />
          <CardTitle className="text-base">Upload File</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-blue-700 font-medium">
            Supported: <strong>.pdf</strong> and <strong>.py</strong> files
          </p>
        </div>

        <div className="relative">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.py"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="flex items-center justify-center w-full px-4 py-6 border-2 border-dashed border-primary-300 rounded-lg cursor-pointer hover:bg-primary-50 transition-colors"
          >
            <div className="text-center">
              <Upload className="h-6 w-6 text-primary-500 mx-auto mb-2" />
              <p className="text-sm font-medium text-slate-700">
                {file ? file.name : "Click to select file"}
              </p>
              <p className="text-xs text-slate-500 mt-1">or drag and drop</p>
            </div>
          </label>
        </div>

        <Button
          onClick={handleUpload}
          disabled={!file}
          className="w-full"
        >
          Upload File
        </Button>
      </CardContent>
    </Card>
  );
}

export default FileUpload;