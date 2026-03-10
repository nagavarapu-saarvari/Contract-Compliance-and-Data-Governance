import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { FileText } from "lucide-react";

function DocumentList({ documents, selectedDoc, setSelectedDoc }) {

  // Ensure selectedDoc is always an array
  const selectedDocs = Array.isArray(selectedDoc) ? selectedDoc : [];

  const handleSelection = (doc) => {

    const isSelected = selectedDocs.includes(doc.id);

    if (isSelected) {
      setSelectedDoc(selectedDocs.filter(id => id !== doc.id));
      return;
    }

    // Limit selection to 2
    if (selectedDocs.length >= 2) {
      alert("You can only select one PDF contract and one Python file.");
      return;
    }

    const currentDocs = documents.filter(d => selectedDocs.includes(d.id));

    const hasPDF = currentDocs.some(d => d.filename.endsWith(".pdf"));
    const hasPY = currentDocs.some(d => d.filename.endsWith(".py"));

    if (doc.filename.endsWith(".pdf") && hasPDF) {
      alert("Only one contract PDF can be selected.");
      return;
    }

    if (doc.filename.endsWith(".py") && hasPY) {
      alert("Only one Python file can be selected.");
      return;
    }

    setSelectedDoc([...selectedDocs, doc.id]);
  };


  return (
    <Card className="border-l-4 border-l-primary-400">

      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary-400" />
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

            {documents.map((doc) => {

              const isSelected = selectedDocs.includes(doc.id);

              return (
                <label
                  key={doc.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all
                  ${
                    isSelected
                      ? "border-primary-400 bg-primary-50"
                      : "border-slate-200 hover:bg-primary-50"
                  }`}
                >

                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleSelection(doc)}
                    className="w-4 h-4 text-primary-400 cursor-pointer"
                  />

                  <span className="text-sm font-medium text-slate-700 flex-1 truncate">
                    {doc.filename}
                  </span>

                </label>
              );

            })}

          </div>

        )}

      </CardContent>

    </Card>
  );
}

export default DocumentList;