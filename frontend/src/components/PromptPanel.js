import React, { useState, useEffect } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Sparkles, Send, Loader } from "lucide-react";

function PromptPanel({ selectedDoc }) {

  const [prompt, setPrompt] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [rules, setRules] = useState([]);
  const [violations, setViolations] = useState([]);
  const [showGuided, setShowGuided] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState(null);

  const guidedPrompts = [
    "Generate governance rules from the selected contract",
    "Extract enforceable business policies from the contract",
    "Check the uploaded python file for violations of the governance rules",
    "Analyze the Python file for any operations that violate the contract's data governance policies"
  ];

  const selectGuidedPrompt = (text) => {
    setPrompt(text);
    setShowGuided(false);
  };


  useEffect(() => {

    if (!selectedDoc) return;

    const fetchDocType = async () => {

      try {

        const response = await fetch("http://localhost:8001/documents");
        const docs = await response.json();

        const doc = docs.find(d => d.id === selectedDoc);

        if (doc) {

          if (doc.filename.endsWith(".pdf")) {
            setSelectedDocType("pdf");
          }
          else if (doc.filename.endsWith(".py")) {
            setSelectedDocType("python");
          }

        }

      } catch (err) {

        console.error("Failed to detect document type", err);

      }

    };

    fetchDocType();

  }, [selectedDoc]);


  const handleSubmit = async () => {

  if (!selectedDoc) {
    alert("Please select a document first");
    return;
  }

  setPrompt("");
  setRules([]);
  setIsLoading(true);

  try {

    let endpoint = "";

    if (selectedDocType === "pdf") {
      endpoint = `http://localhost:8001/generate_rules/${selectedDoc}`;
      setStatusMessage("Parsing PDF...");
    } 
    else if (selectedDocType === "python") {
      endpoint = `http://localhost:8001/check_compliance/${selectedDoc}`;
      setStatusMessage("Preparing Python file...");
    }

    const response = await fetch(endpoint, { method: "POST" });

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
          if (parsed.type === "violations"){
            if (parsed.violations.length === 0){
              setStatusMessage("✔ Safe to execute the file")
            }
            else{
              setViolations(parsed.violations)
              setStatusMessage("")
            }
          }

        } else {

          setStatusMessage(line);

        }

      });

    }

  } catch (error) {

    console.error(error);
    setStatusMessage("Error processing document");

  } finally {

    setIsLoading(false);

  }

};


  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-primary-50 p-6 gap-4">

      <Card className="flex-1 overflow-hidden shadow-lg border-l-4 border-l-primary-500">
        <CardContent className="h-full p-6 overflow-auto">

          {rules.length === 0 && violations.length === 0 && statusMessage && (
            <div className="flex flex-col items-center justify-center h-full gap-4">

              {isLoading && (
                <Loader className="h-8 w-8 text-primary-600 animate-spin" />
              )}

              <p className="text-lg font-medium text-slate-700">{statusMessage}</p>

            </div>
          )}

          {rules.length === 0 && violations.length === 0 && (
  <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">

    <Sparkles className="h-12 w-12 text-primary-300" />

    <p className="text-center">
      {selectedDoc
        ? "Select a guided prompt or enter a custom prompt"
        : "Select a document to get started"}
    </p>

  </div>
)}

          {rules.length > 0 && (
            <div className="space-y-4">

              <h3 className="text-lg font-semibold text-slate-800">
                Generated Rules
              </h3>

              <div className="border border-slate-200 rounded-lg overflow-hidden">

                <Table>

                  <TableHeader>

                    <TableRow className="bg-slate-100">

                      <TableHead>Rule ID</TableHead>
                      <TableHead>Title</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Effect</TableHead>

                    </TableRow>

                  </TableHeader>

                  <TableBody>

                    {rules.map((rule, index) => (

                      <TableRow key={index} className="hover:bg-primary-50">

                        <TableCell className="font-mono text-primary-600">
                          {rule.rule_id}
                        </TableCell>

                        <TableCell>
                          {rule.title}
                        </TableCell>

                        <TableCell className="max-w-xs whitespace-normal break-words">
                          {rule.description}
                        </TableCell>

                        <TableCell>
                          <span className="px-3 py-1 rounded-full text-xs bg-primary-100 text-primary-700 whitespace-nowrap">
                            {rule.action_category}
                          </span>
                        </TableCell>

                        <TableCell>
                          <span className={`px-3 py-1 rounded-full text-xs ${
                            rule.effect === "Allow"
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          }`}>
                            {rule.effect}
                          </span>
                        </TableCell>

                      </TableRow>

                    ))}

                  </TableBody>

                </Table>

              </div>

            </div>
          )}

          {violations.length > 0 && (

            <div className="space-y-4">

              <h3 className="text-lg font-semibold text-red-700">
                Compliance Violations
              </h3>

              <Table>

                <TableHeader>
                  <TableRow>
                    <TableHead>Function</TableHead>
                    <TableHead>Rule ID</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Reason</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>

          {violations.map((v, index) => (

              <TableRow key={index}>

              <TableCell>{v.function}</TableCell>
              <TableCell>{v.rule_id}</TableCell>
              <TableCell>{v.title}</TableCell>
              <TableCell>{v.reason}</TableCell>

            </TableRow>

          ))}

        </TableBody>

      </Table>

    </div>

    )}

        </CardContent>
      </Card>


      {showGuided && (
        <Card className="shadow-lg border-l-4 border-l-primary-500">

          <CardContent className="p-4">

            <p className="text-sm font-semibold text-slate-600 mb-3">
              Suggested Prompts
            </p>

            <div className="grid gap-2">

              {guidedPrompts.map((text, index) => (

                <button
                  key={index}
                  onClick={() => selectGuidedPrompt(text)}
                  className="p-3 text-left text-sm bg-slate-50 hover:bg-primary-100 border rounded"
                >
                {text}
                </button>

              ))}

            </div>

          </CardContent>

        </Card>
      )}


      <Card className="shadow-lg border-l-4 border-l-primary-500">

        <CardContent className="p-4">

          <div className="flex gap-2 items-center">

            <div className="flex-1 relative">

              <Input
                type="text"
                placeholder="Enter your prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isLoading}
                className="pr-20"
              />

              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowGuided(!showGuided)}
                  disabled={isLoading}
                >
                  <Sparkles className="h-4 w-4" />
                </Button>

                <Button
                  size="icon"
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || isLoading || !selectedDoc}
                >
                  {isLoading
                    ? <Loader className="h-4 w-4 animate-spin" />
                    : <Send className="h-4 w-4" />}
                </Button>

              </div>

            </div>

          </div>

        </CardContent>

      </Card>

    </div>
  );
}

export default PromptPanel;