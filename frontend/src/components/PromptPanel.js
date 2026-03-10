import React, { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "./ui/table";
import { Sparkles, Send, Loader } from "lucide-react";

function PromptPanel({ selectedDoc, documents }) {

  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [showGuided, setShowGuided] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const guidedPrompts = [
    "Generate governance rules from the selected contract",
    "Extract enforceable business policies from the contract",
    "Check the uploaded python file for violations of the governance rules",
    "Analyze the Python file for any operations that violate the contract's data governance policies"
  ];

  const selectGuidedPrompt = (text) => {
    setPrompt(text);
    setShowGuided(false);
    inputRef.current?.focus();
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);



  // ===============================
  // STREAM RESPONSE HANDLER
  // ===============================

  const streamResponse = async (url, body = null) => {

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: body ? JSON.stringify(body) : null
    });

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
              updated[updated.length - 1] = {
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
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: "✔ Safe to execute the file"
                };
              } else {
                updated[updated.length - 1] = {
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
            updated[updated.length - 1] = {
              role: "assistant",
              content: line
            };
            return updated;
          });

        }

      }

    }

  };



  // ===============================
  // SUBMIT HANDLER
  // ===============================

  const handleSubmit = async () => {

    if (!prompt.trim()) return;

    const selectedDocs = Array.isArray(selectedDoc) ? selectedDoc : [];

    if (selectedDocs.length === 0) {
      alert("Please select a contract PDF.");
      return;
    }

    const selectedDocuments = documents.filter(doc =>
      selectedDocs.includes(doc.id)
    );

    const pdfFiles = selectedDocuments.filter(doc =>
      doc.filename.endsWith(".pdf")
    );

    const pyFiles = selectedDocuments.filter(doc =>
      doc.filename.endsWith(".py")
    );

    setChatStarted(true);

    const fileLabel = selectedDocuments.map(d => d.filename).join(" + ");

    const userMessage = {
      role: "user",
      content: prompt,
      file: fileLabel
    };

    setMessages(prev => [...prev, userMessage]);

    setPrompt("");
    setIsLoading(true);

    setMessages(prev => [
      ...prev,
      { role: "assistant", content: "" }
    ]);

    try {

      // ==========================
      // CASE 1 → GENERATE RULES
      // ==========================

      if (pdfFiles.length === 1 && pyFiles.length === 0) {

        const contractId = pdfFiles[0].id;

        await streamResponse(
          `http://localhost:8001/generate_rules/${contractId}`
        );

      }

      // ==========================
      // CASE 2 → CHECK COMPLIANCE
      // ==========================

      else if (pdfFiles.length === 1 && pyFiles.length === 1) {

        const contractId = pdfFiles[0].id;
        const pythonId = pyFiles[0].id;

        await streamResponse(
          "http://localhost:8001/check_compliance",
          {
            contract_id: contractId,
            python_id: pythonId
          }
        );

      }

      // ==========================
      // INVALID CASE
      // ==========================

      else {

        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content:
              "Please select exactly:\n• One PDF to generate rules\n• One PDF + one Python file to check compliance"
          };
          return updated;
        });

      }

    } catch (error) {

      console.error(error);

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Error processing request"
        };
        return updated;
      });

    } finally {

      setIsLoading(false);

    }

  };



  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 via-white to-primary-50">

      {/* CHAT AREA */}

      <Card className="flex-1 border-r border-primary-100 bg-primary-100 overflow-hidden flex flex-col">

        <CardContent className="flex-1 p-6 overflow-y-auto space-y-6">

          {!chatStarted && (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-4">
              <Sparkles className="h-12 w-12 text-primary-300" />
              <p>
                Select one contract PDF or one PDF + one Python file, then enter a prompt
              </p>
            </div>
          )}

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`max-w-3xl rounded-xl p-4 shadow-sm ${
                msg.role === "user"
                  ? "ml-auto bg-primary-500 text-white shadow-md"
                  : "bg-white border border-slate-200 text-slate-900 shadow-sm"
              }`}
            >

              {msg.role === "user" && msg.file && (
                <div className="inline-flex items-center gap-2 px-2 py-1 mb-2 rounded bg-primary-50 border border-primary-200 text-primary-700 text-xs">
                  📄 {msg.file}
                </div>
              )}

              {!msg.type && <p className="leading-relaxed">{msg.content}</p>}

              {msg.type === "rules" && (
                <Table className="mt-2">
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
                        <TableCell>{rule.description}</TableCell>
                        <TableCell>{rule.action_category}</TableCell>
                        <TableCell>{rule.effect}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}

              {msg.type === "violations" && (
                <Table className="mt-2">
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
            </div>
          )}

          <div ref={bottomRef}></div>

        </CardContent>

      </Card>



      {/* GUIDED PROMPTS */}

      {showGuided && (
        <Card className="shadow-lg border-l-4 border-l-primary-400">
          <CardContent className="p-4">
            <p className="text-sm font-semibold mb-3">Suggested Prompts</p>

            <div className="grid gap-2">
              {guidedPrompts.map((text, index) => (
                <button
                  key={index}
                  onClick={() => selectGuidedPrompt(text)}
                  className="p-3 text-left text-sm bg-primary-50 hover:bg-primary-100 border border-primary-100 rounded-lg"
                >
                  {text}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}



      {/* PROMPT INPUT */}

      <Card className="shadow-lg border-0">

        <CardContent className="p-4">

          <div className="flex gap-2 items-center">

            <Input
              ref={inputRef}
              placeholder="Enter your prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSubmit();
              }}
              disabled={isLoading}
            />

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowGuided(!showGuided)}
            >
              <Sparkles className="h-4 w-4" />
            </Button>

            <Button
              size="icon"
              onClick={handleSubmit}
              disabled={!prompt.trim() || isLoading}
            >
              {isLoading ? (
                <Loader className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>

          </div>

        </CardContent>

      </Card>

    </div>
  );
}

export default PromptPanel;