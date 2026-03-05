import React, { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Sparkles, Send, Loader } from "lucide-react";

function PromptPanel({ selectedDoc }) {

  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [showGuided, setShowGuided] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState(null);
  const [chatStarted, setChatStarted] = useState(false);

  const bottomRef = useRef(null);

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
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

    if (!prompt.trim()) return;

    setChatStarted(true);

    const userMessage = { role: "user", content: prompt };

    setMessages(prev => [...prev, userMessage]);

    setPrompt("");
    setIsLoading(true);

    let assistantIndex;

    setMessages(prev => {
      assistantIndex = prev.length;
      return [
        ...prev,
        { role: "assistant", content: "Processing..." }
      ];
    });

    try {

      let endpoint = "";

      if (selectedDocType === "pdf") {
        endpoint = `http://localhost:8001/generate_rules/${selectedDoc}`;
      }
      else if (selectedDocType === "python") {
        endpoint = `http://localhost:8001/check_compliance/${selectedDoc}`;
      }

      const response = await fetch(endpoint, { method: "POST" });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {

        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {

          if (!line.trim()) continue;

          if (line.startsWith("{")) {

            const parsed = JSON.parse(line);

            if (parsed.type === "rules") {

              setMessages(prev => {
                const updated = [...prev];
                updated[assistantIndex] = {
                  role: "assistant",
                  type: "rules",
                  data: parsed.rules
                };
                return updated;
              });

            }

            if (parsed.type === "violations") {

              setMessages(prev => {
                const updated = [...prev];

                if (parsed.violations.length === 0) {

                  updated[assistantIndex] = {
                    role: "assistant",
                    content: "✔ Safe to execute the file"
                  };

                } else {

                  updated[assistantIndex] = {
                    role: "assistant",
                    type: "violations",
                    data: parsed.violations
                  };

                }

                return updated;
              });

            }

          } else {

            setMessages(prev => {
              const updated = [...prev];
              updated[assistantIndex] = {
                role: "assistant",
                content: line
              };
              return updated;
            });

          }

        }

      }

    } catch (error) {

      console.error(error);

      setMessages(prev => {
        const updated = [...prev];
        updated[assistantIndex] = {
          role: "assistant",
          content: "Error processing document"
        };
        return updated;
      });

    } finally {

      setIsLoading(false);

    }

  };


  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-primary-50 p-6 gap-4">

      <Card className="flex-1 overflow-hidden shadow-lg border-l-4 border-l-primary-500">
        <CardContent className="h-full p-6 overflow-auto">

          {!chatStarted && (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">

              <Sparkles className="h-12 w-12 text-primary-300" />

              <p className="text-center">
                {selectedDoc
                  ? "Select a guided prompt or enter a custom prompt"
                  : "Select a document to get started"}
              </p>

            </div>
          )}

          {chatStarted && (

            <div className="flex flex-col gap-6">

              {messages.map((msg, index) => (

                <div
                  key={index}
                  className={`max-w-3xl rounded-lg p-4 ${
                    msg.role === "user"
                      ? "ml-auto bg-primary-500 text-white"
                      : "bg-slate-100 text-slate-800"
                  }`}
                >

                  {!msg.type && <p>{msg.content}</p>}

                  {msg.type === "rules" && (

                    <Table>

                      <TableHeader>
                        <TableRow>
                          <TableHead>Rule ID</TableHead>
                          <TableHead>Title</TableHead>
                          <TableHead>Description</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Effect</TableHead>
                        </TableRow>
                      </TableHeader>

                      <TableBody>

                        {msg.data.map((rule, i) => (

                          <TableRow key={i}>

                            <TableCell>{rule.rule_id}</TableCell>
                            <TableCell>{rule.title}</TableCell>
                            <TableCell className="whitespace-normal break-words">
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

                  )}

                  {msg.type === "violations" && (

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

                        {msg.data.map((v, i) => (

                          <TableRow key={i}>
                            <TableCell>{v.function}</TableCell>
                            <TableCell>{v.rule_id}</TableCell>
                            <TableCell>{v.title}</TableCell>
                            <TableCell>{v.reason}</TableCell>
                          </TableRow>

                        ))}

                      </TableBody>

                    </Table>

                  )}

                </div>

              ))}

              {isLoading && (
                <div className="flex items-center gap-2 text-slate-500">
                  <Loader className="h-5 w-5 animate-spin" />
                  Processing...
                </div>
              )}

              <div ref={bottomRef}></div>

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
                onKeyDown={(e) => {
                  if (e.key === "Enter" && prompt.trim() && !isLoading) {
                    handleSubmit();
                  }
                }}
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