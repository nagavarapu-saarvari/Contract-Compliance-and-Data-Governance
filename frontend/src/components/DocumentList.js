import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { FileText } from "lucide-react";

function DocumentList({ documents, selectedDoc, setSelectedDoc }) {

  return (
    <Card className="border-l-4 border-l-primary-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary-600" />
          <CardTitle className="text-base">Uploaded Documents</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {documents.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-4">
            No documents uploaded yet
          </p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {documents.map((doc) => (
              <label
                key={doc.id}
                className="flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all hover:bg-primary-50"
                style={{
                  borderColor: selectedDoc === doc.id ? "#0891b2" : "#e2e8f0",
                  backgroundColor: selectedDoc === doc.id ? "#f0f9fa" : "transparent"
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedDoc === doc.id}
                  onChange={() => setSelectedDoc(selectedDoc === doc.id ? null : doc.id)}
                  className="w-4 h-4 text-primary-600 cursor-pointer"
                />
                <span className="text-sm font-medium text-slate-700 flex-1 truncate">
                  {doc.filename}
                </span>
              </label>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default DocumentList;